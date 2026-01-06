# 🏗️ 架构设计文档

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                              │
│                  (main.py, examples/)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent核心层                              │
│                 (EnhancedLangGraphAgent)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  LangGraph   │  │  Memory      │  │   State      │      │
│  │    Graph     │  │  Manager     │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   工具层      │ │   模型层      │ │  中间件层     │
│              │ │              │ │              │
│ • 搜索工具    │ │ • 模型加载    │ │ • 消息处理    │
│ • RAG工具    │ │ • Tokenizer  │ │ • 格式转换    │
│ • 基础工具    │ │ • Pipeline   │ │ • 解析器     │
└──────────────┘ └──────────────┘ └──────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
        ┌─────────────────────────────┐
        │       外部服务/资源           │
        │                             │
        │ • 向量数据库 (FAISS)         │
        │ • 搜索引擎 (DuckDuckGo)      │
        │ • 本地文档库                 │
        │ • LLM模型                   │
        └─────────────────────────────┘
```

## 核心组件

### 1. Agent核心 (agent/)

#### EnhancedLangGraphAgent

主要职责：
- 协调所有组件
- 管理Agent生命周期
- 处理用户请求
- 执行推理循环

关键方法：
```python
def run(query: str) -> Dict[str, Any]
    # 执行完整的Agent推理流程

def chat(message: str) -> str
    # 简化的对话接口

def _build_agent_graph() -> CompiledGraph
    # 构建LangGraph执行图
```

LangGraph执行流程：
```
用户输入
   ↓
系统提示词 + 历史记忆 + 当前查询
   ↓
输入格式化 (format_input_for_qwen)
   ↓
LLM推理
   ↓
输出解析 (parse_qwen_response)
   ↓
判断：需要调用工具？
   ├─ 是 → 执行工具 → 获取结果 → 回到LLM推理
   └─ 否 → 返回最终答案
```

### 2. 工具系统 (tools/)

#### 工具架构

```
tools/
├── __init__.py          # 工具注册和导出
├── basic_tools.py       # 基础工具集
├── search_tools.py      # 搜索工具集
└── rag_tools.py         # RAG工具集
```

#### 工具定义规范

```python
from langchain_core.tools import tool

@tool
def tool_name(param: type) -> return_type:
    """
    工具描述 - 这很重要，LLM会根据描述选择工具

    Args:
        param: 参数描述

    Returns:
        返回值描述
    """
    # 实现逻辑
    return result
```

#### RAG系统设计

```
RAG工作流：
1. 文档加载 → 2. 文档分块 → 3. 向量化 → 4. 存储到FAISS
                                              ↓
                    ┌─────────────────────────┘
                    ↓
用户查询 → 查询向量化 → 相似度搜索 → 返回Top-K结果
```

RAGSystem单例：
- 管理向量数据库生命周期
- 提供文档索引和检索接口
- 支持增量添加文档

### 3. 记忆系统 (memory/)

#### ConversationMemory

支持三种记忆策略：

1. **窗口记忆 (Window)**
   ```
   保留最近N轮对话
   优点：固定内存占用
   缺点：丢失早期信息
   ```

2. **缓冲记忆 (Buffer)**
   ```
   保留所有历史
   优点：完整上下文
   缺点：内存持续增长
   ```

3. **摘要记忆 (Summary)**
   ```
   定期摘要历史对话
   优点：平衡性能和上下文
   缺点：可能丢失细节
   ```

#### AgentState

追踪Agent运行时状态：
- 当前任务
- 已执行的工具
- 迭代次数
- 中间结果

### 4. 模型层 (utils/)

#### ModelLoader

单例模式的模型管理器：
```python
class ModelLoader:
    _instance = None
    _model = None
    _tokenizer = None
    _chat_model = None

    def load_model() -> ChatHuggingFace
        # 懒加载模型
        # 缓存已加载的实例
