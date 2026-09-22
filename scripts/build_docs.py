# -*- coding: utf-8 -*-
"""把作品简介与软件设计文档生成为 Word（.docx）格式。

用法：
    python scripts/build_docs.py

输出：
    docs/01_作品简介.docx
    docs/02_软件设计文档.docx
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
IMAGES = DOCS / "images"

ZH_BODY = "宋体"
ZH_HEAD = "微软雅黑"
EN_FONT = "Times New Roman"


# --------------------------------------------------------------------------- #
# 基础工具
# --------------------------------------------------------------------------- #
def set_font(run, zh=ZH_BODY, en=EN_FONT, size=12, bold=False, color=None):
    """设置中英文双字体与字号。"""
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set(qn("w:eastAsia"), zh)
    if color:
        run.font.color.rgb = RGBColor(*color)


def new_document():
    doc = Document()
    # 默认正文样式：宋体小四
    normal = doc.styles["Normal"]
    normal.font.name = ZH_BODY
    normal.font.size = Pt(12)
    normal._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), ZH_BODY)
    # 页边距
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.8)
    return doc


def add_title(doc, text, size=22):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, zh=ZH_HEAD, size=size, bold=True)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    return p


def add_subtitle(doc, text, size=14):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, zh=ZH_HEAD, size=size, bold=False)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    return p


def add_heading(doc, text, level=1):
    sizes = {1: 16, 2: 14, 3: 12}
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, zh=ZH_HEAD, size=sizes.get(level, 12), bold=True)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_para(doc, text, size=12, bold=False, indent=True, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, size=size, bold=bold)
    p.paragraph_format.line_spacing = 1.5
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    if align:
        p.alignment = align
    return p


def add_bullet(doc, text, size=12):
    p = doc.add_paragraph()
    run = p.add_run("• " + text)
    set_font(run, size=size)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.left_indent = Pt(18)
    return p


def add_numbered(doc, text, idx, size=12):
    p = doc.add_paragraph()
    run = p.add_run(f"{idx}. {text}")
    set_font(run, size=size)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.left_indent = Pt(18)
    return p


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = 1  # 居中
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_font(run, zh=ZH_HEAD, size=10.5, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row):
            cell = cells[i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(v)
            set_font(run, size=10.5)
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_code_block(doc, lines, size=10.5):
    for line in lines:
        p = doc.add_paragraph()
        run = p.add_run(line)
        set_font(run, zh=ZH_BODY, en="Consolas", size=size)
        p.paragraph_format.left_indent = Pt(18)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(0)


def add_image(doc, filename, caption, width_cm=13.5):
    path = IMAGES / filename
    if path.exists():
        doc.add_picture(str(path), width=Cm(width_cm))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph()
        run = cap.add_run(caption)
        set_font(run, size=10.5, bold=True)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(10)
    else:
        add_para(doc, f"[缺少截图：{filename}]", size=10.5, indent=False)


# --------------------------------------------------------------------------- #
# 01 作品简介
# --------------------------------------------------------------------------- #
def build_intro():
    doc = new_document()
    add_title(doc, "作品简介")
    add_subtitle(doc, "「瞳行」——面向视障群体的 AI 出行与生活辅助智能体")

    add_para(doc, "「瞳行」是一款面向视障群体的 AI 出行与生活辅助智能体。针对视障者出行中 GPS 导航终点与实际目的地之间的「最后十米」盲区——找不到具体入口、台阶、门牌——系统通过手机拍照，调用国产多模态大模型智谱 GLM-4V-Flash 识别台阶、障碍物、红绿灯、门牌等环境信息，再由大语言模型 GLM-4-Flash 结合多轮导航上下文生成简洁口语化指引，经 Edge-TTS 实时语音播报。")

    add_para(doc, "作品提供四大功能：连续导航（多轮上下文生成连贯指引）、环境识别（单次拍照即时播报）、文字朗读（识别招牌票据药品说明）、紧急求助（生成自救建议与求助喊话）。系统采用子智能体编排架构，将视觉识别、指引生成、语音合成、文字朗读、紧急求助拆分为五个职责单一的子智能体，由编排器统一调度，形成「拍照→识别→指引→播报」的完整流水线。")

    add_para(doc, "作品基于国产大模型与免费技术栈开发，具备低成本、易推广特点，致力于用 AI 技术为视障群体构建一条安全、可感知的出行通道。")

    # 核心功能截图
    add_heading(doc, "核心功能截图", level=2)
    add_image(doc, "nav.png", "图 1　连续导航功能截图")
    add_image(doc, "detect.png", "图 2　环境识别功能截图")
    add_image(doc, "help.png", "图 3　紧急求助功能截图")

    out = DOCS / "01_作品简介.docx"
    doc.save(str(out))
    print("已生成:", out)


# --------------------------------------------------------------------------- #
# 02 软件设计文档
# --------------------------------------------------------------------------- #
def build_design():
    doc = new_document()
    add_title(doc, "软件设计文档")
    add_subtitle(doc, "「瞳行」——面向视障群体的 AI 出行与生活辅助智能体")

    # 一、项目概述
    add_heading(doc, "一、项目概述", 1)
    add_para(doc, "「瞳行」是一款面向视障群体的 AI 出行与生活辅助智能体。作品以手机拍照为输入，通过大模型多模态识别与语音合成，解决视障者出行中 GPS 导航结束后「最后十米」找不到入口、台阶、门牌的痛点，并扩展文字朗读、紧急求助等生活辅助能力。")

    # 二、需求分析
    add_heading(doc, "二、需求分析", 1)
    add_heading(doc, "2.1 目标用户", 2)
    add_para(doc, "视障及低视力人群，以及需要「无视觉依赖」获取环境信息的老年用户。")
    add_heading(doc, "2.2 核心痛点", 2)
    add_para(doc, "GPS 导航只能把人「带到附近」，导航终点与实际目的地之间的「最后十米」是感知盲区：找不到单元门、台阶、药店入口、门牌号，是视障者迷路、跌倒、遇险的高发区。")
    add_heading(doc, "2.3 功能需求", 2)
    add_table(doc, ["编号", "功能", "说明"], [
        ["F1", "连续导航", "设定目的地后连续拍照，结合多轮上下文生成连贯语音指引"],
        ["F2", "环境识别", "单次拍照识别台阶/障碍物/红绿灯/斑马线/门牌并播报"],
        ["F3", "文字朗读", "识别招牌、票据、药品说明等文字并朗读"],
        ["F4", "紧急求助", "描述情况后生成自救建议、求助喊话、一键拨号"],
    ], widths=[2, 3, 9])
    add_heading(doc, "2.4 非功能需求", 2)
    add_bullet(doc, "可用性：手机端友好，大字体、高对比、大按钮，语音自动播报。")
    add_bullet(doc, "低成本：全部采用免费 API（国产 GLM + Edge-TTS）。")
    add_bullet(doc, "可部署：支持公网部署（Streamlit Cloud / 云服务器 / 容器）。")
    add_bullet(doc, "鲁棒性：API 未配置或调用失败时优雅降级，不崩溃。")

    # 三、总体设计思路
    add_heading(doc, "三、总体设计思路", 1)
    add_heading(doc, "3.1 系统架构（分层）", 2)
    add_para(doc, "系统采用前后端分离的分层架构，自上而下分为三层：", indent=False)
    add_bullet(doc, "前端层（Streamlit，手机端友好）：首页、连续导航、环境识别、文字朗读、紧急求助五个页面。")
    add_bullet(doc, "编排层（Orchestrator）：协调各子智能体、维护会话状态、串联「拍照→识别→指引→播报」流水线。")
    add_bullet(doc, "智能体层：视觉识别、指引生成、语音合成、文字朗读、紧急求助、会话记忆六个子智能体。")
    add_heading(doc, "3.2 子智能体编排", 2)
    add_para(doc, "系统采用子智能体架构，将复杂任务拆分为五个职责单一、可独立替换的子智能体：", indent=False)
    add_table(doc, ["子智能体", "模型/技术", "职责"], [
        ["VisionAgent", "GLM-4V-Flash", "图片 → 结构化环境 JSON"],
        ["GuidanceAgent", "GLM-4-Flash", "环境 + 历史 → 口语化指引"],
        ["OCRAgent", "GLM-4V-Flash", "图片 → 文字内容"],
        ["EmergencyAgent", "GLM-4-Flash", "情况 → 求助方案"],
        ["TTSAgent", "Edge-TTS", "文字 → 语音 MP3"],
    ], widths=[4, 4, 6])
    add_heading(doc, "3.3 核心数据流", 2)
    add_para(doc, "拍照 → VisionAgent（结构化环境）→ GuidanceAgent（结合多轮历史）→ TTSAgent（语音）→ 播报；其中 NavigationSession（会话记忆）反向为指引生成提供历史上下文。", indent=False)

    # 四、功能模块详细设计
    add_heading(doc, "四、功能模块详细设计", 1)
    add_heading(doc, "4.1 连续导航（F1）", 2)
    add_bullet(doc, "用户设定目的地，NavigationSession 记录出行目标与每轮「环境 + 指引」。")
    add_bullet(doc, "每轮拍照后，GuidanceAgent 携带最近 3 轮历史生成指引，避免重复、保持连贯。")
    add_bullet(doc, "更换目的地自动清空会话，支持「重新开始」。")
    add_heading(doc, "4.2 环境识别（F2）", 2)
    add_para(doc, "单次拍照 → VisionAgent 输出结构化 JSON（场景类型/障碍物/台阶/红绿灯/门牌/文字/安全建议）→ 指引 + 播报。", indent=False)
    add_heading(doc, "4.3 文字朗读（F3）", 2)
    add_para(doc, "拍照 → OCRAgent 提取全部文字（招牌/票据/药品说明）→ 大字号展示 + TTS 朗读。", indent=False)
    add_heading(doc, "4.4 紧急求助（F4）", 2)
    add_bullet(doc, "用户描述情况 → EmergencyAgent 输出严重程度/自救建议/求助喊话/通话话术。")
    add_bullet(doc, "前端大字广播（供路人查看）+ 语音播报 + 一键拨号（110/120/紧急联系人）。")

    # 五、关键技术
    add_heading(doc, "五、关键技术", 1)
    add_numbered(doc, "多模态环境识别：通过提示词约束 GLM-4V-Flash 输出结构化 JSON，鲁棒解析（兼容 markdown 包裹与纯文本退化）。", 1)
    add_numbered(doc, "多轮上下文管理：NavigationSession 保存出行全程记录，只取最近 3 轮喂给模型，兼顾连贯性与上下文长度。", 2)
    add_numbered(doc, "口语化指引生成：提示词工程约束「安全优先、30 字内、方位词、不重复」，temperature 0.5 兼顾自然度。", 3)
    add_numbered(doc, "异步语音合成：Edge-TTS 流式分片聚合为 MP3，前端以 base64 自动播放。", 4)

    # 六、工具与平台
    add_heading(doc, "六、工具与平台", 1)
    add_table(doc, ["类别", "技术", "版本"], [
        ["程序设计语言", "Python", "3.11.9"],
        ["前端框架", "Streamlit", "1.64.0"],
        ["视觉大模型", "智谱 GLM-4V-Flash", "免费"],
        ["文本大模型", "智谱 GLM-4-Flash", "免费"],
        ["语音合成", "Edge-TTS", "7.2.8"],
        ["HTTP 客户端", "requests", "2.34.2"],
        ["图像处理", "Pillow", "≥10.0.0"],
        ["配置管理", "python-dotenv", "1.2.3"],
    ], widths=[4, 6, 4])

    # 七、运行环境与部署
    add_heading(doc, "七、运行环境与部署", 1)
    add_heading(doc, "7.1 开发环境", 2)
    add_table(doc, ["项目", "说明"], [
        ["程序设计语言", "Python 3.11.9"],
        ["开发操作系统", "Windows 11"],
        ["开发工具", "Claude Code（Sonnet 4.6）、VS Code"],
        ["版本管理", "Git"],
    ], widths=[5, 9])
    add_heading(doc, "7.2 关键依赖及版本", 2)
    add_table(doc, ["依赖", "版本", "用途"], [
        ["Streamlit", "1.64.0", "前端框架"],
        ["requests", "2.34.2", "HTTP 客户端（调用智谱 API）"],
        ["edge-tts", "7.2.8", "语音合成"],
        ["Pillow", "≥10.0.0", "图像压缩/格式转换"],
        ["python-dotenv", "1.2.3", "配置加载"],
        ["qrcode", "≥7.4", "二维码生成"],
    ], widths=[4, 3, 7])
    add_heading(doc, "7.3 运行平台", 2)
    add_table(doc, ["平台", "说明"], [
        ["Streamlit Community Cloud", "免费托管，自动 HTTPS，手机拍照可用"],
        ["任意云服务器（阿里云/腾讯云等）", "Docker 或 systemd + Nginx 部署"],
        ["本地运行", "streamlit run app.py"],
    ], widths=[6, 8])
    add_heading(doc, "7.4 配置与启动", 2)
    add_code_block(doc, [
        "pip install -r requirements.txt",
        "cp .env.example .env   # 填入 ZHIPU_API_KEY",
        "streamlit run app.py",
    ])
    add_para(doc, "部署到公网的完整步骤见根目录 DEPLOY.md。本作品为跨平台 Web 应用，无需安装原生包，通过公网 URL 访问，按要求提供对应二维码；应用支持 PWA「添加到主屏幕」，可在移动终端获得类原生 App 的安装体验。", indent=False)
    add_heading(doc, "7.5 测试账号", 2)
    add_para(doc, "作品为免登录的 Web 应用，无需注册账号。评审时直接访问部署后的公网 URL 即可使用（若评审系统要求填写测试用户名/密码，可留空或填写「无需登录」）。", indent=False)

    # 八、测试
    add_heading(doc, "八、测试", 1)
    add_bullet(doc, "单元/冒烟测试：模块导入、JSON 提取、图片压缩、会话往返、TTS 真实调用、未配置 Key 降级均通过。")
    add_bullet(doc, "功能测试：环境识别、文字朗读、紧急求助云端 API 全链路联通。")

    # 九、AI 使用与原创声明
    add_heading(doc, "九、AI 使用与原创声明", 1)
    add_heading(doc, "9.1 运行期调用的 AI 大模型（作品核心能力）", 2)
    add_table(doc, ["AI 大模型 / 服务", "用途", "说明"], [
        ["智谱 GLM-4V-Flash", "多模态视觉识别（环境识别、文字提取）", "国产，免费"],
        ["智谱 GLM-4-Flash", "文本生成（语音指引、求助方案）", "国产，免费"],
        ["Edge-TTS（微软神经网络语音）", "语音合成（文字 → 中文语音）", "免费"],
    ], widths=[6, 5, 3])
    add_para(doc, "作品符合大赛「鼓励使用国产 AI 基础大模型、调用 AI 大模型 API」的要求，全部模型均为可免费调用的国产/免费服务。", indent=False)
    add_heading(doc, "9.2 AI 辅助开发工具", 2)
    add_table(doc, ["工具", "用途", "说明"], [
        ["Claude Code（Anthropic Sonnet 4.6）", "辅助编写与调试代码、生成文档", "开发辅助"],
    ], widths=[6, 5, 3])
    add_heading(doc, "9.3 AI 编写代码所占比例", 2)
    add_para(doc, "AI 辅助生成代码约占全项目代码的 55%。", indent=False)
    add_bullet(doc, "学生原创/主导部分：选题创意、需求分析、系统架构设计（子智能体编排）、提示词工程、无障碍前端设计、多轮会话机制、部署方案。")
    add_bullet(doc, "AI 辅助部分：代码实现细节、调试排错、文档润色。")
    add_heading(doc, "9.4 原创性说明", 2)
    add_numbered(doc, "本作品为原创，选题、需求与总体设计均为团队独立完成。", 1)
    add_numbered(doc, "未抄袭、未复用历年参赛作品、未参与过其他大赛。", 2)
    add_numbered(doc, "第三方开源库（Streamlit、requests、edge-tts、Pillow、python-dotenv）均为宽松开源协议，已在本文档中列明。", 3)
    add_numbered(doc, "作品中不涉及疆域地图，无需标注地图审图号。", 4)

    out = DOCS / "02_软件设计文档.docx"
    doc.save(str(out))
    print("已生成:", out)


if __name__ == "__main__":
    build_intro()
    build_design()
    print("完成。")
