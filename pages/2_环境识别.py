"""环境识别：单次拍照，识别台阶/障碍物/红绿灯/门牌并语音播报。"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui import (
    get_image_input,
    get_orchestrator,
    render_audio,
    render_footer,
    render_header,
    set_page,
    show_setup_banner,
)
from src.utils import format_environment, resize_image

set_page()
render_header("👁️ 环境识别", "拍一张照，立即识别并播报您周围的环境")

orch = get_orchestrator()
if not show_setup_banner(orch):
    st.stop()

image_bytes = get_image_input("拍照（对准您前方的环境）")

if image_bytes is not None:
    with st.spinner("🔍 正在识别环境……"):
        img, mime = resize_image(
            image_bytes, max_edge=orch.config.image_max_edge, quality=orch.config.image_quality
        )
        result = orch.recognize(img, mime)

    if result.ok:
        if result.guidance:
            env_part = result.environment_speech or ""
            att_part = result.attention or ""
            st.markdown(f'<div class="speech-big">📋 环境详情：{env_part}<br>⚠️ 注意事项：{att_part}</div>', unsafe_allow_html=True)
            render_audio(result.audio)
        with st.expander("🔎 环境识别详情"):
            st.markdown(format_environment(result.environment or {}))
    else:
        st.error(result.error)

render_footer()
