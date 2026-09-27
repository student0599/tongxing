"""Streamlit 前端共享工具。

集中处理：编排器缓存、设计系统样式注入、统一页头/页脚、
图片来源选择、语音自动播报、配置提示等，避免各页面重复代码。
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from src.config import load_config
from src.orchestrator import Orchestrator
from src.utils import autoplay_audio_html

APP_TITLE = "瞳行"
APP_ICON = "👁️"
APP_SUBTITLE = "面向视障群体的 AI 出行与生活辅助智能体"

# =============================================================================
# 设计系统：靛蓝主色 + 暖金点缀，高对比、低饱和、留白规整
# =============================================================================
_CSS = """
<style>
:root {
  --primary: #4F46E5;
  --primary-dark: #4338CA;
  --accent: #F59E0B;
  --bg-start: #EAFCF7;
  --bg-mid: #C9F0E8;
  --bg-end: #BCE8F2;
  --surface: #FFFFFF;
  --text: #1E293B;
  --muted: #64748B;
  --border: #E2E8F0;
  --danger: #DC2626;
}

/* ---------- 全局背景：宣纸白（暖白） ---------- */
html, body {
  background-color: #FAF3E1;
}
[data-testid="stAppViewContainer"] {
  background-color: #FAF3E1;
  background-image: linear-gradient(160deg, #FBF5E6 0%, #FAF3E1 50%, #F5EDD9 100%);
  background-attachment: fixed;
  min-height: 100vh;
}
[data-testid="stHeader"] {
  background: transparent;
}
html, body, [data-testid="stAppViewContainer"] {
  font-size: 18px;
  color: var(--text);
}

/* ---------- 标题层级 ---------- */
[data-testid="stAppViewContainer"] h1 {
  font-size: 2rem !important;
  font-weight: 800 !important;
  letter-spacing: -0.01em;
  color: var(--text) !important;
  line-height: 1.3;
}
[data-testid="stAppViewContainer"] h2 {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
}
[data-testid="stAppViewContainer"] h3 {
  font-size: 1.2rem !important;
  font-weight: 700 !important;
}

/* ---------- 说明文字 ---------- */
[data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
  font-size: 1rem !important;
}

/* ---------- 分隔线 ---------- */
[data-testid="stAppViewContainer"] hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1.2rem 0;
}

/* ---------- 主按钮（靛蓝渐变） ---------- */
.stButton > button {
  font-size: 1.15rem !important;
  font-weight: 700 !important;
  padding: 0.7rem 1.1rem !important;
  min-height: 3rem !important;
  border-radius: 0.7rem !important;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.28);
  transition: transform .08s ease, box-shadow .15s ease;
}
.stButton > button:hover {
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.40);
  transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
  background: var(--surface) !important;
  color: var(--primary) !important;
  border: 1.5px solid var(--primary) !important;
  box-shadow: none !important;
}

/* ---------- 链接按钮 ---------- */
[data-testid="stLinkButton"] a {
  border-radius: 0.7rem !important;
  font-weight: 700 !important;
  font-size: 1.05rem !important;
}
[data-testid="stLinkButton"] a[kind="primary"] {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
  color: #ffffff !important;
}

/* ---------- 输入控件 ---------- */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  font-size: 1.15rem !important;
  border-radius: 0.6rem !important;
}

/* ---------- 带边框卡片容器（st.container(border=True)） ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 0.9rem !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  background: var(--surface);
}

/* ---------- 自定义卡片 ---------- */
.kv-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.8rem;
  padding: 0.9rem 1.1rem;
  margin: 0.4rem 0;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  line-height: 1.6;
}

/* ---------- 语音播报文本（核心输出，醒目） ---------- */
.speech-big {
  font-size: 1.5rem !important;
  font-weight: 700;
  line-height: 1.65;
  background: var(--surface);
  border-left: 5px solid var(--primary);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
  color: var(--text);
  padding: 1.1rem 1.3rem;
  border-radius: 0.8rem;
  margin: 0.6rem 0;
}

