"""紧急求助子智能体（GLM-4-Flash）。

职责：根据用户描述的突发情况判断严重程度，生成自救建议、
面向路人的求助播报文案，以及拨打求助电话时该说的话。
"""

from __future__ import annotations

from typing import Any, Dict

from src import prompts
from src.agents.base import AgentResult, BaseAgent
from src.llm_client import ZhipuClient
from src.utils import extract_json


class EmergencyAgent(BaseAgent):
    name = "emergency"
    description = "紧急求助（GLM-4-Flash）"

    DEFAULT_RESULT: Dict[str, Any] = {
        "severity": "高",
        "category": "遇到危险",
        "advice": "请保持冷静，就近寻找安全位置，并立即向周围人求助。",
        "broadcast": "请帮帮我，我需要帮助！",
        "call_message": "您好，我是一名视障人士，现在遇到了紧急情况，需要您的帮助。",
    }

    def __init__(self, client: ZhipuClient, model: str = "glm-4-flash") -> None:
        super().__init__(client)
        self.model = model

    def run(self, situation: str, location: str = "未知位置") -> AgentResult:
        """根据情况描述生成求助方案。"""
        if not situation or not situation.strip():
            return AgentResult.failure("请描述您遇到的情况")

        if not self.client:
            # 未配置 API 时仍返回可用的兜底求助信息
            return AgentResult.success(dict(self.DEFAULT_RESULT))

        prompt = prompts.EMERGENCY_USER_PROMPT.format(
            situation=situation.strip(), location=location or "未知位置"
        )

        try:
            raw = self.client.text(
                prompt,
                system=prompts.EMERGENCY_SYSTEM_PROMPT,
                model=self.model,
                temperature=0.3,
                max_tokens=512,
            )
            result = extract_json(raw)
            if result is None:
                return AgentResult.success(dict(self.DEFAULT_RESULT))
            # 补齐缺失字段
            for k, v in self.DEFAULT_RESULT.items():
                result.setdefault(k, v)
            return AgentResult.success(result)
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"求助分析失败：{exc}")
