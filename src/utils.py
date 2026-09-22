"""通用工具函数：图片处理、JSON 解析、音频播放等。"""

from __future__ import annotations

import base64
import io
import json
import re
from typing import Any, Optional, Tuple

from PIL import Image


def resize_image(image_bytes: bytes, max_edge: int = 1568, quality: int = 85) -> Tuple[bytes, str]:
    """压缩/缩放图片以加速 API 传输并符合视觉模型尺寸限制。

    返回 (压缩后的字节, mime类型)。
    """
    img = Image.open(io.BytesIO(image_bytes))
    # 统一转 RGB，避免 PNG 透明通道或 EXIF 方向问题
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_edge:
        scale = max_edge / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue(), "image/jpeg"


def extract_json(text: str) -> Optional[Any]:
    """从模型输出中鲁棒地提取 JSON（兼容 markdown 代码块包裹）。"""
    if not text:
        return None
    text = text.strip()
    # 去除 ```json ... ``` 包裹
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 兜底：截取第一个 { 到最后一个 } 之间的内容
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


def bytes_to_base64(data: bytes) -> str:
    """字节转 base64 字符串。"""
    return base64.b64encode(data).decode("ascii")


def autoplay_audio_html(audio_bytes: bytes, mime: str = "audio/mpeg") -> str:
    """生成可自动播放的 HTML audio 标签（Streamlit 原生组件不支持 autoplay）。"""
    b64 = bytes_to_base64(audio_bytes)
    return (
        f'<audio controls autoplay style="width:100%">'
        f'<source src="data:{mime};base64,{b64}" type="{mime}">'
        f"</audio>"
    )


def format_environment(env: dict) -> str:
    """把视觉识别的环境 JSON 格式化成可读文本（供界面展示/调试）。"""
    if not env:
        return "暂无环境信息"
    lines = []
    if env.get("summary"):
        lines.append(f"场景：{env['summary']}")
    obstacles = env.get("obstacles") or []
    for ob in obstacles:
        lines.append(f"⚠️ {ob.get('name', '')}（{ob.get('position', '')}，{ob.get('distance', '')}）")
    if env.get("stairs", {}).get("detected"):
        s = env["stairs"]
        lines.append(f"🪜 台阶：{s.get('direction', '')}，约{s.get('steps', '')}级，扶手{s.get('handrail', '')}")
    if env.get("traffic_light", {}).get("detected"):
        t = env["traffic_light"]
        lines.append(f"🚦 红绿灯：{t.get('color', '')}，剩{t.get('countdown', '')}")
    if env.get("crosswalk", {}).get("detected"):
        lines.append(f"🚶 斑马线在{env['crosswalk'].get('position', '')}")
    if env.get("curb", {}).get("detected"):
        c = env["curb"]
        lines.append(f"🪨 路缘石：{c.get('height', '')}，在{c.get('position', '')}")
    if env.get("doorplate", {}).get("detected"):
        lines.append(f"🚪 门牌：{env['doorplate'].get('text', '')}")
    if env.get("text_content"):
        lines.append(f"📝 文字：{env['text_content']}")
    return "\n".join(lines) if lines else "暂无环境信息"
