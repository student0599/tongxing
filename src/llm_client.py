"""智谱 AI（Zhipu BigModel）开放平台客户端封装。

统一封装文本对话（GLM-4-Flash）与视觉理解（GLM-4V-Flash）两种能力，
内置重试与友好错误提示，供各子智能体复用。
"""

from __future__ import annotations

import base64
import time
from typing import Any, Dict, List, Optional

import requests


class ZhipuError(RuntimeError):
    """智谱 API 调用异常。"""


class ZhipuClient:
    """智谱开放平台 HTTP 客户端。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: int = 60,
    ) -> None:
        if not api_key:
            raise ZhipuError("未配置智谱 API Key，请在 .env 或 secrets 中设置 ZHIPU_API_KEY")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    # 底层请求
    # ------------------------------------------------------------------ #
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
        retries: int = 3,
    ) -> str:
        """调用 chat/completions，返回助手的文本内容。"""
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        last_err: Optional[str] = None
        for attempt in range(retries):
            try:
                resp = requests.post(
                    url, headers=self._headers(), json=payload, timeout=self.timeout
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                last_err = f"HTTP {resp.status_code}: {resp.text[:300]}"
            except requests.RequestException as exc:  # 网络层异常
                last_err = str(exc)
            except (KeyError, IndexError, ValueError) as exc:  # 响应结构异常
                last_err = f"响应解析失败: {exc}"

            time.sleep(1 + attempt)  # 简单退避

        raise ZhipuError(f"智谱 API 调用失败：{last_err}")

    # ------------------------------------------------------------------ #
    # 高层能力
    # ------------------------------------------------------------------ #
    def text(
        self,
        prompt: str,
        system: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = "glm-4-flash",
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """纯文本对话。history 为 [{"role": ..., "content": ...}, ...]。"""
        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        return self.chat(model, messages, temperature=temperature, max_tokens=max_tokens)

    def vision(
        self,
        image_bytes: bytes,
        prompt: str,
        model: str = "glm-4v-flash",
        mime: str = "image/jpeg",
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """视觉理解：传入图片字节与提示词，返回文本。"""
        b64 = base64.b64encode(image_bytes).decode("ascii")
        messages: List[Dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ]
        return self.chat(model, messages, temperature=temperature, max_tokens=max_tokens)
