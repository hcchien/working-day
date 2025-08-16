#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'project.template.html'
DATA_DIR = ROOT / 'projects_data'
OUT_DIR = ROOT / 'docs'


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
        picture = (
            f'<picture>'
            f'<source type="image/webp" media="(max-width: 640px)" srcset="{candidate_webp(960)} 1x, {candidate_webp(1600)} 2x">'
            f'<source type="image/webp" media="(max-width: 1280px)" srcset="{candidate_webp(1280)} 1x, {candidate_webp(1920)} 2x">'
            f'<source type="image/webp" media="(min-width: 1281px)" srcset="{candidate_webp(1920)} 1x, {candidate_webp(2560)} 2x">'
            f'<source media="(max-width: 640px)" srcset="{candidate(960)} 1x, {candidate(1600)} 2x">'
            f'<source media="(max-width: 1280px)" srcset="{candidate(1280)} 1x, {candidate(1920)} 2x">'
            f'<source media="(min-width: 1281px)" srcset="{candidate(1920)} 1x, {candidate(2560)} 2x">'
            f'<img id="slide-{i}" class="slide{active_class}" src="{candidate(1920)}" alt="{s.get("alt", title)}">'
            f'</picture>'
        )
        slides_html.append(picture)
        dots_html.append(f'<button class="dot" data-idx="{i}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}"><img src="image_{"black" if i == 0 else "grey"}dot.png" alt="Go to slide {i+1}"></button>')

    html = TEMPLATE.read_text(encoding='utf-8')
    html = html.replace('<!--PROJECT_TITLE-->', title)
    html = html.replace('<!--SLIDESHOW_SLIDES-->', '\n        '.join(slides_html))
    html = html.replace('<!--SLIDESHOW_DOTS-->', '\n        '.join(dots_html))

    out_file = OUT_DIR / f'{slug}.html'
    out_file.write_text(html, encoding='utf-8')
    print(f'Generated {out_file.name}')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in sorted(DATA_DIR.glob('*.json')):
        build_project(p)


if __name__ == '__main__':
    main()


