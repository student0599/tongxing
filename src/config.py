"""配置加载模块。

配置读取优先级：环境变量 > Streamlit secrets > .env 文件 > 默认值。
本地开发填写 .env；部署到 Streamlit Cloud 时在 secrets.toml 中配置同名键。
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# 尝试加载 .env 文件（本地开发）
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _read_secret(key: str, default: str = "") -> str:
    """按优先级读取单个配置项，任何异常都不应中断程序。"""
    # 1. 环境变量
    val = os.getenv(key)
    if val:
        return val

    # 2. Streamlit secrets（部署环境）
    try:
        import streamlit as st

        secrets = st.secrets
        if secrets and key in secrets:
            return str(secrets[key])
        # 支持嵌套写法，例如 secrets["zhipu"]["api_key"] 对应 ZHIPU_API_KEY
        section, _, sub = key.lower().partition("_")
        if section and sub:
            obj = secrets.get(section) if hasattr(secrets, "get") else None
            if isinstance(obj, dict) and sub in obj:
                return str(obj[sub])
    except Exception:
        pass

    return default


@dataclass
class Config:
    """全局配置对象。"""

    # 智谱开放平台
    zhipu_api_key: str = ""
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"

    # 模型
    vision_model: str = "glm-4v-flash"   # 免费视觉模型
    text_model: str = "glm-4-flash"      # 免费文本模型

    # 生成参数
    temperature: float = 0.3
    max_tokens: int = 1024
    timeout: int = 60

    # TTS（Edge-TTS）
    tts_voice: str = "zh-CN-XiaoxiaoNeural"  # 默认晓晓，温柔女声
    tts_rate: str = "+0%"
    tts_volume: str = "+0%"

    # 紧急联系人
    emergency_contact_name: str = "家人"
    emergency_contact_phone: str = ""

    # 图片压缩（减少API传输耗时，符合视觉模型尺寸限制）
    image_max_edge: int = 1568
    image_quality: int = 85

    @property
    def is_configured(self) -> bool:
        """API Key 是否已配置。"""
        return bool(self.zhipu_api_key and self.zhipu_api_key != "your_zhipu_api_key_here")


def load_config() -> Config:
    """从环境/密钥中加载配置。"""
    return Config(
        zhipu_api_key=_read_secret("ZHIPU_API_KEY"),
        emergency_contact_name=_read_secret("EMERGENCY_CONTACT_NAME", "家人"),
        emergency_contact_phone=_read_secret("EMERGENCY_CONTACT_PHONE", ""),
    )


# 模块级单例，供各处直接引用
CONFIG = load_config()
