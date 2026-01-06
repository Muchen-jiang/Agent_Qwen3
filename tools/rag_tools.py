"""
本地RAG工具
实现基于向量数据库的文档检索功能
"""
import os
from typing import List, Optional
from pathlib import Path
from langchain_core.tools import tool
from config import rag_config
import logging

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG系统单例"""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.vectorstore = None
            self.embeddings = None
            self._initialized = True

    def initialize(self):
        """初始化向量数据库和嵌入模型"""
        if self.vectorstore is not None:
            return

        try:
            # 导入依赖
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_community.document_loaders import (
                DirectoryLoader,
                TextLoader,
                PyPDFLoader
            )
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            logger.info("正在初始化RAG系统...")

            # 1. 初始化嵌入模型
            logger.info(f"加载嵌入模型: {rag_config.EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=rag_config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cuda'},
                encode_kwargs={'normalize_embeddings': True}
            )

            # 2. 检查是否存在已有的向量数据库
            vector_db_path = Path(rag_config.VECTOR_DB_PATH)

            if vector_db_path.exists() and (vector_db_path / "index.faiss").exists():
                # 加载现有数据库
                logger.info("加载现有向量数据库...")
                self.vectorstore = FAISS.load_local(
                    str(vector_db_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("✅ 向量数据库加载成功")
            else:
                # 创建新数据库
                logger.info("创建新的向量数据库...")
                docs_path = Path(rag_config.DOCUMENTS_PATH)

                if not docs_path.exists() or not any(docs_path.iterdir()):
                    logger.warning(
                        f"文档目录为空: {docs_path}\n"
                        "请将文档放入该目录后重新初始化"
                    )
                    # 创建空的向量数据库
                    from langchain.schema import Document
                    dummy_doc = Document(
                        page_content="这是一个占位文档，请添加真实文档到 data/rag_docs 目录",
                        metadata={"source": "placeholder"}
                    )
                    self.vectorstore = FAISS.from_documents(
                        [dummy_doc],
                        self.embeddings
                    )
                else:
                    # 加载文档
                    documents = self._load_documents(docs_path)

                    if not documents:
                        logger.warning("未找到有效文档")
                        return

                    # 分割文档
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=rag_config.CHUNK_SIZE,
                        chunk_overlap=rag_config.CHUNK_OVERLAP,
                        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
                    )
                    splits = text_splitter.split_documents(documents)
                    logger.info(f"文档已分割为 {len(splits)} 个块")

                    # 创建向量数据库
                    self.vectorstore = FAISS.from_documents(
                        splits,
                        self.embeddings
                    )

                # 保存数据库
                vector_db_path.mkdir(parents=True, exist_ok=True)
                self.vectorstore.save_local(str(vector_db_path))
                logger.info(f"✅ 向量数据库已保存到: {vector_db_path}")

        except Exception as e:
            logger.error(f"RAG系统初始化失败: {e}")
            raise

    def _load_documents(self, docs_path: Path) -> List:
        """加载文档"""
        from langchain_community.document_loaders import (
            DirectoryLoader,
            TextLoader,
            PyPDFLoader
        )

        documents = []

        # 加载文本文件
        for ext in ['txt', 'md']:
            try:
                loader = DirectoryLoader(
                    str(docs_path),
                    glob=f"**/*.{ext}",
                    loader_cls=TextLoader,
                    loader_kwargs={'encoding': 'utf-8'}
                )
                documents.extend(loader.load())
            except Exception as e:
                logger.warning(f"加载 .{ext} 文件失败: {e}")

        # 加载PDF文件
        for pdf_file in docs_path.glob("**/*.pdf"):
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents.extend(loader.load())
            except Exception as e:
                logger.warning(f"加载PDF失败 {pdf_file}: {e}")

        logger.info(f"共加载 {len(documents)} 个文档")
        return documents

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """检索相关文档"""
        if self.vectorstore is None:
            self.initialize()

        try:
            # 相似度搜索
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query,
                k=top_k
            )

            results = []
            for doc, score in docs_with_scores:
                # 分数越低越相似（距离度量）
                similarity = 1 / (1 + score)  # 转换为相似度

                if similarity < rag_config.SCORE_THRESHOLD:
                    continue

                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': similarity
                })

            return results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def add_documents(self, docs_path: str) -> str:
        """添加新文档到向量数据库"""
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            documents = self._load_documents(Path(docs_path))

            if not documents:
                return "未找到有效文档"

            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=rag_config.CHUNK_SIZE,
                chunk_overlap=rag_config.CHUNK_OVERLAP
            )
            splits = text_splitter.split_documents(documents)

            # 添加到向量数据库
            if self.vectorstore is None:
                self.initialize()

            self.vectorstore.add_documents(splits)

            # 保存
            self.vectorstore.save_local(rag_config.VECTOR_DB_PATH)

            return f"成功添加 {len(documents)} 个文档，共 {len(splits)} 个块"

        except Exception as e:
            return f"添加文档失败: {str(e)}"


# 全局RAG实例
rag_system = RAGSystem()


@tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """
    在本地知识库中搜索相关信息。

    Args:
        query: 搜索查询
        top_k: 返回最相关的文档数量，默认为3

    Returns:
        检索到的相关文档内容
    """
    try:
        results = rag_system.search(query, top_k)

        if not results:
            return (
                f"在知识库中未找到关于 '{query}' 的相关信息。\n"
                f"提示: 请确保已将文档添加到 {rag_config.DOCUMENTS_PATH}"
            )

        formatted_results = []
        for idx, result in enumerate(results, 1):
            content = result['content']
            source = result['metadata'].get('source', 'Unknown')
            score = result['score']

            formatted_results.append(
                f"{idx}. [相关度: {score:.2%}]\n"
                f"   来源: {source}\n"
                f"   内容: {content[:300]}...\n"
            )

        return (
            f"知识库检索结果 (查询: '{query}'):\n\n" +
            "\n".join(formatted_results)
        )

    except Exception as e:
        logger.error(f"知识库检索错误: {e}")
        return f"检索知识库时发生错误: {str(e)}"


@tool
def add_documents_to_knowledge_base(directory_path: str) -> str:
    """
    将指定目录下的文档添加到知识库。

    Args:
        directory_path: 文档目录路径

    Returns:
        操作结果
    """
    return rag_system.add_documents(directory_path)


# 导出
__all__ = ['search_knowledge_base', 'add_documents_to_knowledge_base', 'rag_system']
