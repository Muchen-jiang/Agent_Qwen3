# ⚡ 紧急修复说明

如果你遇到了 `ModuleNotFoundError: No module named 'langgraph.graph.graph'` 错误，请按照以下步骤操作：

## 快速修复（3步）

### 1️⃣ 拉取最新代码

```bash
cd /home/jmc/llm/Agent_Qwen3-claude-langgraph-agent-tools-vUsHK
git pull origin claude/langgraph-agent-tools-vUsHK
```

### 2️⃣ 更新依赖

```bash
pip install --upgrade langgraph>=0.2.0
```

### 3️⃣ 验证修复

```bash
# 测试导入
python test_imports.py

# 如果通过，继续运行
python main.py
```

## 详细说明

已修复的问题：
- ✅ LangGraph API 导入路径错误
- ✅ 添加环境检查脚本 `check_env.py`
- ✅ 添加导入测试脚本 `test_imports.py`
- ✅ 更新 requirements.txt 版本要求
- ✅ 添加完整的故障排查文档

## 如果仍然失败

运行诊断：

```bash
# 1. 检查所有依赖
python check_env.py

# 2. 测试模块导入
python test_imports.py

# 3. 查看详细错误
python main.py 2>&1 | tee error.log
```

然后查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 获取更多帮助。

## 完整重新安装（最后手段）

```bash
# 1. 创建新虚拟环境
python -m venv venv_new
source venv_new/bin/activate

# 2. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 3. 测试
python test_imports.py
```

---

修复完成后，删除此文件：`rm README_FIX.md`
