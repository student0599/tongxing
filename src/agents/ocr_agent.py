"""文字朗读子智能体（GLM-4V-Flash 视觉提取文字）。

职责：识别图片中的招牌、门牌、路牌、票据、菜单、药品说明等文字，
供 TTS 朗读给视障用户。
"""

from __future__ import annotations

from src import prompts
from src.agents.base import AgentResult, BaseAgent
from src.llm_client import ZhipuClient


class OCRAgent(BaseAgent):
    name = "ocr"
    description = "文字识别与朗读（GLM-4V-Flash）"

    def __init__(self, client: ZhipuClient, model: str = "glm-4v-flash") -> None:
        super().__init__(client)
        self.model = model

    def run(self, image_bytes: bytes, mime: str = "image/jpeg") -> AgentResult:
        """提取图片中的全部文字，返回字符串。"""
        if not self.client:
            return AgentResult.failure("文字朗读智能体未初始化")

        try:
            raw = self.client.vision(
                image_bytes,
                prompt=prompts.OCR_USER_PROMPT,
                model=self.model,
                mime=mime,
                temperature=0.1,   # 文字提取要求确定性
                max_tokens=1024,
            )
            return AgentResult.success(raw.strip())
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"文字识别失败：{exc}")
