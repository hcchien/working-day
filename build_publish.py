#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'publish.template.html'
DATA = ROOT / 'publish.json'
OUTPUT = ROOT / 'publish.static.html'


def render_items(items):
    html_parts = []
    for item in items or []:
        title = item.get('title', '')
        image = item.get('image', '')
        description = item.get('description', '')
        date_or_time = item.get('time') or item.get('date') or ''
        location = item.get('location') or ''
        image_base = item.get('imageBase')

        if image_base:
            src = image_base.strip()
            def candidate(w: int) -> str:
                if src.lower().endswith('.jpg'):
                    return src[:-4] + f'_w{w}.jpg'
                return src + f'_w{w}.jpg'
            def candidate_webp(w: int) -> str:
                if src.lower().endswith('.jpg'):
                    return src[:-4] + f'_w{w}.webp'
                return src + f'_w{w}.webp'

            image_html = (
                f'<picture>'
                f'<source type="image/webp" media="(max-width: 640px)" srcset="{candidate_webp(960)} 1x, {candidate_webp(1600)} 2x">'
                f'<source type="image/webp" media="(max-width: 1280px)" srcset="{candidate_webp(1280)} 1x, {candidate_webp(1920)} 2x">'
                f'<source type="image/webp" media="(min-width: 1281px)" srcset="{candidate_webp(1920)} 1x, {candidate_webp(2560)} 2x">'
                f'<source media="(max-width: 640px)" srcset="{candidate(960)} 1x, {candidate(1600)} 2x">'
                f'<source media="(max-width: 1280px)" srcset="{candidate(1280)} 1x, {candidate(1920)} 2x">'
                f'<source media="(min-width: 1281px)" srcset="{candidate(1920)} 1x, {candidate(2560)} 2x">'
                f'<img class="publish-image" src="{candidate(1920)}" alt="{title}">'
                f'</picture>'
            )
        else:
            image_html = f'<img class="publish-image" src="{image}" alt="{title}"/>'

        # 組合時間/地點（若有）
        meta_html = ''
        meta_parts = []
        if date_or_time:
            meta_parts.append(f'<span class="publish-meta-time">{date_or_time}</span>')
        if location:
            meta_parts.append(f'<span class="publish-meta-location">{location}</span>')
        if meta_parts:
            meta_html = '<div class="publish-meta">' + ' · '.join(meta_parts) + '</div>'

        html_parts.append(
            f'''<div class="publish-item">
  <div class="publish-cover">
    {image_html}
  </div>
  <div class="publish-desc">
    <div class="publish-title">{title}</div>
    {meta_html}
    <p>{description}</p>
  </div>
</div>'''
        )
    return "\n".join(html_parts)


def main():
    template_html = TEMPLATE.read_text(encoding='utf-8')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    sections = {s.get('key'): s for s in data.get('sections', [])}

    publish_items_html = render_items(sections.get('publish', {}).get('items', []))
    exhibition_items_html = render_items(sections.get('exhibition', {}).get('items', []))

    out_html = (
        template_html
        .replace('<!--PUBLISH_SECTION-->', publish_items_html)
        .replace('<!--EXHIBITION_SECTION-->', exhibition_items_html)
    )

    OUTPUT.write_text(out_html, encoding='utf-8')
    print(f'Generated {OUTPUT.name}')


if __name__ == '__main__':
    main()


