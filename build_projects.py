#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'projects.template.html'
DATA = ROOT / 'projects.json'
OUTPUT = ROOT / 'projects.static.html'


def render_items(items):
    html_parts = []
    for item in items or []:
        title = item.get('title', '')
        slug = item.get('slug')
        image = item.get('image', '')
        description = item.get('description', '')
        link_open = f'<a href="{slug}.html">' if slug else ''
        link_close = '</a>' if slug else ''
        html_parts.append(
            f'''<div class="publish-item">
  <div class="publish-cover">
    {link_open}<img class="publish-image" src="{image}" alt="{title}"/>{link_close}
  </div>
  <div class="publish-desc">
    <div class="publish-title">{link_open}{title}{link_close}</div>
    <p>{description}</p>
  </div>
</div>'''
        )
    return "\n".join(html_parts)


def main():
    template_html = TEMPLATE.read_text(encoding='utf-8')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    sections = {s.get('key'): s for s in data.get('sections', [])}

    items_html = render_items(sections.get('projects', {}).get('items', []))

    out_html = template_html.replace('<!--PROJECTS_SECTION-->', items_html)

    OUTPUT.write_text(out_html, encoding='utf-8')
    print(f'Generated {OUTPUT.name}')


if __name__ == '__main__':
    main()