```

#### MessageProcessor

解决LangChain与开源模型的兼容性：

1. **输入端处理** (`format_input_for_qwen`)
   ```
   问题：LangChain要求以HumanMessage结尾，不识别ToolMessage
   解决：将ToolMessage转换为特殊格式的HumanMessage
   ```

2. **输出端处理** (`parse_qwen_response`)
   ```
   问题：Qwen输出包含<think>标签，干扰工具调用解析
   解决：使用正则提取<tool_call>，忽略思考内容
   ```

### 5. 配置系统 (config/)

集中式配置管理：

```python
config/settings.py
├── ModelConfig      # 模型相关配置
├── RAGConfig        # RAG相关配置
├── SearchConfig     # 搜索相关配置
├── AgentConfig      # Agent行为配置
└── LogConfig        # 日志配置
```

支持：
- 环境变量覆盖
- 类型安全
- 默认值

## 数据流

### 完整请求流程

```
1. 用户输入
   "帮我搜索Python 3.12的新特性"
   ↓
2. Agent.run()
   - 添加系统提示词
   - 加载历史记忆（如果启用）
   - 构建输入消息列表
   ↓
3. LangGraph执行
   ┌─→ format_input_for_qwen
   │   - 转换ToolMessage
   ↓
   LLM推理
   - 分析需求
   - 决定调用search_web工具
   ↓
   parse_qwen_response
   - 提取工具调用
   ↓
4. 工具执行
   search_web("Python 3.12新特性")
   - 调用DuckDuckGo API
   - 返回搜索结果
   ↓
5. 结果反馈
   ToolMessage("搜索结果...")
   │
   └─→ 回到步骤3（format_input_for_qwen）
   ↓
6. LLM总结
   - 基于搜索结果生成回答
   ↓
7. 返回用户
   "Python 3.12的新特性包括..."
```

### 消息类型转换

```
LangChain标准流程:
HumanMessage → AIMessage → ToolMessage → AIMessage

本项目适配流程:
HumanMessage → AIMessage → HumanMessage(伪装) → AIMessage
                                ↑
                    format_input_for_qwen转换
```

## 设计模式

### 1. 单例模式

- `ModelLoader`: 确保模型只加载一次
- `RAGSystem`: 管理全局向量数据库

### 2. 策略模式

- `ConversationMemory`: 支持多种记忆策略

### 3. 中间件模式

- `format_input_for_qwen`: 输入拦截和转换
- `parse_qwen_response`: 输出拦截和解析

### 4. 构建器模式

- `_build_agent_graph`: 构建复杂的LangGraph执行图

## 扩展点

### 添加新工具

1. 在 `tools/` 创建新文件或在现有文件添加
2. 使用 `@tool` 装饰器定义工具
3. 在 `tools/__init__.py` 导出
4. 添加到 `DEFAULT_TOOLS` 或 `ALL_TOOLS`

### 添加新的记忆策略

1. 在 `ConversationMemory` 添加新方法
2. 更新 `get_messages()` 支持新策略

### 自定义消息处理

1. 创建新的处理函数
2. 在 `_build_agent_graph` 中集成到处理链

### 添加新的状态管理

1. 扩展 `AgentState` 类
2. 在Agent执行过程中更新状态

## 性能优化

### 1. 模型加载

- 懒加载：只在需要时加载
- 单例缓存：避免重复加载
- 显存优化：支持 float16/int8

### 2. 向量检索

- FAISS索引：高效相似度搜索
- 批量索引：文档批量处理
- 缓存机制：持久化向量数据库

### 3. 内存管理

- 窗口记忆：限制历史长度
- 懒初始化：按需创建组件

## 安全考虑

### 1. 工具执行安全

- 计算器使用受限命名空间
- 文件操作路径验证
- 工具输入参数校验

### 2. 模型安全

- 本地部署：数据不出本地
- 访问控制：工具权限管理

### 3. 数据安全

- 环境变量：敏感配置外部化
- .gitignore：排除私密数据

## 最佳实践

### 1. 工具设计

- 单一职责：每个工具做一件事
- 清晰描述：帮助LLM正确选择
- 错误处理：返回友好的错误信息

### 2. 提示词工程

- 结构化：明确工具调用格式
- 示例驱动：提供清晰的示例
- 约束明确：说明使用规则

### 3. 状态管理

- 不可变性：避免状态污染
- 显式重置：清晰的生命周期
- 日志记录：便于调试

## 故障排查

### 日志级别

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 调试工具

- `inspect_messages()`: 查看消息流
- `verbose=True`: 显示详细执行过程
- Agent状态跟踪：查看迭代和工具使用

---

**这份文档会随着系统演进持续更新。**
