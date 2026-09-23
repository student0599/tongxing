# -*- coding: utf-8 -*-
"""生成部署 URL 的二维码，作为 Web 作品的「安装包」提交物。

大赛对 Web（跨平台）作品的「安装包」要求是提供对应二维码。
部署到公网后，运行本脚本生成二维码图片，随作品提交。

用法：
    python scripts/gen_qr.py "https://你的应用.streamlit.app"
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # 避免中文 Windows 控制台编码报错
    except Exception:
        pass
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    if not url or "://" not in url:
        print('用法: python scripts/gen_qr.py "https://你的应用URL"')
        return

    try:
        import qrcode
    except ImportError:
        print("缺少 qrcode 库，请先执行: pip install qrcode[pil]")
        return

    out_dir = Path(__file__).resolve().parents[1] / "docs" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "qrcode.png"
    qrcode.make(url).save(path)
    print(f"✅ 二维码已生成: {path}")
    print(f"   指向: {url}")


if __name__ == "__main__":
    main()
