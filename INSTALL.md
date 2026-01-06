# 🚀 安装指南

## 快速安装（3步）

### 1️⃣ 安装依赖

```bash
# 进入项目目录
cd Agent_Qwen3

# 安装 Python 依赖
pip install -r requirements.txt
```

**注意：** 如果遇到网络问题，可以使用镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2️⃣ 验证安装

```bash
# 检查所有依赖是否正确安装
python check_env.py

# 测试模块导入
python test_imports.py
```

**期望输出：**
```
✅ 所有依赖已正确安装！
✅ 所有模块导入测试通过！
```

### 3️⃣ 配置模型

```bash
# 设置模型路径（替换为你的实际路径）
export MODEL_PATH="/home/jmc/llm/Qwen3-4B"

# 验证路径
ls $MODEL_PATH
# 应该看到 config.json, tokenizer.json 等文件
```

## 详细安装步骤

### 前置要求

- **Python**: 3.9 或更高版本
- **磁盘空间**: 至少 20GB（用于模型和依赖）
- **内存**:
  - 最小 16GB RAM（运行 4B 模型）
  - 推荐 32GB+ RAM（运行 7B+ 模型）
- **GPU**（可选）:
  - 8GB+ 显存（4B 模型）
  - 16GB+ 显存（7B 模型）
  - 24GB+ 显存（14B 模型）

### 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 安装 PyTorch

根据你的硬件选择合适的 PyTorch 版本：

#### CPU 版本

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### GPU 版本（CUDA 11.8）

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### GPU 版本（CUDA 12.1）

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 安装项目依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果遇到错误，尝试逐个安装关键依赖
pip install transformers accelerate
pip install langchain langchain-core langchain-community
pip install langgraph>=0.2.0
pip install langchain-huggingface
pip install faiss-cpu sentence-transformers
pip install duckduckgo-search
```

### 验证安装

#### 1. 检查 PyTorch

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

#### 2. 检查 LangGraph

```bash
python -c "from langgraph.prebuilt import create_react_agent; print('LangGraph OK')"
```

#### 3. 完整环境检查

```bash
python check_env.py
```

#### 4. 测试模块导入

```bash
python test_imports.py
```

## 可选组件安装

### FAISS GPU 版本（如果有 GPU）

```bash
# 卸载 CPU 版本
pip uninstall faiss-cpu -y

# 安装 GPU 版本
pip install faiss-gpu
```

### 高级搜索工具（需要 API key）

```bash
# Tavily 搜索
pip install tavily-python

# 配置 API key
export TAVILY_API_KEY="your_api_key_here"
```

### Jupyter Notebook 支持

```bash
pip install jupyter ipykernel

# 创建 kernel
python -m ipykernel install --user --name=agent_env --display-name="Agent Qwen"
```

## 下载模型

### 方法 1: 使用 Hugging Face

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-4B-Instruct"  # 或其他 Qwen 模型

# 下载模型
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 保存到本地
model.save_pretrained("/path/to/save/model")
tokenizer.save_pretrained("/path/to/save/model")
```

### 方法 2: 使用 git-lfs

```bash
# 安装 git-lfs
git lfs install

# 克隆模型
git clone https://huggingface.co/Qwen/Qwen2.5-4B-Instruct /path/to/save/model
```

### 方法 3: 使用 ModelScope（国内用户）

```bash
# 安装 modelscope
pip install modelscope

# 下载模型
python -c "
from modelscope import snapshot_download
model_dir = snapshot_download('Qwen/Qwen2.5-4B-Instruct', cache_dir='/path/to/save')
print(f'Model downloaded to: {model_dir}')
"
```

## 配置环境变量

### 临时设置（当前会话）

```bash
export MODEL_PATH="/path/to/your/model"
```

### 永久设置

#### Linux/Mac

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
echo 'export MODEL_PATH="/path/to/your/model"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows

```cmd
setx MODEL_PATH "C:\path\to\your\model"
```

### 使用 .env 文件

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器

# 添加配置
MODEL_PATH=/path/to/your/model
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

## 测试安装

### 最小测试

```bash
python -c "
from agent import EnhancedLangGraphAgent
print('✅ Agent导入成功！')
"
```

### 完整测试（需要模型）

```bash
# 设置模型路径
export MODEL_PATH="/path/to/your/model"

# 运行简单示例
python examples/simple_example.py
```

## 故障排查

如果遇到问题，请查看：

1. **环境检查**: `python check_env.py`
2. **导入测试**: `python test_imports.py`
3. **故障排查指南**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 常见问题快速修复

#### 问题 1: langgraph 导入错误

```bash
pip install --upgrade langgraph>=0.2.0
```

#### 问题 2: transformers 版本过低

```bash
pip install --upgrade transformers>=4.35.0
```

#### 问题 3: CUDA 相关错误

```bash
# 检查 CUDA 版本
nvidia-smi

# 重新安装对应版本的 PyTorch
pip install torch --upgrade --index-url https://download.pytorch.org/whl/cu118
```

## 卸载

```bash
# 删除虚拟环境
deactivate  # 先退出虚拟环境
rm -rf venv

# 或者只卸载依赖
pip uninstall -r requirements.txt -y
```

## 下一步

安装完成后：

1. 阅读 [QUICKSTART.md](QUICKSTART.md) 快速开始
2. 运行 `python main.py` 尝试交互模式
3. 查看 [examples/](examples/) 目录的示例代码
4. 阅读 [README.md](README.md) 了解完整功能

---

**需要帮助？** 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 或提交 Issue。
