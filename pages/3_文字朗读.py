"""文字朗读：识别招牌/票据/药品说明等文字并语音朗读。"""

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
from src.utils import resize_image

set_page()
render_header("📖 文字朗读", "拍下招牌、票据、药品说明，帮您读出文字")

orch = get_orchestrator()
if not show_setup_banner(orch):
    st.stop()

image_bytes = get_image_input("拍照（对准文字）")

if image_bytes is not None:
    with st.spinner("🔍 正在识别文字……"):
        img, mime = resize_image(
            image_bytes, max_edge=orch.config.image_max_edge, quality=orch.config.image_quality
        )
        result = orch.read_text(img, mime)

    if result.ok:
        if result.text:
            st.markdown(f'<div class="speech-big">📝 {result.text}</div>', unsafe_allow_html=True)
            render_audio(result.audio)
            if result.error:
                st.warning(result.error)
    else:
        st.error(result.error)

render_footer()
