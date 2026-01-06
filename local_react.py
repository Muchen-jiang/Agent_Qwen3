"""
模块名称: qwen_local_react_agent.py
功能描述: 基于 LangGraph 的本地化 Qwen ReAct 智能体 (集成双向兼容性修复)

主要功能:
    本脚本实现了一个生产级可用的 ReAct (Reason+Act) 智能体，专为本地部署的 
    HuggingFace 模型（如 Qwen-4B/7B/14B）设计。它通过自定义中间件（Middleware）
    解决了 LangChain 严格协议与开源模型灵活输出之间的核心冲突。

核心组件与修复机制:
    1. **模型加载**: 使用 `transformers` 和 `pipeline` 加载本地 Qwen 模型，并封装为 LangChain `ChatHuggingFace`。
    
    2. **输入端中间件 (`format_input_for_qwen`)**:
       - **问题**: LangChain 严格要求对话必须以 HumanMessage 结尾，且不识别 ToolMessage 角色，导致 ReAct 循环中断。
       - **方案**: 拦截所有 `ToolMessage`，将其伪装成带有 "Observation:" 前缀的 `HumanMessage`。这不仅绕过了类型检查，还符合模型训练时的 ReAct Prompt 范式。

    3. **输出端中间件 (`parse_qwen_response`)**:
       - **问题**: Qwen 模型倾向于先输出 `<think>` 思考过程，这会干扰标准 XML 解析器，导致工具调用失败。
       - **方案**: 使用正则表达式绕过思考标签，精准提取 `<tool_call>` 中的 JSON 数据，并重构为标准的 `AIMessage`。

    4. **智能体编排**: 使用 `langgraph.prebuilt.create_react_agent` 构建图运行环境，支持流式输出 (Streaming) 和多步推理。

适用场景:
    - 在本地显卡上运行开源 LLM 并进行工具调用 (Function Calling)。
    - 学习和调试 LangChain 的底层消息流转机制。
    - 解决 "Last message must be a HumanMessage" 和 XML 解析错误的通用方案。
"""
import os
import torch
import warnings
from typing import List, Literal

# --- LangChain & LangGraph Imports ---
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
# 根据文档，Agent 是基于 Graph 构建的
from langgraph.prebuilt import create_react_agent

import re
import json
import uuid
from langchain_core.messages import AIMessage
# 屏蔽一些烦人的警告
warnings.filterwarnings("ignore")

# ==========================================
# 1. 配置路径
# ==========================================
# ⚠️ 请确认路径正确，Qwen2.5 或 Qwen2 通常效果更好
MODEL_PATH = "/home/jmc/llm/Qwen3-4B" 

# ==========================================
# 2. 加载模型 (Local LLM via HuggingFace)
# ==========================================
print(f"🔄 正在加载模型: {MODEL_PATH} ...")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    exit()

# 创建 Pipeline
text_pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=2048,
    return_full_text=False, # LangChain 会处理历史记录，不需要 Pipeline 重复返回
    temperature=0.1,        # 低温有助于工具调用的格式稳定
    do_sample=True 
)

# 包装为 Chat Model
# ChatHuggingFace 负责把 System Prompt 和 Tools 塞进 Query
llm = HuggingFacePipeline(pipeline=text_pipe)
chat_model = ChatHuggingFace(llm=llm)

print("✅ 模型加载完成。")

# ==========================================
# 3. 定义工具 (Tools)
# ==========================================

