from typing import Protocol


class NarratorClient(Protocol):
    """AI 叙事客户端接口"""

    def generate(self, prompt: str) -> str:
        """根据提示词生成叙事文本"""
        ...


class SimpleNarrator:
    """简单的占位实现，后续接入真实模型"""

    def generate(self, prompt: str) -> str:
        # TODO: 接入 qwen3:4b / qwen3:1.7b
        return f"[AI叙事占位] {prompt[:100]}..."
