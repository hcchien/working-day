#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'index.template.html'
DATA = ROOT / 'index_images.json'
OUTPUT = ROOT / 'index.static.html'


def main():
    template_html = TEMPLATE.read_text(encoding='utf-8')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    slides = data.get('slides', [])

    slides_html = []
    dots_html = []
    for i, s in enumerate(slides):
        active_class = ' active' if i == 0 else ''
        slides_html.append(f'<img class="slide{active_class}" src="{s.get("src", "")}" alt="{s.get("alt", "")}">')
        dots_html.append(f'<img class="dot" data-idx="{i}" src="image_{"black" if i == 0 else "grey"}dot.png" alt="dot {i+1}">')

    out_html = (
        template_html
        .replace('<!--SLIDESHOW_SLIDES-->', '\n        '.join(slides_html))
        .replace('<!--SLIDESHOW_DOTS-->', '\n        '.join(dots_html))
    )

    OUTPUT.write_text(out_html, encoding='utf-8')
    print('Generated index.static.html')


if __name__ == '__main__':
    main()


