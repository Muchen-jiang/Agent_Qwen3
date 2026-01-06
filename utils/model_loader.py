"""
模型加载器
负责加载和初始化LLM模型
"""
import torch
import warnings
from typing import Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_huggingface import HuggingFacePipeline, ChatHuggingFace
from config import model_config
import logging

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


class ModelLoader:
    """模型加载器单例类"""

    _instance = None
    _model = None
    _tokenizer = None
    _chat_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_path: Optional[str] = None) -> ChatHuggingFace:
        """
        加载模型并返回ChatHuggingFace实例

        Args:
            model_path: 模型路径，如果为None则使用配置中的路径

        Returns:
            ChatHuggingFace 实例
        """
        if self._chat_model is not None:
            logger.info("模型已加载，返回缓存实例")
            return self._chat_model

        model_path = model_path or model_config.MODEL_PATH

        logger.info(f"🔄 正在加载模型: {model_path}")

        try:
            # 1. 加载分词器
            logger.info("加载分词器...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True
            )

            # 2. 加载模型
            logger.info("加载模型权重...")
            self._model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map=model_config.DEVICE_MAP,
                torch_dtype=getattr(torch, model_config.TORCH_DTYPE),
                trust_remote_code=True
            )

            # 3. 创建Pipeline
            logger.info("创建生成Pipeline...")
            text_pipeline = pipeline(
                "text-generation",
                model=self._model,
                tokenizer=self._tokenizer,
                max_new_tokens=model_config.MAX_NEW_TOKENS,
                return_full_text=False,
                temperature=model_config.TEMPERATURE,
                do_sample=model_config.DO_SAMPLE,
                top_p=model_config.TOP_P,
                top_k=model_config.TOP_K,
            )

            # 4. 包装为LangChain模型
            llm = HuggingFacePipeline(pipeline=text_pipeline)
            self._chat_model = ChatHuggingFace(llm=llm)

            logger.info("✅ 模型加载完成")

            return self._chat_model

        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise

    @property
    def tokenizer(self):
        """获取分词器"""
        if self._tokenizer is None:
            self.load_model()
        return self._tokenizer

    @property
    def chat_model(self):
        """获取聊天模型"""
        if self._chat_model is None:
            self.load_model()
        return self._chat_model


# 全局模型加载器实例
model_loader = ModelLoader()


__all__ = ['model_loader', 'ModelLoader']
