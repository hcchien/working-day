#!/usr/bin/env python3
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'project.template.html'
DATA_DIR = ROOT / 'projects_data'
LOCALE = os.environ.get('LOCALE', 'en').strip() or 'en'
IS_ZH = LOCALE.lower() == 'zh'
OUT_DIR = ROOT / ('docs/zh' if IS_ZH else 'docs')


def build_project(data_path: Path):
    data = json.loads(data_path.read_text(encoding='utf-8'))
    title = data.get('title', data_path.stem)
    slides = data.get('slides', [])
    base_dir = data.get('baseDir', '').strip()
    if base_dir and not base_dir.endswith('/'):
        base_dir = base_dir + '/'
    slug = data.get('slug', data_path.stem)

    slides_html = []
    dots_html = []
    for i, s in enumerate(slides):
        active_class = ' active' if i == 0 else ''
        raw_src = s.get('src', '')
        src = raw_src
        if base_dir and ('/' not in raw_src and not raw_src.startswith('http')):
            src = f'{base_dir}{raw_src}'
        # 產出 <picture>，用多尺寸圖優化載入
        def candidate(w):
            if src.lower().endswith('.jpg'):
                return src[:-4] + f'_w{w}.jpg'
            return src + f'_w{w}.jpg'
        def candidate_webp(w):
            if src.lower().endswith('.jpg'):
                return src[:-4] + f'_w{w}.webp'
            return src + f'_w{w}.webp'
        prefix = '../' if IS_ZH else ''
        alt_text = s.get('alt', title)
        picture = (
            '<picture>'
            f'<source type="image/webp" media="(max-width: 640px)" srcset="{prefix}{candidate_webp(960)} 1x, {prefix}{candidate_webp(1600)} 2x">'
            f'<source type="image/webp" media="(max-width: 1280px)" srcset="{prefix}{candidate_webp(1280)} 1x, {prefix}{candidate_webp(1920)} 2x">'
            f'<source type="image/webp" media="(min-width: 1281px)" srcset="{prefix}{candidate_webp(1920)} 1x, {prefix}{candidate_webp(2560)} 2x">'
            f'<source media="(max-width: 640px)" srcset="{prefix}{candidate(960)} 1x, {prefix}{candidate(1600)} 2x">'
            f'<source media="(max-width: 1280px)" srcset="{prefix}{candidate(1280)} 1x, {prefix}{candidate(1920)} 2x">'
            f'<source media="(min-width: 1281px)" srcset="{prefix}{candidate(1920)} 1x, {prefix}{candidate(2560)} 2x">'
            f'<img id="slide-{i}" class="slide{active_class}" src="{prefix}{candidate(1920)}" alt="{alt_text}">'
            '</picture>'
        )
        slides_html.append(picture)
        aria_selected = 'true' if i == 0 else 'false'
        tab_index = 0 if i == 0 else -1
        dot_color = 'black' if i == 0 else 'grey'
        dots_html.append(
            f'<button class="dot" data-idx="{i}" aria-selected="{aria_selected}" tabindex="{tab_index}"><img src="{prefix}image_{dot_color}dot.png" alt="Go to slide {i+1}"></button>'
        )

    html = TEMPLATE.read_text(encoding='utf-8')
    html = html.replace('<!--PROJECT_TITLE-->', title)
    html = html.replace('<!--SLIDESHOW_SLIDES-->', '\n        '.join(slides_html))
    html = html.replace('<!--SLIDESHOW_DOTS-->', '\n        '.join(dots_html))

    out_file = OUT_DIR / f'{slug}.html'
    if IS_ZH:
        html = (html
            .replace('href="gallery.css"', 'href="../gallery.css"')
            .replace('src="menu.js"', 'src="../menu.js"')
            .replace('src="slider.js"', 'src="../slider.js"')
        )
    out_file.write_text(html, encoding='utf-8')
    print(f'Generated {out_file.name}')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in sorted(DATA_DIR.glob('*.json')):
        # For zh, prefer per-project zh json if exists
        if IS_ZH:
            zh_path = p.with_name(p.stem + '.zh.json')
            build_project(zh_path if zh_path.exists() else p)
        else:
            build_project(p)


if __name__ == '__main__':
    main()


