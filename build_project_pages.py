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

    slides_html = []
    dots_html = []
    for i, s in enumerate(slides):
        active_class = ' active' if i == 0 else ''
        slides_html.append(
            f'<img class="slide{active_class}" src="{s.get("src", "")}" alt="{s.get("alt", title)}">'
        )
        dots_html.append(
            f'<img class="dot" data-idx="{i}" src="image_{"black" if i == 0 else "grey"}dot.png" alt="dot {i+1}">'
        )

    html = TEMPLATE.read_text(encoding='utf-8')
    html = html.replace('<!--PROJECT_TITLE-->', title)
    html = html.replace('<!--SLIDESHOW_SLIDES-->', '\n        '.join(slides_html))
    html = html.replace('<!--SLIDESHOW_DOTS-->', '\n        '.join(dots_html))

    out_file = OUT_DIR / f'{data.get("slug", data_path.stem)}.html'
    out_file.write_text(html, encoding='utf-8')
    print(f'Generated {out_file.name}')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in sorted(DATA_DIR.glob('*.json')):
        build_project(p)


if __name__ == '__main__':
    main()


