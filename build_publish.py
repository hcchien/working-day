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
        html_parts.append(
            f'''<div class="publish-item">
  <div class="publish-cover">
    <img class="publish-image" src="{image}" alt="{title}"/>
  </div>
  <div class="publish-desc">
    <div class="publish-title">{title}</div>
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


