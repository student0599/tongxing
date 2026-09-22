"""连续导航：解决 GPS 导航结束后「最后十米」盲区。

流程：设定目的地 → 连续拍照 → 视觉识别 + 多轮上下文 → 连贯语音指引。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 保证可导入项目根目录下的 src 包
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.agents.tts_agent import VOICES
from src.session import NavigationSession
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
render_header("🚶 连续导航", "拍照识别 + 语音指引，解决导航终点的「最后十米」盲区")

orch = get_orchestrator()
if not show_setup_banner(orch):
    st.stop()

# ---------------- 会话初始化 ----------------
if "nav_session" not in st.session_state:
    st.session_state.nav_session = NavigationSession()
session: NavigationSession = st.session_state.nav_session

# ---------------- 目的地设定 ----------------
goal = st.text_input(
    "📍 您要去哪里？（可留空，AI 会帮您观察环境）",
    value=session.goal,
    placeholder="例如：3号楼2单元门口 / 药店 / 地铁站A口",
)
if goal and goal != session.goal:
    session.set_goal(goal)
    session.turns.clear()  # 更换目的地则重新开始

# ---------------- 语音设置 ----------------
with st.expander("🔊 语音设置"):
    voice_label = st.selectbox("选择播报音色", list(VOICES.keys()), index=0)
    orch.tts.voice = VOICES[voice_label]

# ---------------- 拍照 / 上传 ----------------
image_bytes = get_image_input("拍照（对准您前方的环境）")

# ---------------- 执行导航 ----------------
if image_bytes is not None:
    with st.spinner("🔍 正在识别环境并生成指引……"):
        img, mime = resize_image(
            image_bytes, max_edge=orch.config.image_max_edge, quality=orch.config.image_quality
        )
        result = orch.navigate_step(img, mime, session)

    if result.ok:
        if result.guidance:
            st.markdown(f'<div class="speech-big">🗣️ {result.guidance}</div>', unsafe_allow_html=True)
            render_audio(result.audio)
        with st.expander("🔎 环境识别详情"):
            st.markdown(format_environment(result.environment or {}))
        st.caption(f"已连续指引 {session.step_count} 步")
    else:
        st.error(result.error)

# ---------------- 导航历史 ----------------
if session.step_count > 0:
    with st.expander("🧭 本次导航记录"):
        st.markdown(session.summary())
    if st.button("🔄 重新开始导航", type="secondary", use_container_width=True):
        session.reset()
        st.rerun()

render_footer()
