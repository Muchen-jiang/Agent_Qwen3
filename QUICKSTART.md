# 🚀 快速启动指南

## 5分钟快速上手

### 步骤 1: 安装依赖

```bash
# 克隆或进入项目目录
cd Agent_Qwen3

# 安装Python依赖
pip install -r requirements.txt
```

### 步骤 2: 配置模型路径

**方法 1: 环境变量（推荐）**

```bash
export MODEL_PATH="/home/jmc/llm/Qwen3-4B"
```

**方法 2: 编辑配置文件**

编辑 `config/settings.py`，修改第54行：

```python
MODEL_PATH: str = os.getenv(
    "MODEL_PATH",
    "/your/path/to/Qwen-model"  # 改成你的模型路径
)
```

### 步骤 3: 运行示例

```bash
# 方式1: 交互模式（推荐新手）
python main.py
# 然后选择 6 进入交互模式

# 方式2: 运行简单示例
python examples/simple_example.py

# 方式3: 尝试知识库检索
python examples/rag_example.py
```

## 📝 最小代码示例

创建一个新文件 `test.py`:

```python
from agent import EnhancedLangGraphAgent

# 创建Agent
agent = EnhancedLangGraphAgent()

# 开始对话
response = agent.chat("北京今天天气怎么样？")
print(response)
```

运行:

```bash
python test.py
```

## 🎯 常见使用场景

### 场景1: 数学计算

```python
agent = EnhancedLangGraphAgent()
agent.chat("帮我计算 sqrt(144) + 10 * 5")
```

### 场景2: 网络搜索

```python
agent = EnhancedLangGraphAgent()
agent.chat("搜索一下 Python 3.12 的新特性")
```

### 场景3: 知识库问答

```python
# 1. 将文档放入 data/rag_docs/ 目录
# 2. 查询
agent = EnhancedLangGraphAgent()
agent.chat("我的文档中关于XXX的内容是什么？")
```

### 场景4: 多轮对话

```python
agent = EnhancedLangGraphAgent(enable_memory=True)

agent.chat("我叫张三，今年25岁")
agent.chat("我叫什么名字？")  # Agent会记住之前的信息
agent.chat("我多大了？")       # Agent会记住之前的信息
```

## ⚙️ 自定义工具

```python
from langchain_core.tools import tool
from agent import EnhancedLangGraphAgent
from tools import DEFAULT_TOOLS

# 定义你的工具
@tool
def my_tool(text: str) -> str:
    """我的自定义工具"""
    return f"处理结果: {text.upper()}"

# 创建包含自定义工具的Agent
agent = EnhancedLangGraphAgent(
    tools=DEFAULT_TOOLS + [my_tool]
)

agent.chat("使用my_tool处理 'hello'")
```

## 🔧 配置选项

### 启用/禁用功能

```python
agent = EnhancedLangGraphAgent(
    enable_memory=True,      # 启用对话记忆
    memory_type="window",    # 记忆类型: window, buffer, summary
    verbose=True             # 显示详细日志
)
```

### 自定义系统提示词

```python
custom_prompt = """
你是一个专业的Python编程助手。
你需要：
1. 提供准确的代码示例
2. 解释技术概念
3. 推荐最佳实践
"""

agent = EnhancedLangGraphAgent(
    system_prompt=custom_prompt
)
```

## 📊 查看执行详情

```python
# 使用 run() 而不是 chat() 可以获取详细信息
result = agent.run("查询...", stream=True)

print(f"响应: {result['response']}")
print(f"使用的工具: {result['tools_used']}")
print(f"迭代次数: {result['iterations']}")
```

## 🐛 常见问题

### Q1: 导入错误

```bash
# 确保在项目根目录运行
cd Agent_Qwen3
python main.py
```

### Q2: 模型加载失败

```bash
# 检查模型路径
echo $MODEL_PATH

# 或查看配置
python -c "from config import model_config; print(model_config.MODEL_PATH)"
```

### Q3: 搜索功能不工作

```bash
# 安装搜索依赖
pip install duckduckgo-search
```

### Q4: 显存不足

编辑 `config/settings.py`:

```python
TORCH_DTYPE = "float16"  # 或 "int8" 以节省显存
```

## 📚 下一步

- 阅读完整 [README.md](README.md) 了解所有功能
- 查看 [examples/](examples/) 目录的更多示例
- 探索 [tools/](tools/) 目录了解如何创建工具
- 自定义 [config/settings.py](config/settings.py) 调整配置

## 💡 提示

1. **首次运行可能较慢** - 需要加载模型和初始化向量数据库
2. **使用GPU** - 确保 PyTorch 安装了 CUDA 支持以获得最佳性能
3. **查看日志** - 设置 `verbose=True` 可以看到Agent的思考过程
4. **保存对话** - 启用 `enable_memory=True` 可以进行多轮对话

---

**开始探索吧！** 🎉

有问题？查看 [README.md](README.md) 或提交 Issue。
