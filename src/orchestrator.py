"""编排器：协调各子智能体，实现核心业务流水线。

参照 Claude Agent SDK 的多智能体编排思想，将复杂任务拆分为多个
职责单一的子智能体，由 Orchestrator 统一调度：

  连续导航：拍照 -> 视觉识别(VisionAgent) -> 指引生成(GuidanceAgent) -> 语音合成(TTSAgent)
  文字朗读：拍照 -> 文字识别(OCRAgent) -> 语音合成(TTSAgent)
  紧急求助：情况描述 -> 求助分析(EmergencyAgent) -> 语音合成(TTSAgent)

编排器对外暴露与前端无关的接口，便于单元测试与复用。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.agents import EmergencyAgent, GuidanceAgent, OCRAgent, TTSAgent, VisionAgent
from src.config import Config
from src.llm_client import ZhipuClient, ZhipuError
from src.session import NavigationSession


@dataclass
class NavigateResult:
    """一次导航步骤的完整结果。"""

    ok: bool
    environment: Optional[Dict[str, Any]] = None
    guidance: Optional[str] = None
    audio: Optional[bytes] = None
    error: str = ""


@dataclass
class ReadResult:
    """一次文字朗读的完整结果。"""

    ok: bool
    text: Optional[str] = None
    audio: Optional[bytes] = None
    error: str = ""


@dataclass
class EmergencyResult:
    """一次紧急求助的完整结果。"""

    ok: bool
    info: Optional[Dict[str, Any]] = None
    audio: Optional[bytes] = None
    error: str = ""


class Orchestrator:
    """瞳行核心编排器。"""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client: Optional[ZhipuClient] = None
        if config.is_configured:
            try:
                self.client = ZhipuClient(
                    config.zhipu_api_key, base_url=config.base_url, timeout=config.timeout
                )
            except ZhipuError as exc:
                self.client = None
                self._init_error = str(exc)
        else:
            self._init_error = "未配置智谱 API Key"

        # 子智能体
        self.vision = VisionAgent(self.client, model=config.vision_model)
        self.guidance = GuidanceAgent(self.client, model=config.text_model)
        self.ocr = OCRAgent(self.client, model=config.vision_model)
        self.emergency = EmergencyAgent(self.client, model=config.text_model)
        self.tts = TTSAgent(voice=config.tts_voice, rate=config.tts_rate, volume=config.tts_volume)

    @property
    def ready(self) -> bool:
        """是否已正确初始化（API Key 就绪）。"""
        return self.client is not None

    # ------------------------------------------------------------------ #
    # 连续导航
    # ------------------------------------------------------------------ #
    def navigate_step(
        self, image_bytes: bytes, mime: str, session: NavigationSession
    ) -> NavigateResult:
        """执行一次导航步骤：识别 + 指引 + 播报。"""
        if not self.ready:
            return NavigateResult(ok=False, error=self._init_error)

        # 1. 视觉识别
        env_res = self.vision.run(image_bytes, mime=mime)
        if not env_res.ok:
            return NavigateResult(ok=False, error=env_res.error)
        environment = env_res.data

        # 2. 指引生成（携带历史上下文）
        guide_res = self.guidance.run(
            environment=environment,
            goal=session.goal,
            history=session.history(n=3),
        )
        if not guide_res.ok:
            return NavigateResult(ok=False, environment=environment, error=guide_res.error)
        guidance = guide_res.data

        # 3. 语音合成
        tts_res = self.tts.run(guidance)
        if not tts_res.ok:
            # TTS 失败不阻断流程，仍返回指引文本
            return NavigateResult(ok=True, environment=environment, guidance=guidance, error=f"语音合成失败：{tts_res.error}")

        # 4. 记录会话
        session.add_turn(environment, guidance)
        return NavigateResult(ok=True, environment=environment, guidance=guidance, audio=tts_res.data)

    # ------------------------------------------------------------------ #
    # 单次环境识别（不含上下文）
    # ------------------------------------------------------------------ #
    def recognize(self, image_bytes: bytes, mime: str) -> NavigateResult:
        """单次环境识别 + 语音播报（不写入导航会话）。"""
        if not self.ready:
            return NavigateResult(ok=False, error=self._init_error)

        env_res = self.vision.run(image_bytes, mime=mime)
        if not env_res.ok:
            return NavigateResult(ok=False, error=env_res.error)
        environment = env_res.data

        guide_res = self.guidance.run(environment=environment, goal="", history=None)
        if not guide_res.ok:
            return NavigateResult(ok=False, environment=environment, error=guide_res.error)
        guidance = guide_res.data

        tts_res = self.tts.run(guidance)
        return NavigateResult(
            ok=True,
            environment=environment,
            guidance=guidance,
            audio=tts_res.data if tts_res.ok else None,
        )

    # ------------------------------------------------------------------ #
    # 文字朗读
    # ------------------------------------------------------------------ #
    def read_text(self, image_bytes: bytes, mime: str) -> ReadResult:
        """识别图片文字并朗读。"""
        if not self.ready:
            return ReadResult(ok=False, error=self._init_error)

        ocr_res = self.ocr.run(image_bytes, mime=mime)
        if not ocr_res.ok:
            return ReadResult(ok=False, error=ocr_res.error)
        text = ocr_res.data

        tts_res = self.tts.run(text)
        return ReadResult(
            ok=True,
            text=text,
            audio=tts_res.data if tts_res.ok else None,
            error="" if tts_res.ok else f"语音合成失败：{tts_res.error}",
        )

    # ------------------------------------------------------------------ #
    # 紧急求助
    # ------------------------------------------------------------------ #
    def handle_emergency(self, situation: str, location: str) -> EmergencyResult:
        """分析求助情况并生成播报。"""
        em_res = self.emergency.run(situation, location)
        if not em_res.ok:
            return EmergencyResult(ok=False, error=em_res.error)
        info = em_res.data

        broadcast = info.get("broadcast") or "请帮帮我！"
        tts_res = self.tts.run(broadcast, rate="+10%")  # 求助时语速稍快、声音稍大
        return EmergencyResult(
            ok=True,
            info=info,
            audio=tts_res.data if tts_res.ok else None,
            error="" if tts_res.ok else f"语音合成失败：{tts_res.error}",
        )
