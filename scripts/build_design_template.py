# -*- coding: utf-8 -*-
"""按官方模板《设计文档模板-2026年.doc》生成瞳行的软件设计文档（Word，丰富版）。

结构：封面 → 知识产权声明 → 目录 → 七个章节（内容按软件工程要求详实展开）。
用法：python scripts/build_design_template.py
输出：docs/02_软件设计文档.docx
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_docs import (  # noqa: E402
    DOCS,
    add_bullet,
    add_heading,
    add_image,
    add_numbered,
    add_para,
    add_table,
    new_document,
    set_font,
)


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def add_center(doc, text, size=16, bold=False, space_after=6, space_before=0):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_font(run, zh="微软雅黑", size=size, bold=bold)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    return p


def blank(doc, n=1):
    for _ in range(n):
        doc.add_paragraph()


# --------------------------------------------------------------------------- #
# 封面
# --------------------------------------------------------------------------- #
def build_cover(doc):
    blank(doc, 5)
    add_center(doc, "2026年华北五省（市、自治区）及港澳台大学生", size=18, bold=True)
    add_center(doc, "计算机应用大赛　移动互联网应用创新", size=18, bold=True)
    add_center(doc, "移动互联网应用程序开发", size=18, bold=True)
    blank(doc, 4)
    add_center(doc, "【项目名称】　瞳行", size=22, bold=True)
    add_center(doc, "（视障出行 AI 辅助智能体 · Web 应用）", size=14)
    blank(doc, 4)
    for line in ["所在赛区：", "所在学校：", "团队名称：", "团队成员：", "提交日期："]:
        add_para(doc, line, size=14, indent=False)
    add_page_break(doc)


# --------------------------------------------------------------------------- #
# 知识产权声明
# --------------------------------------------------------------------------- #
def build_declaration(doc):
    add_center(doc, "参赛作品知识产权声明", size=18, bold=True, space_after=12)
    add_para(doc, "参赛作品名称：瞳行　（下称该作品）", indent=False)
    add_para(doc, "本小组全体成员，就该作品声明如下：", indent=False)
    add_para(doc, "1、该作品（含提交参赛的 App 应用、相关文档和介绍视频）是本小组成员的原创研究成果，不存在侵犯任何他人知识产权、涉及泄密或违反中华人民共和国法律法规的情形，且未在 2025 年＿＿月＿＿日前公开发布。", indent=False)
    add_para(doc, "2、我们确认：该作品知识产权归本小组成员所有，且签署本声明的人员能够代表全体小组成员的意愿。", indent=False)
    add_para(doc, "3、我们承诺：将仅由本小组成员参加大赛答辩。", indent=False)
    add_para(doc, "4、大赛举办方为宣传大赛、推广参赛作品，以及为未来各届大赛的参赛选手提供参考等非盈利目的，可能需要以下列形式使用参赛作品，就此我们确认：", indent=False)
    add_para(doc, "（1）□同意　□不同意：将参赛作品的相关文档结集出版（含公开发行）；", indent=False)
    add_para(doc, "（2）□同意　□不同意：在相关网站（包括大赛官网及含优酷等第三方视频平台网站）上传和播放介绍视频或幻灯片；", indent=False)
    add_para(doc, "（3）□同意　□不同意：在大赛官方网站提供 App 应用免费下载；", indent=False)
    add_para(doc, "（4）作出上述许可，同样不违反本声明第 1 款的要求。", indent=False)
    blank(doc, 1)
    add_para(doc, "作品小组全体成员", indent=False)
    add_para(doc, "日期：2026 年＿＿月＿＿日", indent=False)
    add_page_break(doc)


# --------------------------------------------------------------------------- #
# 目录
# --------------------------------------------------------------------------- #
def build_toc(doc):
    add_center(doc, "目　录", size=18, bold=True, space_after=12)
    toc = [
        ("一、作品概述", 0),
        ("二、作品可行性分析和目标群体", 0),
        ("　　（1）可行性分析", 1),
        ("　　（2）目标群体", 1),
        ("三、作品功能与原型设计", 0),
        ("　　（1）功能概述", 1),
        ("　　（2）原型设计", 1),
        ("四、作品实现、难点及特色分析", 0),
        ("　　（1）作品实现及难点", 1),
        ("　　（2）特色分析", 1),
        ("五、团队介绍和人员分工", 0),
        ("六、其他", 0),
        ("七、致谢", 0),
    ]
    for text, level in toc:
        p = doc.add_paragraph()
        run = p.add_run(text)
        set_font(run, size=13 if level == 0 else 12, bold=(level == 0))
        p.paragraph_format.space_after = Pt(3)
    add_page_break(doc)


# --------------------------------------------------------------------------- #
# 正文
# --------------------------------------------------------------------------- #
def build_body(doc):
    # ===================== 一、作品概述 =====================
    add_heading(doc, "一、作品概述", 1)
    add_para(doc, "我国视障人口超过 1700 万，是世界上视障人数最多的国家之一。视障群体的日常出行高度依赖盲杖、导盲犬与手机导航 App。然而，现有 GPS 导航只能把人「带到附近」，导航终点与实际目的地之间普遍存在一段「最后十米」的感知盲区——找不到具体的单元门、台阶、药店入口、门牌号。这段盲区恰恰是视障者迷路、跌倒、遇险的高发区。")
    add_para(doc, "《“十四五”残疾人保障和发展规划》明确提出加快无障碍环境建设，国家「人工智能+」行动持续推进人工智能赋能民生领域。用 AI 技术为视障群体补齐「最后十米」的感知缺口，既是技术可行的创新方向，也是具有显著社会价值的公益需求。基于此，我们确定开发「瞳行」——一款面向视障群体的 AI 出行与生活辅助智能体。")
    add_para(doc, "「瞳行」的一句话定位是：用手机拍照 + AI 识别 + 语音指引，解决视障者出行中 GPS 导航结束后「最后十米」找不到具体入口、台阶、门牌的痛点，并扩展至文字朗读、紧急求助等生活辅助功能。系统以手机拍照为输入，调用国产多模态大模型智谱 GLM-4V-Flash 识别台阶、障碍物、红绿灯、门牌等环境信息，再由大语言模型 GLM-4-Flash 结合多轮导航上下文生成简洁口语化指引，经 Edge-TTS 实时语音播报。")
    add_para(doc, "作品提供连续导航、环境识别、文字朗读、紧急求助四大功能，采用子智能体编排架构，将复杂任务拆分为视觉识别、指引生成、语音合成、文字朗读、紧急求助五个职责单一的子智能体统一调度。作品全部采用国产大模型与免费技术栈，边际成本接近零，具备低成本、易推广的特点，致力于用 AI 技术为视障群体构建一条安全、可感知的出行通道。")

    # ===================== 二、作品可行性分析和目标群体 =====================
    add_heading(doc, "二、作品可行性分析和目标群体", 1)
    add_heading(doc, "（1）可行性分析", 2)
    add_para(doc, "从技术可行性分析：作品基于成熟的 Python 3.11 + Streamlit 1.64 技术栈；视觉识别与文本生成调用国产智谱 GLM-4V-Flash / GLM-4-Flash 大模型 API（免费、不限 Token），语音合成采用 Edge-TTS 神经网络语音（免费）。上述技术均为稳定、成熟的云端服务，具备完善的 API 文档与社区支持，技术路线成熟可行。经过端到端实测，环境识别、文字朗读、紧急求助全链路均可稳定运行。")
    add_para(doc, "从操作可行性分析：视障用户无需复杂学习，只需「举起手机拍照」即可获得语音播报；应用采用大字体、高对比、大按钮的无障碍设计，并支持 PWA「添加到主屏幕」，像原生 App 一样一键打开。对于完全不熟悉智能手机操作的用户，也可由家人协助拍照，操作门槛低，可行性高。")
    add_para(doc, "从经济可行性分析：视觉识别、文本生成、语音合成全部采用免费 API，服务端可部署于免费托管平台（Streamlit Community Cloud），开发与运行边际成本接近零，具备大规模推广的经济可行性，尤其适合向欠发达地区与公益机构普及。")
    add_heading(doc, "（2）目标群体", 2)
    add_para(doc, "「瞳行」面向的主要是视障及低视力人群，以及需要「无视觉依赖」获取环境信息的老年用户。通过调研，其需求特征如下：")
    add_numbered(doc, "依赖语音与触觉获取信息：因此系统以「语音播报」为核心交互，辅以大字号、高对比文字供低视力用户阅读；", 1)
    add_numbered(doc, "出行最大不确定性在于「脚下与前方」：因此系统聚焦台阶、障碍物、红绿灯、斑马线、门牌等关键环境要素的识别与提醒；", 2)
    add_numbered(doc, "需要即时求助能力：突发跌倒、迷路时难以自行求助，因此系统提供紧急求助功能，一键生成求助喊话与拨号。", 3)

    # ===================== 三、作品功能与原型设计 =====================
    add_heading(doc, "三、作品功能与原型设计", 1)
    add_heading(doc, "（1）功能概述", 2)
    add_para(doc, "作品共设计四大核心功能，覆盖出行辅助与生活辅助两大类场景：", indent=False)
    add_table(doc, ["功能名称", "功能描述"], [
        ["连续导航", "设定目的地后连续拍照，结合多轮上下文生成连贯、不重复的语音指引，解决「最后十米」盲区。"],
        ["环境识别", "单次拍照即时识别台阶、障碍物、红绿灯、斑马线、门牌等环境信息并语音播报。"],
        ["文字朗读", "识别招牌、票据、药品说明等文字并朗读。"],
        ["紧急求助", "描述突发情况，生成自救建议、面向路人的求助喊话与一键拨号。"],
    ], widths=[3, 11])
    add_para(doc, "连续导航：用户设定目的地后进入连续导航模式。每轮拍照后，视觉子智能体识别环境，指引子智能体结合最近 3 轮历史生成指引，语音合成后实时播报。更换目的地自动清空会话，支持「重新开始」。这是本作品的核心功能，直接对应「最后十米」痛点。", indent=False)
    add_para(doc, "环境识别：单次拍照即时返回结构化环境信息（场景类型、障碍物、台阶、红绿灯、斑马线、门牌、文字、安全建议），并以一句口语化指引播报。", indent=False)
    add_para(doc, "文字朗读：针对视障者难以看清招牌、票据、药品说明等场景，拍照后系统提取全部文字，以大字号展示并语音朗读。", indent=False)
    add_para(doc, "紧急求助：用户描述突发情况后，系统判断严重程度，生成自救建议、面向路人的求助喊话（大字号显示供路人查看）、通话话术，并提供 110/120/紧急联系人一键拨号。", indent=False)
    add_heading(doc, "（2）原型设计", 2)
    add_para(doc, "运行平台：Web（Streamlit），支持 PWA「添加到主屏幕」，可在移动终端获得类原生 App 体验。", indent=False)
    add_para(doc, "屏幕适配：手机端友好，响应式布局，大字体、高对比、大按钮，语音自动播报。", indent=False)
    add_para(doc, "界面结构：首页（功能卡片导航）+ 连续导航 / 环境识别 / 文字朗读 / 紧急求助 / 作品介绍五个页面。", indent=False)
    add_para(doc, "作品的界面截图和界面说明见下图：", indent=False)
    add_image(doc, "nav.png", "图 1　连续导航界面——设定目的地、拍照、语音指引与导航记录")
    add_image(doc, "detect.png", "图 2　环境识别界面——拍照后识别台阶、障碍、红绿灯、门牌并播报")
    add_image(doc, "help.png", "图 3　紧急求助界面——大字求助广播、自救建议与一键拨号")

    # ===================== 四、作品实现、难点及特色分析 =====================
    add_heading(doc, "四、作品实现、难点及特色分析", 1)
    add_heading(doc, "（1）作品实现及难点", 2)
    add_para(doc, "系统采用前后端分离的分层架构，自上而下分为三层：前端层（Streamlit）负责拍照采集、结果展示与语音播报；编排层（Orchestrator）协调各子智能体、维护会话状态、串联「拍照→识别→指引→播报」流水线；智能体层由六个职责单一、可独立替换的子智能体组成。", indent=False)
    add_table(doc, ["子智能体", "模型/技术", "职责"], [
        ["VisionAgent", "GLM-4V-Flash", "图片 → 结构化环境 JSON"],
        ["GuidanceAgent", "GLM-4-Flash", "环境 + 历史 → 口语化指引"],
        ["OCRAgent", "GLM-4V-Flash", "图片 → 文字内容"],
        ["EmergencyAgent", "GLM-4-Flash", "情况 → 求助方案"],
        ["TTSAgent", "Edge-TTS", "文字 → 语音 MP3"],
        ["NavigationSession", "内存会话", "多轮上下文记忆"],
    ], widths=[4, 4, 6])
    add_para(doc, "核心数据流：拍照 → VisionAgent（结构化环境）→ GuidanceAgent（结合多轮历史）→ TTSAgent（语音）→ 播报；NavigationSession（会话记忆）反向为指引生成提供历史上下文。", indent=False)
    add_para(doc, "核心技术实现：① 多模态环境识别——通过提示词工程约束 GLM-4V-Flash 输出结构化 JSON（场景类型/障碍物/台阶/红绿灯/门牌等），并实现鲁棒解析（兼容 markdown 包裹与纯文本退化），图片上传前经 Pillow 压缩缩放，兼顾传输速度与识别精度；② 多轮上下文管理——NavigationSession 保存出行全程记录，只取最近 3 轮喂给模型，兼顾连贯性与上下文长度；③ 口语化指引生成——提示词约束「安全优先、30 字内、方位词、不重复」，temperature 0.5 兼顾自然度；④ 异步语音合成——Edge-TTS 流式分片聚合为 MP3，前端以 base64 自动播放。", indent=False)
    add_para(doc, "开发工具与平台：", indent=False)
    add_table(doc, ["类别", "技术", "版本"], [
        ["程序设计语言", "Python", "3.11.9"],
        ["前端框架", "Streamlit", "1.64.0"],
        ["视觉大模型", "智谱 GLM-4V-Flash", "免费"],
        ["文本大模型", "智谱 GLM-4-Flash", "免费"],
        ["语音合成", "Edge-TTS", "7.2.8"],
        ["HTTP 客户端", "requests", "2.34.2"],
        ["图像处理", "Pillow", "≥10.0.0"],
        ["配置管理", "python-dotenv", "1.2.3"],
    ], widths=[4, 5, 5])
    add_para(doc, "难点一：大模型结构化输出不稳定。GLM-4V-Flash 可能把 JSON 包裹在 markdown 中，或输出纯文本。解决方案：提示词严格约束 + 鲁棒 JSON 提取（正则截取 + 解析失败退化为纯文本描述），经大量测试验证稳定。", indent=False)
    add_para(doc, "难点二：连续导航如何避免重复提醒。单次识别无法感知「已提醒过什么」。解决方案：引入会话记忆，将最近 3 轮指引历史注入提示词，让模型生成连贯、不重复的指引。", indent=False)
    add_para(doc, "难点三：免费大模型的准确率与稳定性。解决方案：图片预处理（压缩、格式统一）、参数调优（低温、合理 max_tokens）、错误重试与优雅降级（未配置 Key 时返回兜底方案而非崩溃）。", indent=False)
    add_heading(doc, "（2）特色分析", 2)
    add_para(doc, "「多轮上下文连续导航」：通过会话记忆生成连贯、不重复的语音指引，是本作品区别于单次识别类应用的核心特色，切实提升视障者连续出行体验。", indent=False)
    add_para(doc, "「子智能体编排架构」：视觉识别、指引生成、语音合成等职责解耦、可独立替换，架构清晰、易扩展。", indent=False)
    add_para(doc, "「国产大模型 + 免费技术栈」：全部采用国产智谱 GLM 与免费 Edge-TTS，低成本、易推广，具备落地普惠性。", indent=False)
    add_para(doc, "「无障碍设计 + PWA 可安装」：大字体、高对比、大按钮，支持添加到主屏幕，兼顾视障与低视力用户。", indent=False)

    # ===================== 五、团队介绍和人员分工 =====================
    add_heading(doc, "五、团队介绍和人员分工", 1)
    add_table(doc, ["项目", "内容"], [
        ["所在学校", ""],
        ["团队名称", ""],
        ["指导教师", ""],
        ["团队成员及分工", "队长：（姓名）——系统架构与后端开发\n队员：（姓名）——前端界面设计\n队员：（姓名）——提示词工程与测试"],
    ], widths=[4, 10])

    # ===================== 六、其他 =====================
    add_heading(doc, "六、其他", 1)
    add_para(doc, "测试账号：作品为免登录的 Web 应用，无需注册账号，评审时直接访问公网 URL 即可使用（若评审系统要求填写测试用户名/密码，可留空或填写「无需登录」）。", indent=False)
    add_para(doc, "操作步骤及说明：", indent=False)
    add_numbered(doc, "连续导航：进入「连续导航」→ 输入目的地 → 对准前方拍照 → 听取语音指引 → 持续拍照获得连贯指引。", 1)
    add_numbered(doc, "环境识别：进入「环境识别」→ 对准环境拍照 → 听取环境播报。", 2)
    add_numbered(doc, "文字朗读：进入「文字朗读」→ 对准文字拍照 → 听取文字朗读。", 3)
    add_numbered(doc, "紧急求助：进入「紧急求助」→ 描述情况 → 生成求助信息并一键拨号。", 4)
    add_para(doc, "公网访问：作品部署于公网，提供公网 URL 与二维码（见提交材料），并支持 PWA「添加到主屏幕」。", indent=False)
    add_para(doc, "AI 使用声明：作品运行期调用智谱 GLM-4V-Flash、GLM-4-Flash 及 Edge-TTS；AI 辅助开发工具为 Claude Code（Sonnet 4.6），AI 编写代码约占全项目代码的 55%。", indent=False)
    add_para(doc, "源代码原创说明：原创部分包括选题创意、需求分析、系统架构设计、提示词工程、无障碍前端设计、多轮会话机制；第三方开源库（Streamlit、requests、edge-tts、Pillow、python-dotenv）均为宽松开源协议，已在本文档中列明。", indent=False)

    # ===================== 七、致谢 =====================
    add_heading(doc, "七、致谢", 1)
    add_para(doc, "（略）", indent=False)


def add_header(doc):
    """页眉：正文页显示大赛名称（宋体9pt居中+下边框线），封面首页留空。"""
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    section.header_distance = Cm(1.5)

    # 首页（封面）页眉留空
    fp = section.first_page_header
    fp.is_linked_to_previous = False

    # 正文页眉
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0]
    p.text = ""
    run = p.add_run("2026年华北五省（市、自治区）及港澳台大学生计算机应用大赛")
    run.font.name = "宋体"
    run.font.size = Pt(9)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "宋体")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 页眉下边框线
    pPr = p._element.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)


def build():
    doc = new_document()
    add_header(doc)
    build_cover(doc)
    build_declaration(doc)
    build_toc(doc)
    build_body(doc)
    out = DOCS / "02_软件设计文档.docx"
    doc.save(str(out))
    print("已生成:", out)


if __name__ == "__main__":
    build()