/* ---------- 求助广播（红底白字） ---------- */
.broadcast-big {
  font-size: 1.9rem !important;
  font-weight: 900;
  color: #ffffff;
  background: linear-gradient(135deg, #DC2626, #B91C1C);
  padding: 1.4rem;
  border-radius: 0.9rem;
  text-align: center;
  line-height: 1.7;
  margin: 0.6rem 0;
}

/* ---------- 首页 Hero ---------- */
.hero {
  text-align: center;
  padding: 1.4rem 0 0.6rem;
}
.hero h1 {
  font-size: 2.5rem !important;
  margin-bottom: 0.5rem;
}
.hero .hero-sub {
  color: var(--muted);
  font-size: 1.05rem;
  margin: 0;
}
.hero .hero-rule {
  width: 64px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  margin: 1rem auto 0;
}

/* ---------- 功能卡片内图标 ---------- */
.feat-icon { font-size: 1.9rem; line-height: 1; margin-bottom: 0.2rem; }
.feat-title { font-size: 1.2rem; font-weight: 800; color: var(--text); margin: 0.2rem 0; }
.feat-desc { color: var(--muted); font-size: 0.95rem; line-height: 1.5; margin: 0.3rem 0 0.8rem; }

/* ---------- 智能体架构流程图 ---------- */
.arch-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
  margin: 0.5rem 0;
}
.arch-box {
  background: var(--surface);
  border: 1.5px solid var(--primary);
  border-radius: 0.7rem;
  padding: 0.5rem 0.8rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text);
  text-align: center;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.06);
}
.arch-box .sub {
  display: block;
  font-weight: 500;
  font-size: 0.76rem;
  color: var(--muted);
  margin-top: 0.1rem;
}
.arch-arrow {
  color: var(--accent);
  font-weight: 800;
  font-size: 1.25rem;
  line-height: 1;
}

/* ---------- 标签 ---------- */
.tag {
  display: inline-block;
  background: #EEF2FF;
  color: var(--primary);
  border-radius: 999px;
  padding: 0.18rem 0.7rem;
  font-size: 0.85rem;
  font-weight: 700;
  margin: 0.15rem 0.3rem 0.15rem 0;
}
.tag-gold { background: #FEF3C7; color: #92400E; }
.tag-green { background: #D1FAE5; color: #065F46; }

/* ---------- 创新点 / 亮点卡片 ---------- */
.hl-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.85rem;
  padding: 0.85rem 1.05rem;
  margin: 0.5rem 0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  line-height: 1.6;
}
.hl-card b { color: var(--primary); }

/* ---------- 顶部导航栏 ---------- */
.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 1rem;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 0.9rem;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.07);
  margin-bottom: 1rem;
}
.topnav .brand { display: flex; align-items: baseline; gap: 0.55rem; }
.topnav .logo { font-size: 1.35rem; font-weight: 800; color: var(--primary); }
.topnav .slogan { font-size: 0.85rem; color: var(--muted); }

