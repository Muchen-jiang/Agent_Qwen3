# 🔧 故障排查指南

## 快速诊断

运行以下命令进行环境检查：

```bash
# 1. 检查所有依赖
python check_env.py

# 2. 测试模块导入
python test_imports.py
```

## 常见问题及解决方案

### 1. ModuleNotFoundError: No module named 'langgraph.graph.graph'

**错误信息：**
```
ModuleNotFoundError: No module named 'langgraph.graph.graph'
```

**原因：** LangGraph API 版本不兼容

**解决方案：**

```bash
# 更新 LangGraph
pip install --upgrade langgraph>=0.2.0

# 或者重新安装
pip install -r requirements.txt --upgrade
```

**已修复：** 代码已更新使用正确的导入方式

---

### 2. 模型加载失败

**错误信息：**
```
❌ 模型加载失败: ...
```

**解决方案：**

1. **检查模型路径：**
```bash
# 设置环境变量
export MODEL_PATH="/path/to/your/Qwen-model"

# 验证路径
ls $MODEL_PATH
# 应该看到 config.json, model.safetensors 等文件
```

2. **检查模型文件完整性：**
```bash
# 确保包含这些文件
cd $MODEL_PATH
ls -lh config.json tokenizer.json *.safetensors
```

3. **显存不足：**

编辑 `config/settings.py`，降低精度：

```python
TORCH_DTYPE = "float16"  # 或 "int8"
```

或使用量化版本的模型。

---

### 3. 导入错误

**错误信息：**
```
ImportError: cannot import name 'xxx' from 'yyy'
```

**解决方案：**

```bash
# 1. 重新安装所有依赖
pip uninstall langchain langchain-core langchain-community langgraph -y
pip install -r requirements.txt

# 2. 清除 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 3. 重新测试
python test_imports.py
```

---

### 4. DuckDuckGo 搜索失败

**错误信息：**
```
错误: 缺少 duckduckgo-search 库
```

**解决方案：**

```bash
pip install duckduckgo-search>=4.0.0
```

**网络问题：**

如果网络受限，可以临时禁用搜索工具：

```python
from tools import calculator, get_weather, get_current_time

# 只使用基础工具
agent = EnhancedLangGraphAgent(
    tools=[calculator, get_weather, get_current_time]
)
```

---

### 5. RAG 向量数据库初始化失败

**错误信息：**
```
RAG系统初始化失败: ...
```

**解决方案：**

1. **安装 FAISS：**
```bash
# CPU 版本
pip install faiss-cpu

# GPU 版本（如果有CUDA）
pip install faiss-gpu
```

2. **安装 sentence-transformers：**
```bash
pip install sentence-transformers
```

3. **检查文档目录：**
```bash
# 创建目录
mkdir -p data/rag_docs data/vector_db

# 添加示例文档
echo "这是测试文档" > data/rag_docs/test.txt
```

4. **下载 Embedding 模型：**

首次运行时会自动下载，如果网络慢，可以手动下载：

```python
from sentence_transformers import SentenceTransformer

# 手动下载并缓存
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
```

---

### 6. CUDA 相关错误

**错误信息：**
```
RuntimeError: CUDA out of memory
```

**解决方案：**

1. **降低精度：**
```python
# config/settings.py
TORCH_DTYPE = "float16"  # 或 "int8"
```

2. **减少 max_new_tokens：**
```python
# config/settings.py
MAX_NEW_TOKENS = 1024  # 从 2048 降低
```

3. **使用 CPU：**
```python
# config/settings.py
DEVICE_MAP = "cpu"
```

4. **清理显存：**
```python
import torch
torch.cuda.empty_cache()
```

---

### 7. 依赖版本冲突

**错误信息：**
```
ERROR: pip's dependency resolver does not currently take into account...
```

**解决方案：**

```bash
# 创建新的虚拟环境
python -m venv venv_new
source venv_new/bin/activate  # Linux/Mac
# 或
venv_new\Scripts\activate  # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 8. 编码错误

**错误信息：**
```
UnicodeDecodeError: 'utf-8' codec can't decode...
```

**解决方案：**

确保文档使用 UTF-8 编码：

```bash
# 转换文件编码
iconv -f GBK -t UTF-8 old_file.txt > new_file.txt

# 或使用 Python
python -c "
content = open('file.txt', 'r', encoding='gbk').read()
open('file.txt', 'w', encoding='utf-8').write(content)
"
```

---

### 9. 运行速度慢

**优化建议：**

1. **使用 GPU：**
```bash
# 检查 CUDA 是否可用
python -c "import torch; print(torch.cuda.is_available())"
```

2. **减少记忆窗口：**
```python
agent = EnhancedLangGraphAgent(
    memory_type="window",
    enable_memory=True
)

# config/settings.py
MEMORY_WINDOW_SIZE = 5  # 减少到 5
```

3. **禁用详细日志：**
```python
agent = EnhancedLangGraphAgent(verbose=False)
```

4. **使用量化模型：**
   - 使用 GPTQ 或 AWQ 量化的模型
   - 或使用 int8/int4 量化

---

### 10. 工具调用不生效

**问题：** Agent 不调用工具

**解决方案：**

1. **检查模型是否支持工具调用：**
   - 确保使用的是支持 function calling 的 Qwen 模型
   - Qwen2.5-Instruct 系列支持较好

2. **调整温度参数：**
```python
# config/settings.py
TEMPERATURE = 0.1  # 降低温度
```

3. **改进提示词：**
```python
custom_prompt = """
你必须使用提供的工具来完成任务。
当需要信息时，调用相应的工具。

格式：<tool_call>{"name": "工具名", "arguments": {...}}</tool_call>
"""

agent = EnhancedLangGraphAgent(system_prompt=custom_prompt)
```

---

## 环境检查清单

运行以下检查：

```bash
# ✅ Python 版本
python --version  # 建议 3.9+

# ✅ PyTorch 和 CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# ✅ 依赖检查
python check_env.py

# ✅ 模块导入
python test_imports.py

# ✅ 磁盘空间
df -h .

# ✅ 显存/内存
nvidia-smi  # GPU
free -h     # RAM
```

---

## 获取帮助

如果问题仍未解决：

1. **查看详细日志：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **运行最小示例：**
```bash
python test_imports.py
```

3. **提供错误信息：**
   - Python 版本
   - 错误堆栈
   - 使用的模型
   - 依赖版本：`pip list | grep -E "langchain|langgraph|transformers"`

4. **查看文档：**
   - [README.md](README.md) - 完整文档
   - [QUICKSTART.md](QUICKSTART.md) - 快速开始
   - [ARCHITECTURE.md](ARCHITECTURE.md) - 架构说明

---

## 版本兼容性

**测试环境：**

```
Python: 3.9+
PyTorch: 2.0.0+
transformers: 4.35.0+
langchain: 0.1.0+
langgraph: 0.2.0+
CUDA: 11.8+ (可选)
```

**推荐配置：**

```bash
# 最小配置
CPU: 4核
RAM: 16GB
模型: Qwen-4B

# 推荐配置
CPU: 8核
RAM: 32GB
GPU: 8GB+ 显存
模型: Qwen-7B

# 生产配置
CPU: 16核
RAM: 64GB
GPU: 24GB+ 显存
模型: Qwen-14B
```

---

**仍有问题？** 提交 Issue 并附上诊断信息：

```bash
python check_env.py > diagnostic.txt
python test_imports.py >> diagnostic.txt 2>&1
```
