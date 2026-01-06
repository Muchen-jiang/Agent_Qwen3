# 📖 文档索引

快速找到你需要的文档。

## 🚀 开始使用

| 文档 | 适用场景 | 阅读时间 |
|------|----------|----------|
| **[README_FIX.md](README_FIX.md)** | ⚡ **遇到导入错误？先看这个！** | 2分钟 |
| **[QUICKSTART.md](QUICKSTART.md)** | 5分钟快速上手 | 5分钟 |
| **[INSTALL.md](INSTALL.md)** | 详细安装指南 | 10分钟 |
| **[README.md](README.md)** | 完整使用文档 | 15分钟 |

## 🔧 问题排查

| 文档 | 解决什么问题 |
|------|--------------|
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | 各种错误的解决方案 |
| **[check_env.py](check_env.py)** | 检查依赖安装 |
| **[test_imports.py](test_imports.py)** | 测试模块导入 |

## 🏗️ 深入理解

| 文档 | 内容 |
|------|------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 系统架构设计 |
| **[CHANGELOG.md](CHANGELOG.md)** | 版本更新历史 |

## 📝 示例代码

| 文件 | 说明 |
|------|------|
| **[main.py](main.py)** | 交互式演示系统 |
| **[examples/simple_example.py](examples/simple_example.py)** | 最简单的使用示例 |
| **[examples/custom_tools_example.py](examples/custom_tools_example.py)** | 如何添加自定义工具 |
| **[examples/rag_example.py](examples/rag_example.py)** | 知识库检索示例 |

## 🎯 按需求查找

### 我想快速开始
1. [README_FIX.md](README_FIX.md) - 先解决可能的问题
2. [QUICKSTART.md](QUICKSTART.md) - 5分钟入门
3. `python main.py` - 运行交互模式

### 我想深入学习
1. [README.md](README.md) - 完整功能介绍
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 理解架构
3. [examples/](examples/) - 学习示例代码

### 我遇到了错误
1. [README_FIX.md](README_FIX.md) - 常见错误快速修复
2. `python check_env.py` - 检查环境
3. `python test_imports.py` - 测试导入
4. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 详细排查

### 我想自定义扩展
1. [examples/custom_tools_example.py](examples/custom_tools_example.py) - 学习如何添加工具
2. [ARCHITECTURE.md](ARCHITECTURE.md) - 理解扩展点
3. [tools/](tools/) - 查看现有工具实现

### 我想部署到生产
1. [INSTALL.md](INSTALL.md) - 完整安装指引
2. [README.md](README.md) - 配置说明
3. [ARCHITECTURE.md](ARCHITECTURE.md) - 性能优化

## 📚 推荐阅读顺序

### 新手路径
```
README_FIX.md → QUICKSTART.md → examples/simple_example.py → main.py
```

### 进阶路径
```
README.md → examples/* → ARCHITECTURE.md → 自定义开发
```

### 故障排查路径
```
check_env.py → test_imports.py → TROUBLESHOOTING.md → README_FIX.md
```

## 🔍 关键词索引

- **安装问题**: [INSTALL.md](INSTALL.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **导入错误**: [README_FIX.md](README_FIX.md), [test_imports.py](test_imports.py)
- **模型配置**: [INSTALL.md](INSTALL.md), [config/settings.py](config/settings.py)
- **工具开发**: [examples/custom_tools_example.py](examples/custom_tools_example.py), [tools/](tools/)
- **RAG知识库**: [examples/rag_example.py](examples/rag_example.py), [tools/rag_tools.py](tools/rag_tools.py)
- **网络搜索**: [tools/search_tools.py](tools/search_tools.py)
- **对话记忆**: [memory/](memory/), [ARCHITECTURE.md](ARCHITECTURE.md)
- **性能优化**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md), [config/settings.py](config/settings.py)

## 💡 快速命令

```bash
# 检查环境
python check_env.py

# 测试导入
python test_imports.py

# 运行示例
python main.py                          # 交互模式
python examples/simple_example.py      # 简单示例
python examples/rag_example.py         # RAG示例

# 获取帮助
python main.py --help                  # 查看选项（如果支持）
```

## 📞 获取帮助

1. 先查阅对应文档
2. 运行诊断脚本：`python check_env.py`
3. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. 提交 Issue（附上诊断信息）

---

**提示**: 所有文档都支持 Markdown 格式，可以用任何文本编辑器或 Markdown 阅读器查看。
