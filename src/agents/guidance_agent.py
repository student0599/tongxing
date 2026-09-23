"""语音指引生成子智能体（GLM-4-Flash）。

职责：把视觉识别结果 + 导航历史上下文，转换为一句口语化、
安全优先、可被 TTS 直接播报的语音指引。
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src import prompts
from src.agents.base import AgentResult, BaseAgent
from src.llm_client import ZhipuClient
from src.utils import extract_json


class GuidanceAgent(BaseAgent):
    name = "guidance"
    description = "语音指引生成（GLM-4-Flash）"

    def __init__(self, client: ZhipuClient, model: str = "glm-4-flash") -> None:
        super().__init__(client)
        self.model = model

    def run(
        self,
        environment: Dict[str, Any],
        goal: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResult:
        """根据环境与历史上下文生成一句语音指引。"""
        if not self.client:
            return AgentResult.failure("指引智能体未初始化")

        env_json = json.dumps(environment, ensure_ascii=False)
        history_text = self._format_history(history)

        prompt = prompts.GUIDANCE_USER_PROMPT.format(
            goal=goal or "（用户未设定具体目的地）",
            environment_json=env_json,
            history_text=history_text or "（暂无历史，这是第一步）",
        )

        try:
            raw = self.client.text(
                prompt,
                system=prompts.GUIDANCE_SYSTEM_PROMPT,
                model=self.model,
                temperature=0.5,   # 口语化需要一定多样性
                max_tokens=256,
            )
            guidance = raw.strip().strip("。；;．") + "。"
            return AgentResult.success(guidance)
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"指引生成失败：{exc}")

    def narrate(
        self,
        environment: Dict[str, Any],
        goal: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResult:
        """生成两段式播报：先环境详情，再注意事项。返回 {"environment_speech", "attention"}。"""
        if not self.client:
            return AgentResult.failure("播报智能体未初始化")

        env_json = json.dumps(environment, ensure_ascii=False)
        history_text = self._format_history(history)
        prompt = prompts.NARRATION_USER_PROMPT.format(
            goal=goal or "（用户未设定具体目的地）",
            environment_json=env_json,
            history_text=history_text or "（暂无历史，这是第一步）",
        )

        try:
            raw = self.client.text(
                prompt,
                system=prompts.NARRATION_SYSTEM_PROMPT,
                model=self.model,
                temperature=0.5,
                max_tokens=512,
            )
            data = extract_json(raw)
            if not isinstance(data, dict):
                raise ValueError("播报结果不是有效 JSON")
            environment_speech = (data.get("environment_speech") or "").strip()
            attention = (data.get("attention") or "").strip()
        except Exception:  # noqa: BLE001
            # 降级：直接用视觉输出的 summary + guidance
            environment_speech = (environment.get("summary") or "").strip()
            attention = (environment.get("guidance") or "").strip()

        if not environment_speech:
            environment_speech = (environment.get("summary") or "").strip()
        if not attention:
            attention = (environment.get("guidance") or "").strip()

        return AgentResult.success(
            {"environment_speech": environment_speech, "attention": attention}
        )

    @staticmethod
    def _format_history(history: Optional[List[Dict[str, Any]]]) -> str:
        """把最近若干轮指引拼成可读文本，供模型避免重复。"""
        if not history:
            return ""
        lines = []
        for i, h in enumerate(history[-3:]):  # 只取最近 3 轮，控制上下文长度
            step = h.get("step", i + 1)
            guidance = h.get("guidance", "")
            if guidance:
                lines.append(f"第{step}步已提醒：{guidance}")
        return "\n".join(lines)
