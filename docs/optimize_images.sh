#!/usr/bin/env bash
set -euo pipefail

# 針對 images 目錄（與根目錄）中的 .jpg/.jpeg/.png/.tif/.tiff 生成多尺寸 jpg/webp：
# 960 / 1280 / 1600 / 1920 / 2560
# 會在同一資料夾輸出 *_w{size}.jpg 與 *_w{size}.webp

SIZES=(960 1280 1600 1920 2560)
QUALITY_JPG=0.9  # sips 無法設畫質，用於註記
QUALITY_WEBP=82

HAS_CWEBP=0
if command -v cwebp >/dev/null 2>&1; then HAS_CWEBP=1; fi

optimize_dir() {
  local dir="$1"
  [ -d "$dir" ] || return 0
  # 僅處理原始圖檔，排除已產生的 _w{size} 檔
  while IFS= read -r -d '' f; do
    local name base ext lower
    name=$(basename -- "$f")
    base="${name%.*}"
    ext="${name##*.}"
    lower=$(echo "$ext" | tr 'A-Z' 'a-z')
    # 來源檔完整路徑
    for w in "${SIZES[@]}"; do
      local out_jpg out_webp
      out_jpg="${dir}/${base}_w${w}.jpg"
      out_webp="${dir}/${base}_w${w}.webp"

      # 生成 JPG（若不存在或來源較新）
      if [ ! -f "$out_jpg" ] || [ "$out_jpg" -ot "$f" ]; then
        sips -s format jpeg -Z "$w" "$f" --out "$out_jpg" >/dev/null || true
      fi

      # 生成 WebP（若工具可用且不存在或來源較新）
      if [ $HAS_CWEBP -eq 1 ]; then
        if [ ! -f "$out_webp" ] || [ "$out_webp" -ot "$out_jpg" ]; then
          cwebp -quiet -q "$QUALITY_WEBP" "$out_jpg" -o "$out_webp" >/dev/null || true
        fi
      fi
    done
  done < <(find "$dir" -type f \( \
      -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \
    \) ! -regex '.*_w[0-9]+\.(jpg|jpeg|png|tif|tiff)$' -print0)
}

optimize_dir "images"
for d in images/*; do
  [ -d "$d" ] && optimize_dir "$d"
done
optimize_dir "."

if [ $HAS_CWEBP -eq 0 ]; then
  echo "Note: cwebp not found. Only JPG sizes were generated. Install 'webp' package to enable WebP."
fi

echo "Image optimization done."