/* ---------- 主横幅 ---------- */
.hero-banner {
  background: linear-gradient(130deg, #0D9488 0%, #14B8A6 55%, #06B6D4 100%);
  border-radius: 1.2rem;
  padding: 2rem 2.1rem;
  color: #fff;
  margin-bottom: 0.9rem;
  box-shadow: 0 10px 28px rgba(13, 148, 136, 0.28);
}
.hero-banner h1 { color: #fff !important; font-size: 2.3rem !important; margin: 0 0 0.5rem; line-height: 1.2; }
.hero-banner .hero-tag {
  display: inline-block;
  background: rgba(255, 255, 255, 0.22);
  color: #fff;
  border-radius: 999px;
  padding: 0.22rem 0.85rem;
  font-size: 0.85rem;
  margin-bottom: 0.9rem;
}
.hero-banner .hero-sub { color: rgba(255, 255, 255, 0.96); font-size: 1.02rem; line-height: 1.65; margin: 0; }

/* ---------- 功能卡片（四色） ---------- */
.fcard {
  border-radius: 0.9rem;
  padding: 1rem 1.1rem;
  margin: 0.3rem 0 0.55rem;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
  min-height: 8.2rem;
}
.fcard .ficon { font-size: 1.9rem; line-height: 1; }
.fcard .ftitle { font-size: 1.15rem; font-weight: 800; color: var(--text); margin: 0.4rem 0 0.25rem; }
.fcard .fdesc { font-size: 0.9rem; line-height: 1.5; color: var(--text); margin: 0; }
.fcard-blue { background: #E3EDFF; }
.fcard-green { background: #DBF5E8; }
.fcard-purple { background: #ECE6FF; }
.fcard-red { background: #FFE3E3; }

/* ---------- 侧边栏（鸢尾蓝） ---------- */
[data-testid="stSidebar"] {
  background: #1561AD;
  border-right: 1px solid rgba(255, 255, 255, 0.12);
}
.side-brand { font-size: 1.35rem; font-weight: 800; color: #ffffff; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: rgba(255, 255, 255, 0.82) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong { color: #ffffff !important; }
[data-testid="stSidebar"] [data-testid="stLinkButton"] a {
  background: rgba(255, 255, 255, 0.16) !important;
  color: #ffffff !important;
  border: none !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.25) !important; }
</style>
"""


def inject_styles() -> None:
    """注入全局设计系统样式。"""
    st.markdown(_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_orchestrator() -> Orchestrator:
    """获取全局编排器单例（跨页面、跨 rerun 复用）。"""
    return Orchestrator(load_config())


def render_audio(audio: Optional[bytes]) -> None:
    """若存在音频则自动播放。"""
    if audio:
        st.markdown(autoplay_audio_html(audio), unsafe_allow_html=True)


def show_setup_banner(orch: Orchestrator) -> bool:
    """展示配置状态；返回是否已就绪。"""
    if orch.ready:
        return True
    st.error(
        "⚠️ 尚未配置智谱 AI API Key。\n\n"
        "请复制 `.env.example` 为 `.env`，填入 `ZHIPU_API_KEY`（获取地址：https://open.bigmodel.cn）。"
    )
    return False


def render_header(title: str, subtitle: str = "", center: bool = False) -> None:
    """统一页头：标题 + 副标题 + 分隔线。"""
    if center:
        st.markdown(
            f'<div class="hero"><h1>{title}</h1>'
            f'<p class="hero-sub">{subtitle}</p>'
            f'<div class="hero-rule"></div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.title(title)
        if subtitle:
            st.caption(subtitle)
        st.markdown("---")


def render_footer() -> None:
    """统一页脚：居中的返回首页链接。"""
    st.markdown("---")
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.page_link("app.py", label="🏠 返回首页", use_container_width=True)


def get_image_input(label: str = "拍照（对准前方环境）") -> Optional[bytes]:
    """统一的图片来源选择器（拍照 / 上传），返回图片字节或 None。"""
    source = st.radio(
        "图片来源",
        ["📷 拍照", "🖼️ 上传图片"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if source == "📷 拍照":
        return rear_camera_input(label)
    upload = st.file_uploader("上传一张照片", type=["jpg", "jpeg", "png"])
    return upload.getvalue() if upload is not None else None


# PWA 元信息：通过 JS 注入 <head>，使应用可被「添加到主屏幕」（移动端可安装）。
_PWA_HTML = """
<script>
(function () {
  var BASE = "/app/static/";
  function mk(tag, attrs) {
    var el = document.createElement(tag);
    for (var k in attrs) { el.setAttribute(k, attrs[k]); }
    document.head.appendChild(el);
  }
  mk("link", {rel: "manifest", href: BASE + "manifest.webmanifest"});
  mk("link", {rel: "apple-touch-icon", href: BASE + "icon-180.png"});
  mk("meta", {name: "theme-color", content: "#0D9488"});
  mk("meta", {name: "apple-mobile-web-app-capable", content: "yes"});
  mk("meta", {name: "apple-mobile-web-app-status-bar-style", content: "default"});
})();
</script>
"""


def inject_pwa() -> None:
    """注入 PWA 元信息，使应用可被「添加到主屏幕」（移动端可安装）。"""
    st.markdown(_PWA_HTML, unsafe_allow_html=True)


def rear_camera_input(label: str = "拍照（对准前方环境）") -> Optional[bytes]:
    """拍照（st.camera_input 原生组件）。"""
    shot = st.camera_input(label)
    return shot.getvalue() if shot is not None else None


def render_sidebar() -> None:
    """左侧导航侧边栏：首页 / 功能中心 / 个人中心。"""
    with st.sidebar:
        st.image("static/logo.png", width=88)
        st.markdown('<div class="side-brand">👁️ 瞳行</div>', unsafe_allow_html=True)
        st.caption("AI 伴你同行 · 看见更好的自己")
        st.markdown("---")
        st.page_link("app.py", label="🏠 首页", use_container_width=True)
        st.markdown("**🧩 功能中心**")
        st.page_link("pages/1_连续导航.py", label="🚶 连续导航", use_container_width=True)
        st.page_link("pages/2_环境识别.py", label="👁️ 环境识别", use_container_width=True)
        st.page_link("pages/3_文字朗读.py", label="📖 文字朗读", use_container_width=True)
        st.page_link("pages/4_紧急求助.py", label="🆘 紧急求助", use_container_width=True)
        st.markdown("**👤 个人中心**")
        st.page_link("pages/6_个人设置.py", label="⚙️ 个人设置", use_container_width=True)
        st.page_link("pages/5_作品介绍.py", label="🏆 作品介绍", use_container_width=True)
        st.markdown("---")
        st.caption("面向视障群体的 AI 出行与生活辅助智能体")


def set_page() -> None:
    """统一页面配置（须作为每个脚本的首个 Streamlit 命令调用）。"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="centered",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    inject_pwa()
    render_sidebar()
