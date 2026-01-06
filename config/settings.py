"""
配置管理模块
集中管理所有配置项，支持环境变量和默认值
"""
import os
from pathlib import Path
from typing import Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# ==========================================
# 模型配置
# ==========================================
class ModelConfig:
    """LLM模型配置"""
    MODEL_PATH: str = os.getenv(
        "MODEL_PATH",
        "/home/jmc/llm/Qwen3-4B"
    )
    DEVICE_MAP: str = "auto"
    TORCH_DTYPE: str = "float16"
    MAX_NEW_TOKENS: int = 2048
    TEMPERATURE: float = 0.1
    DO_SAMPLE: bool = True
    TOP_P: float = 0.9
    TOP_K: int = 50

# ==========================================
# RAG配置
# ==========================================
class RAGConfig:
    """检索增强生成配置"""
    # 向量数据库配置
    VECTOR_DB_TYPE: str = "faiss"  # faiss, chroma
    VECTOR_DB_PATH: str = str(PROJECT_ROOT / "data" / "vector_db")

    # 文档存储路径
    DOCUMENTS_PATH: str = str(PROJECT_ROOT / "data" / "rag_docs")

    # Embedding模型
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "BAAI/bge-small-zh-v1.5"  # 中文embedding模型
    )

    # 检索配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3
    SCORE_THRESHOLD: float = 0.5

# ==========================================
# 搜索配置
# ==========================================
class SearchConfig:
    """网络搜索配置"""
    # 搜索引擎选择: duckduckgo, tavily, serper
    SEARCH_ENGINE: str = os.getenv("SEARCH_ENGINE", "duckduckgo")

    # Tavily API (如果使用)
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")

    # Serper API (如果使用)
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")

    # 搜索结果数量
    MAX_RESULTS: int = 5

# ==========================================
# Agent配置
# ==========================================
class AgentConfig:
    """Agent运行配置"""
    # 最大迭代次数
    MAX_ITERATIONS: int = 10

    # 是否启用流式输出
    ENABLE_STREAMING: bool = True

    # 是否启用记忆
    ENABLE_MEMORY: bool = True

    # 记忆窗口大小
    MEMORY_WINDOW_SIZE: int = 10

    # 是否启用详细日志
    VERBOSE: bool = True

# ==========================================
# 日志配置
# ==========================================
class LogConfig:
    """日志配置"""
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = str(PROJECT_ROOT / "logs" / "agent.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==========================================
# 全局配置实例
# ==========================================
model_config = ModelConfig()
rag_config = RAGConfig()
search_config = SearchConfig()
agent_config = AgentConfig()
log_config = LogConfig()
