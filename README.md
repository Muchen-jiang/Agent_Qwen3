# 🤖 Enhanced LangGraph Agent

基于 LangGraph 的增强型本地 AI Agent 系统，支持复杂工具调用、知识库检索、网络搜索等功能。

---

## ⚡ 快速导航

- **遇到导入错误？** → [README_FIX.md](README_FIX.md) ⚡
- **5分钟快速开始** → [QUICKSTART.md](QUICKSTART.md) 🚀
- **详细安装指南** → [INSTALL.md](INSTALL.md) 📦
- **问题排查** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 🔧
- **所有文档索引** → [DOCS_INDEX.md](DOCS_INDEX.md) 📖

---

## ✨ 核心特性

- 🧠 **强大的推理能力**: 基于 LangGraph 的 ReAct Agent 架构
- 🔧 **丰富的工具集**:
  - 🌐 网络搜索 (DuckDuckGo)
  - 📚 本地知识库 (RAG)
  - 🧮 数学计算器
  - 🌤️ 天气查询
  - ⏰ 时间获取
  - 📝 文件操作
- 💾 **对话记忆**: 支持多种记忆策略（窗口、缓冲、摘要）
- 📊 **状态管理**: 完整的 Agent 执行状态跟踪
- 🔄 **流式输出**: 实时查看 Agent 推理过程
- 🎯 **模块化设计**: 易于扩展和自定义

## 📁 项目结构

```
Agent_Qwen3/
├── config/              # 配置模块
│   ├── __init__.py
│   └── settings.py      # 所有配置项
├── tools/               # 工具模块
│   ├── __init__.py
│   ├── basic_tools.py   # 基础工具（计算器、天气等）
│   ├── search_tools.py  # 搜索工具
│   └── rag_tools.py     # RAG知识库工具
├── agent/               # Agent核心
│   ├── __init__.py
│   └── langgraph_agent.py  # 主Agent实现
├── memory/              # 记忆系统
│   ├── __init__.py
│   └── conversation_memory.py
├── utils/               # 工具函数
│   ├── __init__.py
│   ├── model_loader.py  # 模型加载器
│   └── message_processor.py  # 消息处理
├── examples/            # 示例代码
│   ├── simple_example.py
│   ├── custom_tools_example.py
│   └── rag_example.py
├── data/                # 数据目录
│   ├── rag_docs/        # 知识库文档
│   └── vector_db/       # 向量数据库
├── main.py              # 主程序入口
├── requirements.txt     # Python依赖
└── README.md           # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型路径

编辑 `config/settings.py`，设置你的模型路径：

```python
MODEL_PATH = "/path/to/your/Qwen-model"
```

或使用环境变量：

```bash
export MODEL_PATH="/path/to/your/Qwen-model"
```

### 3. 运行示例

#### 交互模式（推荐）

```bash
python main.py
# 选择 6 进入交互模式
```

#### 快速示例

```bash
python examples/simple_example.py
```

#### RAG知识库示例

```bash
python examples/rag_example.py
```

#### 自定义工具示例

```bash
python examples/custom_tools_example.py
```

## 💡 使用示例

### 基础使用

```python
from agent import EnhancedLangGraphAgent

# 创建Agent
agent = EnhancedLangGraphAgent()

# 简单对话
response = agent.chat("北京今天天气怎么样？")
print(response)

# 使用计算器
response = agent.chat("帮我计算 sqrt(144) + 100")
print(response)

# 网络搜索
response = agent.chat("搜索一下 Python 3.12 的新特性")
print(response)
```

### 高级用法 - 自定义工具

```python
from langchain_core.tools import tool
from agent import EnhancedLangGraphAgent
from tools import DEFAULT_TOOLS

# 定义自定义工具
@tool
def my_custom_tool(input_text: str) -> str:
    """
    我的自定义工具描述

    Args:
        input_text: 输入文本

    Returns:
        处理结果
    """
    return f"处理结果: {input_text.upper()}"

# 创建包含自定义工具的Agent
agent = EnhancedLangGraphAgent(
    tools=DEFAULT_TOOLS + [my_custom_tool]
)

# 使用自定义工具
response = agent.chat("使用my_custom_tool处理 'hello world'")
```

### 知识库检索

```python
from agent import EnhancedLangGraphAgent

# 1. 准备知识库文档
# 将文档放入 data/rag_docs/ 目录

# 2. 创建Agent
agent = EnhancedLangGraphAgent()

