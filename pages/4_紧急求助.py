"""紧急求助：描述情况，生成自救建议、求助喊话与紧急联系电话。"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui import get_orchestrator, render_audio, render_footer, render_header, set_page

set_page()
render_header("🆘 紧急求助", "遇到困难时，快速生成求助信息并联系紧急联系人")

orch = get_orchestrator()

# ---------------- 常用情况快捷按钮 ----------------
if "em_situation" not in st.session_state:
    st.session_state.em_situation = ""

st.markdown("**快捷选择**")
c1, c2, c3, c4 = st.columns(4)
if c1.button("🩹 跌倒"):
    st.session_state.em_situation = "我不小心跌倒了，站不起来。"
if c2.button("🧭 迷路"):
    st.session_state.em_situation = "我迷路了，找不到方向。"
if c3.button("🤒 身体不适"):
    st.session_state.em_situation = "我突然身体不舒服，需要帮助。"
if c4.button("⚠️ 危险"):
    st.session_state.em_situation = "我遇到了危险，请帮帮我。"

situation = st.text_area(
    "请描述您遇到的情况",
    key="em_situation",
    placeholder="例如：我在XX路附近跌倒了，膝盖很疼……",
    height=100,
)
location = st.text_input("📍 您的大致位置（可选）", placeholder="例如：中山路与人民路交叉口")

if st.button("🆘 生成求助信息", type="primary", use_container_width=True):
    if not situation.strip():
        st.warning("请先描述您遇到的情况")
    else:
        with st.spinner("正在生成求助方案……"):
            result = orch.handle_emergency(situation.strip(), location.strip())

        if result.ok and result.info:
            info = result.info
            # 1. 面向路人的求助播报（大字 + 语音）
            st.markdown(f'<div class="broadcast-big">{info.get("broadcast", "请帮帮我！")}</div>', unsafe_allow_html=True)
            render_audio(result.audio)

            # 2. 严重程度与建议
            sev = info.get("severity", "高")
            st.markdown(f"**危险程度：{sev}　|　类型：{info.get('category', '')}**")
            if info.get("advice"):
                st.markdown(f'<div class="kv-card">💡 自救建议：{info["advice"]}</div>', unsafe_allow_html=True)
            if info.get("call_message"):
                st.markdown(f'<div class="kv-card">📞 求助话术：{info["call_message"]}</div>', unsafe_allow_html=True)

            # 3. 紧急电话
            st.markdown("#### ☎️ 紧急电话（点击拨打）")
            p1, p2 = st.columns(2)
            p1.link_button("🚨 报警 110", "tel:110", use_container_width=True)
            p2.link_button("🚑 急救 120", "tel:120", use_container_width=True)

            # 4. 紧急联系人
            contact_name = orch.config.emergency_contact_name
            contact_phone = orch.config.emergency_contact_phone
            if contact_phone:
                st.link_button(
                    f"👤 联系 {contact_name}",
                    f"tel:{contact_phone}",
                    use_container_width=True,
                )
            else:
                st.info("可在 `.env` 中配置 `EMERGENCY_CONTACT_NAME` 与 `EMERGENCY_CONTACT_PHONE`，一键拨打紧急联系人。")
        else:
            st.error(result.error or "求助生成失败，请重试")

render_footer()
