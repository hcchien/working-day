# working-day

## 建置與部署流程（使用 JSON 產生靜態頁面）

此專案的 `Publish & Exhibitions` 頁面資料維護於 `publish.json`，透過生成腳本輸出純靜態的 `docs/publish.html`，方便部署到 GitHub Pages。

### 需求
- macOS 或 Linux（內建 bash）
- Python 3（用於執行 `build_publish.py`）
- rsync（用於複製靜態資產；macOS 預設有）

### 資料結構（publish.json）
```json
{
  "sections": [
    {
      "key": "publish",
      "label": "PUBLISH",
      "items": [
        { "title": "1139KM", "image": "portrait.jpg", "description": "..." }
      ]
    },
    {
      "key": "exhibition",
      "label": "EXHIBITIONS",
      "items": [
        { "title": "1139KM", "image": "portrait.jpg", "description": "..." }
      ]
    }
  ]
}
```

### 一鍵生成靜態頁面
1. 編輯 `publish.json`
2. 執行建置腳本：
```bash
./build.sh
```
3. 產出在 `docs/`，主要頁面為 `docs/publish.html`

### 維護導覽選單（menu.json）
- 選單設定在 `menu.json`，格式如下：
```json
{
  "menu": [
    { "label": "Home", "href": "index.html" },
    { "label": "Projects" },
    { "label": "Publish & Exhibitions", "href": "publish.html" },
    { "label": "Bio", "href": "bio.html" }
  ]
}
```
- 執行 `./build.sh` 後，系統會將 `menu.json` 轉成 HTML，並注入 `docs/` 內每一個 `*.html` 檔的 `<div class="uh-menu">...</div>` 區塊。
- 會根據頁面檔名自動套用 `item-selected` 樣式到目前頁面對應的選單項。

### 本機預覽
- 啟動簡易伺服器：
```bash
python3 -m http.server 8000
```
- 瀏覽 `http://localhost:8000/docs/publish.html`

### 部署到 GitHub Pages（使用 docs/）
1. 在 GitHub 專案設定：Settings → Pages
2. 設定 Source：`Deploy from a branch`
3. Branch 選 `main`，Folder 選 `docs/`
4. 儲存後等候 Pages 部署完成（第一次可能需要幾分鐘）

### 常見問題
- 為什麼 `publish.html` 直接打開是空的？
  - 該檔版本使用 `fetch('publish.json')` 動態載入，`file://` 會被瀏覽器阻擋。正式部署請使用 `docs/publish.html`（已靜態化）。
- 要新增項目？
  - 只需在 `publish.json` 對應 `items` 中新增物件，再執行 `./build.sh`。

