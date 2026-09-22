"""视觉识别子智能体（GLM-4V-Flash）。

职责：把视障用户拍摄的照片转换为结构化的环境信息，
识别台阶、障碍物、红绿灯、门牌、斑马线、路缘石等关键要素。
"""

from __future__ import annotations

from typing import Any, Dict

from src import prompts
from src.agents.base import AgentResult, BaseAgent
from src.llm_client import ZhipuClient
from src.utils import extract_json


class VisionAgent(BaseAgent):
    name = "vision"
    description = "环境视觉识别（GLM-4V-Flash）"

    def __init__(self, client: ZhipuClient, model: str = "glm-4v-flash") -> None:
        super().__init__(client)
        self.model = model

    def run(self, image_bytes: bytes, mime: str = "image/jpeg") -> AgentResult:
        """分析一张图片，返回结构化的环境 JSON。"""
        if not self.client:
            return AgentResult.failure("视觉智能体未初始化（缺少 API 客户端）")

        try:
            raw = self.client.vision(
                image_bytes,
                prompt=prompts.VISION_ANALYZE_PROMPT,
                model=self.model,
                mime=mime,
                temperature=0.2,   # 视觉识别偏确定性
                max_tokens=1024,
            )
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"视觉识别失败：{exc}")

        env = extract_json(raw)
        if env is None:
            # 模型未按 JSON 输出时，退化为纯文本描述
            env = {"scene_type": "未知", "summary": raw.strip(), "guidance": raw.strip()}
        return AgentResult.success(env)

    def describe(self, image_bytes: bytes, mime: str = "image/jpeg") -> AgentResult:
        """轻量模式：仅返回一句话场景描述。"""
        if not self.client:
            return AgentResult.failure("视觉智能体未初始化")
        try:
            raw = self.client.vision(
                image_bytes,
                prompt="请用一句口语化的话描述这张照片中的场景，重点说明对视障者重要的信息。",
                model=self.model,
                mime=mime,
                temperature=0.3,
                max_tokens=128,
            )
            return AgentResult.success(raw.strip())
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"视觉识别失败：{exc}")
