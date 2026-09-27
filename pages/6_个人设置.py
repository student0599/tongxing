"""个人设置：自定义语音播报与紧急联系人。"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.agents.tts_agent import VOICES
from src.ui import get_orchestrator, render_audio, render_footer, render_header, set_page

set_page()
render_header("⚙️ 个人设置", "自定义语音播报与紧急联系人")

orch = get_orchestrator()

RATE_MAP = {"较慢": "-20%", "正常": "+0%", "较快": "+20%"}
RATE_REV = {v: k for k, v in RATE_MAP.items()}
VOLUME_MAP = {"较小": "-20%", "正常": "+0%", "较大": "+20%"}
VOLUME_REV = {v: k for k, v in VOLUME_MAP.items()}

# 读取当前设置
voice_keys = list(VOICES.keys())
current_label = next((k for k, v in VOICES.items() if v == orch.tts.voice), voice_keys[0])
rate_label = RATE_REV.get(orch.tts.rate, "正常")
volume_label = VOLUME_REV.get(orch.tts.volume, "正常")

# ---------------- 语音播报设置 ----------------
st.markdown("### 🔊 语音播报设置")
voice = st.selectbox("播报音色", voice_keys, index=voice_keys.index(current_label))
rate = st.select_slider("播报语速", list(RATE_MAP.keys()), value=rate_label)
volume = st.select_slider("播报音量", list(VOLUME_MAP.keys()), value=volume_label)

if st.button("🔊 试听当前音色", use_container_width=True):
    res = orch.tts.run("瞳行已就绪，请注意安全。", voice=VOICES[voice], rate=RATE_MAP[rate])
    if res.ok:
        render_audio(res.data)
    else:
        st.warning(res.error)

# ---------------- 紧急联系人设置 ----------------
st.markdown("### 📞 紧急联系人")
contact_name = st.text_input("联系人姓名", value=orch.config.emergency_contact_name)
contact_phone = st.text_input("联系人电话", value=orch.config.emergency_contact_phone)

# ---------------- 保存 ----------------
if st.button("💾 保存设置", type="primary", use_container_width=True):
    orch.tts.voice = VOICES[voice]
    orch.tts.rate = RATE_MAP[rate]
    orch.tts.volume = VOLUME_MAP[volume]
    orch.config.emergency_contact_name = contact_name.strip() or "家人"
    orch.config.emergency_contact_phone = contact_phone.strip()
    st.success("✅ 设置已保存，将在语音播报与紧急求助中生效")

render_footer()
