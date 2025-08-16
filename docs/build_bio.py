#!/usr/bin/env python3
import os
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE_EN = ROOT / 'bio.html'
TEMPLATE_ZH = ROOT / 'bio.zh.html'
LOCALE = os.environ.get('LOCALE', 'en').strip() or 'en'
IS_ZH = LOCALE.lower() == 'zh'
OUT_DIR = ROOT / ('docs/zh' if IS_ZH else 'docs')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    template_path = TEMPLATE_ZH if IS_ZH and TEMPLATE_ZH.exists() else TEMPLATE_EN
    html = template_path.read_text(encoding='utf-8')
    if IS_ZH:
        html = (html
            .replace('href="gallery.css"', 'href="../gallery.css"')
            .replace('src="menu.js"', 'src="../menu.js"')
        )
    out = OUT_DIR / 'bio.html'
    out.write_text(html, encoding='utf-8')
    print(f'Generated {out}')


if __name__ == '__main__':
    main()