# 3. 查询知识库
response = agent.chat("什么是LangGraph？")
print(response)
```

### 多轮对话（带记忆）

```python
agent = EnhancedLangGraphAgent(
    enable_memory=True,
    memory_type="window"  # 或 "buffer", "summary"
)

# 第一轮
agent.chat("我叫张三")

# 第二轮 - Agent会记住你的名字
agent.chat("我叫什么名字？")

# 查看对话历史
print(agent.get_conversation_history())

# 清空记忆
agent.clear_memory()
```

## 🔧 配置说明

所有配置在 `config/settings.py` 中，主要配置项：

### 模型配置

```python
class ModelConfig:
    MODEL_PATH = "/path/to/model"  # 模型路径
    MAX_NEW_TOKENS = 2048          # 最大生成token数
    TEMPERATURE = 0.1              # 温度参数
    TOP_P = 0.9                    # Top-p采样
```

### RAG配置

```python
class RAGConfig:
    VECTOR_DB_TYPE = "faiss"       # 向量数据库类型
    DOCUMENTS_PATH = "data/rag_docs"  # 文档路径
    EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"  # Embedding模型
    CHUNK_SIZE = 500               # 文档分块大小
    TOP_K = 3                      # 检索top-k结果
```

### Agent配置

```python
class AgentConfig:
    MAX_ITERATIONS = 10            # 最大迭代次数
    ENABLE_STREAMING = True        # 启用流式输出
    ENABLE_MEMORY = True           # 启用记忆
    MEMORY_WINDOW_SIZE = 10        # 记忆窗口大小
```

## 📚 可用工具

### 基础工具

- **calculator**: 数学计算器，支持基本运算和常用数学函数
- **get_weather**: 天气查询（模拟数据）
- **get_current_time**: 获取当前时间
- **string_operations**: 字符串操作
- **file_operations**: 文件读写操作

### 搜索工具

- **search_web**: 网络搜索（DuckDuckGo）
- **search_news**: 新闻搜索
- **search_with_tavily**: Tavily搜索（需要API key）

### RAG工具

- **search_knowledge_base**: 检索本地知识库
- **add_documents_to_knowledge_base**: 添加文档到知识库

## 🎯 高级特性

### 1. 动态添加工具

```python
from langchain_core.tools import tool

agent = EnhancedLangGraphAgent()

@tool
def new_tool(param: str) -> str:
    """新工具"""
    return f"Result: {param}"

agent.add_tool(new_tool)
```

### 2. 自定义系统提示词

```python
custom_prompt = """
你是一个专业的技术助手...
"""

agent = EnhancedLangGraphAgent(
    system_prompt=custom_prompt
)
```

### 3. 获取执行统计

```python
result = agent.run("查询...", stream=True)

print(f"使用的工具: {result['tools_used']}")
print(f"迭代次数: {result['iterations']}")
print(f"状态摘要: {result['state_summary']}")
```

## 🔍 调试和日志

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = EnhancedLangGraphAgent(verbose=True)
```

### 查看消息处理过程

```python
from utils import inspect_messages

# 在代码中插入消息检查
inspect_messages(messages, title="调试点")
```

## 📝 添加自己的知识库

1. 在 `data/rag_docs/` 目录下放入文档（支持 .txt, .md, .pdf）
2. Agent会自动索引这些文档
3. 使用 `search_knowledge_base` 工具检索

示例：

```bash
# 添加文档
cp my_docs/*.pdf data/rag_docs/

# 使用Agent查询
python -c "
from agent import EnhancedLangGraphAgent
agent = EnhancedLangGraphAgent()
print(agent.chat('我的文档中关于XXX的内容是什么？'))
"
```

## 🛠️ 故障排除

### 问题1: 模型加载失败

```
检查模型路径是否正确
确保有足够的显存/内存
尝试降低 TORCH_DTYPE（如使用 float16）
```

### 问题2: 工具调用失败

```
检查工具描述是否清晰
降低 TEMPERATURE 以提高稳定性
查看日志中的错误信息
```

### 问题3: 搜索功能不可用

```bash
# 安装搜索依赖
pip install duckduckgo-search

# 如果网络受限，可以使用本地搜索或禁用搜索工具
```

### 问题4: RAG检索效果不佳

```
增加文档质量和数量
调整 CHUNK_SIZE 和 CHUNK_OVERLAP
尝试不同的 EMBEDDING_MODEL
调整 TOP_K 和 SCORE_THRESHOLD
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Qwen](https://github.com/QwenLM/Qwen)
- [Transformers](https://github.com/huggingface/transformers)

## 📧 联系方式

如有问题，欢迎提交 Issue。

---

**Happy Coding! 🚀**
