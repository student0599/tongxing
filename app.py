"""瞳行 —— 面向视障群体的 AI 出行与生活辅助智能体（主页）。

运行方式：streamlit run app.py
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from src.ui import get_orchestrator, set_page, show_setup_banner

set_page()

orch = get_orchestrator()

# 内嵌 logo（base64 数据 URI，避免 URL 引用失效）
_LOGO_B64 = base64.b64encode(Path("static/logo_small.png").read_bytes()).decode()

# ---------------- 顶部导航栏 ----------------
st.markdown(
    f"""
    <div class="topnav">
      <div class="brand">
        <span class="logo"><img src="data:image/png;base64,{_LOGO_B64}" width="24" style="vertical-align:-4px; border-radius:4px;"> 瞳行</span>
        <span class="slogan">AI 伴你同行 · 看见更好的自己</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 配置状态提示
show_setup_banner(orch)

# ---------------- 主横幅 ----------------
st.markdown(
    f"""
    <div class="hero-banner">
      <span class="hero-tag">✨ 面向视障群体的 AI 出行与生活辅助智能体</span>
      <h1><img src="data:image/png;base64,{_LOGO_B64}" width="46" style="vertical-align:-6px; border-radius:6px;"> 瞳行</h1>
      <div class="hero-sub">
        用科技点亮生活，让每一次出行都更安全、更便捷、更有温度。<br>
        手机拍照 + AI 识别 + 语音指引，解决视障出行的「最后十米」盲区。
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.page_link("pages/1_连续导航.py", label="🚀 开始使用", use_container_width=True)

# ---------------- 功能卡片（2×2 四色） ----------------
st.markdown("### 核心功能")

features = [
    ("🚶", "连续导航", "拍照识别 + 语音指引，解决 GPS 导航终点「最后十米」的盲区", "fcard-blue", "pages/1_连续导航.py"),
    ("👁️", "环境识别", "单次拍照，识别台阶、障碍物、红绿灯、门牌", "fcard-green", "pages/2_环境识别.py"),
    ("📖", "文字朗读", "识别招牌、票据、药品说明等文字并朗读", "fcard-purple", "pages/3_文字朗读.py"),
    ("🆘", "紧急求助", "语音描述情况，生成求助播报与自救建议", "fcard-red", "pages/4_紧急求助.py"),
]

rows = [st.columns(2), st.columns(2)]
for idx, (icon, title, desc, color, page) in enumerate(features):
    col = rows[idx // 2][idx % 2]
    with col:
        st.markdown(
            f'<div class="fcard {color}"><div class="ficon">{icon}</div>'
            f'<div class="ftitle">{title}</div><div class="fdesc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label="进入功能 →", use_container_width=True)

# ---------------- 作品介绍 / 使用说明 ----------------
st.page_link(
    "pages/5_作品介绍.py",
    label="🏆 查看完整作品介绍（选题背景 / 技术架构 / 创新点 / 应用案例）",
    use_container_width=True,
)

st.markdown("---")

with st.expander("📋 使用说明"):
    st.markdown(
        """
        - **连续导航**：语音说出目的地，连续拍照，AI 结合上下文给出连贯语音指引。
        - **环境识别**：对当前环境拍一张照，立即识别并播报台阶、障碍物、红绿灯等。
        - **文字朗读**：拍下招牌、票据、药品说明，系统朗读文字内容。
        - **紧急求助**：语音描述突发情况，系统生成求助喊话与自救建议，并显示紧急联系电话。

        > 建议佩戴耳机，以获得更清晰的语音播报体验。
        """
    )

with st.expander("🔧 技术说明"):
    st.markdown(
        """
        - **前端**：Streamlit（手机端友好）
        - **视觉识别**：智谱 GLM-4V-Flash（免费）
        - **文本生成**：智谱 GLM-4-Flash（免费）
        - **语音识别**：智谱 GLM-ASR（免费）
        - **语音合成**：Edge-TTS（免费中文语音）
        - **架构**：子智能体编排（视觉识别 / 指引生成 / 语音合成 / 文字朗读 / 紧急求助）
        """
    )
