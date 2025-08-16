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
    base_dir = (data.get('baseDir') or '').strip()
    if base_dir and not base_dir.endswith('/'):
        base_dir = base_dir + '/'

    slides_html = []
    dots_html = []
    for i, s in enumerate(slides):
        active_class = ' active' if i == 0 else ''
        src = s.get("src", "")
        resolved = src
        if base_dir and ('/' not in src and not src.startswith('http')):
            resolved = base_dir + src
        def candidate(w):
            if resolved.lower().endswith('.jpg'):
                return resolved[:-4] + f'_w{w}.jpg'
            return resolved + f'_w{w}.jpg'
        def candidate_webp(w):
            if resolved.lower().endswith('.jpg'):
                return resolved[:-4] + f'_w{w}.webp'
            return resolved + f'_w{w}.webp'
        slides_html.append(
            f'<picture>'
            f'<source type="image/webp" media="(max-width: 640px)" srcset="{candidate_webp(960)} 1x, {candidate_webp(1600)} 2x">'
            f'<source type="image/webp" media="(max-width: 1280px)" srcset="{candidate_webp(1280)} 1x, {candidate_webp(1920)} 2x">'
            f'<source type="image/webp" media="(min-width: 1281px)" srcset="{candidate_webp(1920)} 1x, {candidate_webp(2560)} 2x">'
            f'<source media="(max-width: 640px)" srcset="{candidate(960)} 1x, {candidate(1600)} 2x">'
            f'<source media="(max-width: 1280px)" srcset="{candidate(1280)} 1x, {candidate(1920)} 2x">'
            f'<source media="(min-width: 1281px)" srcset="{candidate(1920)} 1x, {candidate(2560)} 2x">'
            f'<img id="slide-{i}" class="slide{active_class}" src="{candidate(1920)}" alt="{s.get("alt", "")}">' \
            f'</picture>'
        )
        dots_html.append(f'<button class="dot" data-idx="{i}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}"><img src="image_{"black" if i == 0 else "grey"}dot.png" alt="Go to slide {i+1}"></button>')

    out_html = (
        template_html
        .replace('<!--SLIDESHOW_SLIDES-->', '\n        '.join(slides_html))
        .replace('<!--SLIDESHOW_DOTS-->', '\n        '.join(dots_html))
    )

    OUTPUT.write_text(out_html, encoding='utf-8')
    print('Generated index.static.html')


if __name__ == '__main__':
    main()


