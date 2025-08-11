#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / 'docs'
MENU_JSON = ROOT / 'menu.json'


def build_menu_html(current_filename: str, menu_config: dict) -> str:
    items = []
    for entry in menu_config.get('menu', []):
        label = entry.get('label', '')
        href = entry.get('href')
        # 判斷選取頁
        item_class = 'menu-item'
        if href and Path(href).name == current_filename:
            item_class += ' item-selected'
        if href:
            items.append(f'<div class="{item_class}"><a href="{href}">{label}</a></div>')
        else:
            items.append(f'<div class="{item_class}">{label}</div>')
    items_html = '\n                '.join(items)
    return (
        '<button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false"></button>\n'
        '                <div class="menu-items">\n'
        f'                {items_html}\n'
        '                </div>'
    )


def inject_menu(html: str, menu_html: str) -> str:
    # 精準尋找 <div class="uh-menu"...> 對應的結束 </div>，避免只匹配到內層第一個 </div>
    open_match = re.search(r'<div\s+class="uh-menu"[^>]*>', html, flags=re.IGNORECASE)
    if not open_match:
        # 若沒有找到就嘗試插入在 .uh 與 .history 之間
        uh_match = re.search(r'<div\s+class="uh"[^>]*>', html, flags=re.IGNORECASE)
        history_match = re.search(r'<div\s+class="history"[^>]*>', html, flags=re.IGNORECASE)
        if uh_match and history_match:
            insert_pos = history_match.start()
            injection = ('\n            <div class="uh-menu">\n                ' + menu_html + '\n            </div>\n        ')
            return html[:insert_pos] + injection + html[insert_pos:]
        return html

    # 自 open tag 開始用深度計數尋找匹配的關閉位置
    token_re = re.compile(r'<div\b|</div>', flags=re.IGNORECASE)
    depth = 0
    start_idx = open_match.start()
    end_idx = None
    for m in token_re.finditer(html, pos=start_idx):
        token = m.group(0).lower()
        if token == '<div':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end_idx = m.end()
                break
    if end_idx is None:
        return html

    before = html[:start_idx]
    after = html[end_idx:]
    new_block = (
        '<div class="uh-menu">\n'
        '                ' + menu_html + '\n'
        '            </div>'
    )
    result = before + new_block + after
    # 確保在頁面底部載入 menu.js（若尚未載入）
    if 'menu.js' not in result:
        result = re.sub(r'</body>', '\n    <script src="menu.js"></script>\n  </body>', result, flags=re.IGNORECASE, count=1)
    return result


def main():
    menu_config = json.loads(MENU_JSON.read_text(encoding='utf-8'))
    for html_path in DOCS.glob('*.html'):
        current_name = html_path.name
        original = html_path.read_text(encoding='utf-8')
        menu_html = build_menu_html(current_name, menu_config)
        updated = inject_menu(original, menu_html)
        html_path.write_text(updated, encoding='utf-8')
        print(f'Injected menu into {current_name}')


if __name__ == '__main__':
    main()


