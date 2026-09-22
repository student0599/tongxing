"""瞳行 —— 面向视障群体的 AI 出行与生活辅助智能体（主页）。

运行方式：streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from src.ui import (
    APP_ICON,
    APP_SUBTITLE,
    APP_TITLE,
    get_orchestrator,
    render_header,
    set_page,
    show_setup_banner,
)

set_page()

# ---------------- Hero 区 ----------------
render_header(f"{APP_ICON} {APP_TITLE}", APP_SUBTITLE, center=True)

# 配置状态提示
orch = get_orchestrator()
show_setup_banner(orch)

# ---------------- 功能卡片（2×2 网格） ----------------
features = [
    ("🚶", "连续导航", "拍照识别 + 语音指引，解决 GPS 导航终点「最后十米」的盲区", "pages/1_连续导航.py"),
    ("👁️", "环境识别", "单次拍照，识别台阶、障碍物、红绿灯、门牌", "pages/2_环境识别.py"),
    ("📖", "文字朗读", "识别招牌、票据、药品说明等文字并朗读", "pages/3_文字朗读.py"),
    ("🆘", "紧急求助", "一键生成求助播报、自救建议与联系电话", "pages/4_紧急求助.py"),
]

st.markdown("### 选择功能")

rows = [st.columns(2), st.columns(2)]
for idx, (icon, title, desc, page) in enumerate(features):
    col = rows[idx // 2][idx % 2]
    with col:
        with st.container(border=True):
            st.markdown(
                f'<div class="feat-icon">{icon}</div>'
                f'<div class="feat-title">{title}</div>'
                f'<div class="feat-desc">{desc}</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page, label="进入功能 →", use_container_width=True)

# ---------------- 创新亮点 ----------------
st.markdown("---")
st.markdown("### ✨ 创新亮点")
st.markdown(
    """
    <div class="hl-card">🎯 <b>精准切入「最后十米」盲区</b>——补全 GPS 导航与目的地之间无人告知的感知缺口。</div>
    <div class="hl-card">🧠 <b>多轮上下文连续导航</b>——记住已提醒内容，生成连贯、不重复的语音指引。</div>
    <div class="hl-card">🤖 <b>子智能体编排架构</b>——视觉识别 / 指引生成 / 语音合成等子智能体协同。</div>
    <div class="hl-card">🇨🇳 <b>国产大模型 + 免费技术栈</b>——GLM-4V-Flash / GLM-4-Flash / Edge-TTS，低成本易推广。</div>
    """,
    unsafe_allow_html=True,
)

# ---------------- 作品介绍入口 ----------------
st.page_link(
    "pages/5_作品介绍.py",
    label="🏆 查看完整作品介绍（选题背景 / 技术架构 / 创新点 / 应用案例）→",
    use_container_width=True,
)

# ---------------- 使用说明 / 技术说明 ----------------
st.markdown("---")

with st.expander("📋 使用说明"):
    st.markdown(
        """
        - **连续导航**：设定目的地后连续拍照，AI 会结合上下文给出连贯的语音指引。
        - **环境识别**：对当前环境拍一张照，立即识别并播报台阶、障碍物、红绿灯等。
        - **文字朗读**：拍下招牌、票据、药品说明，系统朗读文字内容。
        - **紧急求助**：描述突发情况，系统生成求助喊话与自救建议，并显示紧急联系电话。

        > 建议佩戴耳机，以获得更清晰的语音播报体验。
        """
    )

with st.expander("🔧 技术说明"):
    st.markdown(
        """
        - **前端**：Streamlit（手机端友好）
        - **视觉识别**：智谱 GLM-4V-Flash（免费）
        - **文本生成**：智谱 GLM-4-Flash（免费）
        - **语音合成**：Edge-TTS（免费中文语音）
        - **架构**：子智能体编排（视觉识别 / 指引生成 / 语音合成 / 文字朗读 / 紧急求助）
        """
    )