@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的天气状况。
    Args:
        city: 城市名称（如 '北京', '上海'）。
    """
    # 模拟 API 调用
    if "北京" in city:
        return "北京今天晴朗，气温 25 度，适合出行。"
    elif "上海" in city:
        return "上海今天有小雨，气温 20 度。"
    else:
        return f"暂无 {city} 的天气数据。"

@tool
def magic_calculation(a: int, b: int) -> int:
    """
    计算两个数字的神秘加法。
    Args:
        a: 第一个数字
        b: 第二个数字
    """
    return a + b

tools = [get_weather, magic_calculation]

# ==========================================
# 4. 【上帝视角】Prompt 检查器 (调试用)
# ==========================================
def inspect_raw_prompt(inputs: dict):
    """
    接收 LangGraph 的 inputs 字典，解析其中的 messages，
    并展示最终送给模型的真实 Prompt。
    """
    print("\n" + "="*60)
    print("🕵️  【上帝视角】真实 Prompt 预览")
    print("="*60)
    
    # 1. 提取 LangChain 消息对象列表
    lc_messages = inputs.get("messages", [])
    
    # 2. 将 LangChain 消息转换为 HuggingFace Tokenizer 所需的字典格式
    hf_messages = []
    for msg in lc_messages:
        role = "user"
        if isinstance(msg, SystemMessage):
            role = "system"
        elif isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, ToolMessage):
            role = "tool"
        # 注意：这里暂未处理 AIMessage，因为初始输入通常不包含 AI 回复
        
        hf_messages.append({"role": role, "content": msg.content})

    # 3. 获取工具定义 (Tool Schema)
    # 依然需要从 chat_model 中获取，因为这是绑定在模型上的
    llm_with_tools = chat_model.bind_tools(tools)
    tool_schemas = llm_with_tools.kwargs.get("tools", [])

    try:
        # 4. 使用 Tokenizer 渲染
        final_prompt = tokenizer.apply_chat_template(
            hf_messages,           # <--- 这里现在使用的是转换后的真实消息
            tools=tool_schemas,    # 注入工具
            add_generation_prompt=True,
            tokenize=False
        )
        print(final_prompt)
    except Exception as e:
        print(f"❌ 渲染失败: {e}")
        # 如果渲染失败，打印原始消息列表帮助调试
        print("原始消息列表:", hf_messages)
        
    print("="*60 + "\n")

# ==========================================
# 5.1 【输出端修复】自定义解析器 (处理 <think>)
# ==========================================
def parse_qwen_response(ai_message: AIMessage) -> AIMessage:
    """
    清洗模型输出：提取 <tool_call>，忽略 <think>
    """
    content = ai_message.content
    if ai_message.tool_calls:
        return ai_message

    pattern = r"<tool_call>(.*?)</tool_call>"
    matches = re.findall(pattern, content, re.DOTALL)
    extracted_tool_calls = []
    
    for match in matches:
        try:
            json_str = match.strip()
            tool_data = json.loads(json_str)
            extracted_tool_calls.append({
                "name": tool_data["name"],
                "args": tool_data["arguments"],
                "id": f"call_{uuid.uuid4().hex[:8]}"
            })
        except Exception as e:
            pass

    if extracted_tool_calls:
        return AIMessage(content=content, tool_calls=extracted_tool_calls)
    return ai_message

# ==========================================
# 5.2 【输入端修复】输入格式化器 (全局清洗版)
# ==========================================
def format_input_for_qwen(input_data):
    """
    中间件核心功能：
    1. 提取消息列表。
    2. 【关键】遍历所有消息，将 'ToolMessage' 彻底转换为 'HumanMessage'。
       这是因为 langchain_huggingface 库目前不识别 ToolMessage 类型，会导致崩溃。
    """
    # 1. 解包 input_data
    if isinstance(input_data, dict) and "messages" in input_data:
        original_messages = list(input_data["messages"])
    elif isinstance(input_data, list):
        original_messages = list(input_data)
    else:
        original_messages = [input_data]

    new_messages = []
    
    # 2. 遍历并转换
    for msg in original_messages:
        if isinstance(msg, ToolMessage):
            # print(f"🕵️ [Middleware] 捕获 ToolMessage (ID: {msg.tool_call_id})，正在清洗...")
            
            # 将工具结果伪装成用户的“观察报告”
            # 格式：Observation: <Result>
            new_content = f"Observation: {msg.content}"
            
            # 替换为 HumanMessage
            new_messages.append(HumanMessage(content=new_content))
        else:
            # 其他消息保持不变
            new_messages.append(msg)
    
    return new_messages
# ==========================================
# 6. 运行 Agent (最终版)
# ==========================================

def run_agent(query: str):
    print("🤖 正在构建 LangGraph Agent (双向修复版)...")
    
    # 1. 绑定工具
    llm_with_tools = chat_model.bind_tools(tools)
    
    # 2. 【构建核心链】 Input格式化 -> 模型 -> Output解析
    # 这里的 RunnableLambda 负责执行我们的 format_input_for_qwen 函数
    model_chain = (
        RunnableLambda(format_input_for_qwen) 
        | llm_with_tools 
        | parse_qwen_response
    )

    # 3. 创建 Agent
    agent_graph = create_react_agent(
        model=model_chain, 
        tools=tools
    )

    print(f"🚀 开始执行对话: {query}\n")
    print("-" * 40)

    # 4. System Prompt
    system_prompt_content = """
    你是一个智能助手。
    在回答用户问题前，请先进行思考。
    
    【工具调用规则】
    所有的能力输出，请使用工具。如果需要使用工具，请生成 <tool_call> JSON XML。
    格式示例：
    <tool_call>{"name": "get_weather", "arguments": {"city": "北京"}}</tool_call>

    所有的计算任务必须使用 Tools 工具。

    【执行结果反馈】
    当你看到 "Observation: ..." 时，那就是工具返回的结果。请根据结果回答用户。
    """
    
    inputs = {
        "messages": [
            SystemMessage(content=system_prompt_content),
            HumanMessage(content=query)
        ]
    }
    print(inspect_raw_prompt(inputs))

    try:
        # 5. 运行图
        for event in agent_graph.stream(inputs, stream_mode="values"):
            message = event["messages"][-1]
            
            if message.type == "human":
                print(f"🗣️ [用户输入] {message.content}")

            if message.type == "ai":
                print(f"🗣️ [AI 回复] {message.content}")
                if message.tool_calls:
                    print(f"🧠 [AI 决定调用工具] ({len(message.tool_calls)} 个)")
                    for tc in message.tool_calls:
                        print(f"   --> 工具: {tc['name']}")
                        print(f"   --> 参数: {tc['args']}")
                else:
                    print(f"🗣️ [AI 最终回复] {message.content}")
            
            elif message.type == "tool":
                print(f"🔧 [工具原始结果] {message.content}")
            
            # 注意：因为我们做了输入伪装，LangGraph 内部状态还是 ToolMessage，
            # 所以这里的打印依然会显示 ToolMessage，这是对的。
                
            print("-" * 40)

    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    user_query = "你拥有帮我检查天气的能力吗？例如，今天北京今天天气怎么样？同时，你有算数的能力吗？另外帮我算一下 88 加 11 等于多少。"
    run_agent(user_query)
