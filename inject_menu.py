#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / 'docs'
MENU_JSON_EN = ROOT / 'menu.json'
MENU_JSON_ZH = ROOT / 'menu.zh.json'


def build_menu_html(current_filename: str, menu_config: dict, is_zh: bool, zh_link_prefix: str = 'zh/', en_link_prefix: str = '../') -> str:
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

    # 語系切換：獨立固定在標題列的 Locale Switch，不佔用可折疊選單
    if is_zh:
        locale_switch = (
            '<div class="locale-switch">'
            f'<a href="{en_link_prefix}{current_filename}">EN</a>'
            ' / '
            '<span class="active">中文</span>'
            '</div>'
        )
    else:
        locale_switch = (
            '<div class="locale-switch">'
            '<span class="active">EN</span>'
            ' / '
            f'<a href="{zh_link_prefix}{current_filename}">中文</a>'
            '</div>'
        )
    return (
        '<button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false"></button>\n'
        f'                {locale_switch}\n'
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
    # Walk docs/ and project root recursively for html files
    targets = list(DOCS.rglob('*.html')) + list(ROOT.glob('*.html'))
    zh_root = ROOT / 'zh'
    if zh_root.exists():
        targets += list(zh_root.rglob('*.html'))

    for html_path in targets:
        # Pick menu per locale
        is_zh = (html_path.parent.name == 'zh')
        menu_path = MENU_JSON_ZH if is_zh and MENU_JSON_ZH.exists() else MENU_JSON_EN
        menu_config = json.loads(menu_path.read_text(encoding='utf-8'))

        current_name = html_path.name
        original = html_path.read_text(encoding='utf-8')
        # 決定語系連結前綴：
        # - docs/*.html (英文)：zh_link_prefix = 'zh/'
        # - docs/zh/*.html (中文)：en_link_prefix = '../'
        # - 專案根目錄/*.html (英文)：zh_link_prefix = 'docs/zh/'
        # - 專案根目錄/zh/*.html（若存在）：en_link_prefix = '../'（與 docs/zh 相同）
        zh_link_prefix = 'zh/'
        en_link_prefix = '../'
        menu_html = build_menu_html(current_name, menu_config, is_zh, zh_link_prefix=zh_link_prefix, en_link_prefix=en_link_prefix)
        updated = inject_menu(original, menu_html)

        # Ensure correct asset paths for zh pages
        if is_zh:
            updated = (updated
                .replace('src="menu.js"', 'src="../menu.js"')
                .replace('href="gallery.css"', 'href="../gallery.css"')
                .replace('src="slider.js"', 'src="../slider.js"')
            )

        html_path.write_text(updated, encoding='utf-8')
        print(f'Injected menu into {("zh/" if is_zh else "")}{current_name}')


if __name__ == '__main__':
    main()


