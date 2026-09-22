"""语音合成子智能体（Edge-TTS，免费中文语音）。

职责：把文字转换为中文语音（MP3 字节流），供前端实时播报。
Edge-TTS 使用微软神经网络语音，免费、无需密钥、支持多种中文音色。
"""

from __future__ import annotations

import asyncio
from typing import Dict, Optional

from src.agents.base import AgentResult, BaseAgent


# 常用中文音色（音色可扩展）
VOICES: Dict[str, str] = {
    "晓晓（女声·温柔）": "zh-CN-XiaoxiaoNeural",
    "晓伊（女声·活泼）": "zh-CN-XiaoyiNeural",
    "云希（男声·年轻）": "zh-CN-YunxiNeural",
    "云扬（男声·新闻）": "zh-CN-YunyangNeural",
    "云健（男声·沉稳）": "zh-CN-YunjianNeural",
}


class TTSAgent(BaseAgent):
    name = "tts"
    description = "语音合成（Edge-TTS）"

    def __init__(
        self,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        volume: str = "+0%",
    ) -> None:
        super().__init__(client=None)  # TTS 无需 LLM 客户端
        self.voice = voice
        self.rate = rate
        self.volume = volume

    async def _collect_audio(self, text: str) -> bytes:
        """异步拉取音频分片并拼接为完整 MP3 字节。"""
        import edge_tts

        communicate = edge_tts.Communicate(
            text, voice=self.voice, rate=self.rate, volume=self.volume
        )
        data = bytearray()
        async for chunk in communicate.stream():
            if chunk.get("type") == "audio":
                data.extend(chunk.get("data", b""))
        return bytes(data)

    def run(self, text: str, voice: Optional[str] = None, rate: Optional[str] = None) -> AgentResult:
        """合成语音，返回音频字节。"""
        text = (text or "").strip()
        if not text:
            return AgentResult.failure("没有可播报的内容")

        if voice is not None:
            self.voice = voice
        if rate is not None:
            self.rate = rate

        try:
            audio = asyncio.run(self._collect_audio(text))
            if not audio:
                return AgentResult.failure("语音合成为空")
            return AgentResult.success(audio)
        except Exception as exc:  # noqa: BLE001
            return AgentResult.failure(f"语音合成失败：{exc}")
