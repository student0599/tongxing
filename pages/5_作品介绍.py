"""作品介绍（评审页）：选题背景、痛点、技术方案、架构、创新点、应用案例。

面向大赛评审的集中展示页，对应方向一「大模型与智能应用赛道」的
选题创意、软件设计、创新能力等考察点。
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui import render_footer, render_header, set_page

set_page()
render_header("🏆 作品介绍", "面向视障群体的 AI 出行与生活辅助智能体")

# ---------------- 一句话定位 ----------------
st.markdown(
    '<div class="speech-big">手机拍照 → AI 多模态识别 → 口语化语音指引，'
    "解决视障者出行「最后十米」的盲区。</div>",
    unsafe_allow_html=True,
)

# ---------------- 选题背景与痛点 ----------------
st.markdown("### 🎯 选题背景与痛点")
st.markdown(
    """
    我国视障群体超过 **1700 万**，日常出行高度依赖盲杖与导航 App。但 GPS 导航只能把人
    「带到附近」，导航终点与实际目的地之间普遍存在 **「最后十米」盲区**——找不到具体的
    单元门、台阶、药店入口、门牌号。这段盲区恰恰是视障者最容易迷路、跌倒、发生危险的区域。

    **核心痛点**：导航结束后，「该往哪走、脚下有什么、门在哪里」无人告知。
    """
)

# ---------------- 解决方案 ----------------
st.markdown("### 💡 解决方案")
st.markdown(
    """
    「瞳行」以**手机拍照 + 大模型识别 + 语音指引**重构视障者的最后十米：
    用户举起手机拍照，系统调用多模态大模型识别台阶、障碍物、红绿灯、门牌等环境信息，
    再由大语言模型结合多轮导航上下文生成一句口语化指引，经 TTS 实时语音播报。
    """
)

# ---------------- 技术架构（子智能体编排） ----------------
st.markdown("### 🧬 技术架构：子智能体编排")
st.markdown("系统将复杂任务拆分为**职责单一、可独立替换的子智能体**，由编排器统一调度：")
st.markdown(
    """
    <div class="arch-row">
      <div class="arch-box">📷 拍照<span class="sub">手机摄像头</span></div>
      <div class="arch-arrow">→</div>
      <div class="arch-box">👁️ 视觉识别<span class="sub">GLM-4V-Flash</span></div>
      <div class="arch-arrow">→</div>
      <div class="arch-box">🧭 指引生成<span class="sub">GLM-4-Flash</span></div>
      <div class="arch-arrow">→</div>
      <div class="arch-box">🔊 语音合成<span class="sub">Edge-TTS</span></div>
      <div class="arch-arrow">→</div>
      <div class="arch-box">🎧 语音播报<span class="sub">实时引导</span></div>
    </div>
    <div class="arch-row">
      <div class="arch-box">📖 文字朗读<span class="sub">GLM-4V-Flash</span></div>
      <div class="arch-box">🆘 紧急求助<span class="sub">GLM-4-Flash</span></div>
      <div class="arch-box">🧠 会话记忆<span class="sub">多轮上下文</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- 核心功能 ----------------
st.markdown("### 🧩 核心功能")
st.markdown(
    """
    - **🚶 连续导航**：设定目的地后连续拍照，结合多轮上下文生成连贯、不重复的语音指引（旗舰功能）。
    - **👁️ 环境识别**：单次拍照即时识别台阶、障碍物、红绿灯、斑马线、门牌并播报。
    - **📖 文字朗读**：识别招牌、票据、药品说明等文字并朗读。
    - **🆘 紧急求助**：描述突发情况，生成自救建议、面向路人的求助喊话与一键拨号。
    """
)

# ---------------- 创新点 ----------------
st.markdown("### ✨ 创新点")
st.markdown(
    """
    <div class="hl-card">🎯 <b>精准切入「最后十米」盲区</b>——补全 GPS 导航与真实目的地之间的感知缺口，选题切口小、社会价值高。</div>
    <div class="hl-card">🧠 <b>多轮上下文连续导航</b>——通过会话记忆记住「已提醒过什么」，生成连贯、不重复的语音指引，而非单次孤立识别。</div>
    <div class="hl-card">🤖 <b>子智能体编排架构</b>——视觉识别 / 指引生成 / 语音合成 / 文字朗读 / 紧急求助五个子智能体职责单一、可独立替换。</div>
    <div class="hl-card">🇨🇳 <b>国产大模型 + 免费技术栈</b>——智谱 GLM-4V-Flash / GLM-4-Flash + Edge-TTS，低成本、易推广、具备落地普惠性。</div>
    """,
    unsafe_allow_html=True,
)

# ---------------- 技术栈 ----------------
st.markdown("### 🛠️ 技术栈")
st.markdown(
    """
    | 模块 | 技术 | 说明 |
    | --- | --- | --- |
    | 前端 | Streamlit | 手机端友好、无障碍大字体 |
    | 视觉识别 | 智谱 GLM-4V-Flash | 国产、免费 |
    | 文本生成 | 智谱 GLM-4-Flash | 国产、免费 |
    | 语音合成 | Edge-TTS | 免费中文神经网络语音 |
    | 架构 | 子智能体编排 | 五子智能体 + 编排器 |
    | 开发语言 | Python 3.11 | — |
    """
)

# ---------------- 应用案例 ----------------
st.markdown("### 📚 应用案例")
st.markdown(
    """
    **案例一 · 前往药店取药**：导航把用户带到药店附近后，系统通过连续拍照指引
    「前方三米有台阶，请慢行」→「台阶已通过，右前方就是药店门口」→「门口在右侧，已到达」。

    **案例二 · 识别公交站牌**：视障者难以看清站牌线路信息，拍照后系统朗读
    「本站为中山路站，停靠 5 路、12 路、28 路」。

    **案例三 · 突发跌倒求助**：用户描述「我跌倒了」，系统立即生成并大声播报求助喊话，
    同时显示大字求助信息与一键拨号，便于路人施救。
    """
)

# ---------------- 社会价值 ----------------
st.markdown("### ❤️ 社会价值与展望")
st.markdown(
    """
    作品以无障碍公益为出发点，用低成本国产大模型为视障群体构建一条「安全、可感知」的出行通道。
    未来可扩展接入实时地图 API 与障碍物距离估计，进一步覆盖室内导航、公交出行等场景。
    """
)

render_footer()
