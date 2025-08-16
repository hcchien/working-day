#!/usr/bin/env python3
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / 'projects.template.html'
LOCALE = os.environ.get('LOCALE', 'en').strip() or 'en'
IS_ZH = LOCALE.lower() == 'zh'
DATA = ROOT / ('projects.zh.json' if IS_ZH and (ROOT / 'projects.zh.json').exists() else 'projects.json')
OUT_DIR = ROOT / ('docs/zh' if IS_ZH else 'docs')
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT = OUT_DIR / 'projects.static.html'
ASSET_PREFIX = '../' if IS_ZH else ''


def choose_random_preview_for_slug(slug: str) -> str:
    # 優先使用已優化的 960 寬縮圖
    images_dir = ROOT / 'projects_data' / slug / 'images'
    if images_dir.exists():
        candidates = sorted(images_dir.glob('*_w960.jpg'))
        if candidates:
            return str(candidates[random.randrange(len(candidates))].as_posix())

    # 次要：讀取該 project 的 JSON slides
    project_json = ROOT / 'projects_data' / f'{slug}.json'
    if project_json.exists():
        data = json.loads(project_json.read_text(encoding='utf-8'))
        base_dir = (data.get('baseDir') or '').strip()
        if base_dir and not base_dir.endswith('/'):
            base_dir = base_dir + '/'
        slides = data.get('slides') or []
        if slides:
            slide = random.choice(slides)
            src = (slide.get('src') or '').strip()
            if base_dir and ('/' not in src and not src.startswith('http')):
                resolved = base_dir + src
            else:
                resolved = src
            # 嘗試對應的 960 衍生檔
            if resolved.lower().endswith('.jpg'):
                derived = resolved[:-4] + '_w960.jpg'
            else:
                derived = resolved + '_w960.jpg'
            if (ROOT / derived).exists():
                return derived
            return resolved

    return ''


def render_items(items):
    html_parts = []
    for item in items or []:
        title = item.get('title', '')
        slug = item.get('slug')
        image = item.get('image', '')
        description = item.get('description', '')
        link_open = f'<a href="{slug}.html">' if slug else ''
        link_close = '</a>' if slug else ''
        # 若有 slug，嘗試從該專案資料夾隨機挑預覽圖
        if slug:
            rnd = choose_random_preview_for_slug(slug)
            if rnd:
                # 轉成相對路徑（相對網站根目錄），避免輸出成為本機絕對路徑
                image = Path(rnd).as_posix()
                if image.startswith(str(ROOT.as_posix()) + '/'):
                    image = image[len(str(ROOT.as_posix()) + '/'):]
                # 中文版加上資產前綴，確保在 docs/zh/ 下能正確引用
                if ASSET_PREFIX and not image.startswith(('http://','https://','/')):
                    image = ASSET_PREFIX + image
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

    if IS_ZH:
        out_html = (out_html
            .replace('href="gallery.css"', 'href="../gallery.css"')
            .replace('src="menu.js"', 'src="../menu.js"')
            .replace('src="slider.js"', 'src="../slider.js"')
        )

    OUTPUT.write_text(out_html, encoding='utf-8')
    print(f'Generated {OUTPUT.name}')


if __name__ == '__main__':
    main()


