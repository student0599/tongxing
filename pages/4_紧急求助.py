"""紧急求助：语音描述情况，AI 自动识别并执行紧急操作。"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui import get_orchestrator, render_audio, render_footer, render_header, set_page

set_page()
render_header("🆘 紧急求助", "语音描述情况，AI 自动识别并为您求助")

orch = get_orchestrator()

# ---------------- 首次进入自动播报询问 ----------------
if "em_asked" not in st.session_state:
    st.session_state.em_asked = True
    res = orch.tts.run("请描述您遇到的情况，我会立即帮您求助。")
    if res.ok:
        render_audio(res.data)

# ---------------- 位置（可选） ----------------
location = st.text_input("📍 您的大致位置（可选）", placeholder="例如：中山路与人民路交叉口")

# ---------------- 语音录音（主交互） ----------------
st.markdown("### 🎙️ 语音描述情况")
audio = st.audio_input("点击录音，说出您遇到的情况")

situation = ""

if audio is not None:
    with st.spinner("正在识别您的话并生成求助方案……"):
        situation = orch.transcribe(audio)
    if situation:
        st.success(f"✅ 识别到：{situation}")
    else:
        st.warning("未能识别您的话，请重试录音，或改用下方文字输入")

# ---------------- 快捷选择 / 手动输入（备选） ----------------
with st.expander("✍️ 快捷选择 / 手动输入"):
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🩹 跌倒"):
        st.session_state.em_manual = "我不小心跌倒了，站不起来。"
    if c2.button("🧭 迷路"):
        st.session_state.em_manual = "我迷路了，找不到方向。"
    if c3.button("🤒 身体不适"):
        st.session_state.em_manual = "我突然身体不舒服，需要帮助。"
    if c4.button("⚠️ 危险"):
        st.session_state.em_manual = "我遇到了危险，请帮帮我。"
    manual = st.text_area(
        "描述情况", key="em_manual", height=100,
        placeholder="例如：我跌倒了，膝盖很疼……",
    )
    if manual.strip() and st.button("🆘 生成求助信息", type="primary", use_container_width=True):
        situation = manual.strip()

# ---------------- 执行紧急操作 ----------------
if situation.strip():
    with st.spinner("正在生成求助方案……"):
        st.session_state.em_result = orch.handle_emergency(situation.strip(), location.strip())

# ---------------- 显示结果 ----------------
result = st.session_state.get("em_result")
if result is not None:
    if result.ok and result.info:
        info = result.info
        st.markdown(f'<div class="broadcast-big">{info.get("broadcast", "请帮帮我！")}</div>', unsafe_allow_html=True)
        render_audio(result.audio)
        sev = info.get("severity", "高")
        st.markdown(f"**危险程度：{sev}　|　类型：{info.get('category', '')}**")
        def _fmt(s: str) -> str:
            s = (s or "").replace("；；", "\n").replace("；", "\n")
            return s.strip("\n； ").replace("\n", "<br>")

        if info.get("advice"):
            st.markdown(f'<div class="kv-card">💡 自救建议：<br>{_fmt(info["advice"])}</div>', unsafe_allow_html=True)
        if info.get("precautions"):
            st.markdown(f'<div class="kv-card">⚠️ 注意事项：<br>{_fmt(info["precautions"])}</div>', unsafe_allow_html=True)
        if info.get("call_message"):
            st.markdown(f'<div class="kv-card">📞 求助话术：{info["call_message"]}</div>', unsafe_allow_html=True)
        st.markdown("#### ☎️ 紧急电话（点击拨打）")
        p1, p2 = st.columns(2)
        p1.link_button("🚨 报警 110", "tel:110", use_container_width=True)
        p2.link_button("🚑 急救 120", "tel:120", use_container_width=True)
        contact_name = orch.config.emergency_contact_name
        contact_phone = orch.config.emergency_contact_phone
        if contact_phone:
            st.link_button(f"👤 联系 {contact_name}", f"tel:{contact_phone}", use_container_width=True)
    else:
        st.error(result.error or "求助生成失败，请重试")

render_footer()
