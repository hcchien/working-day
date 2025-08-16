#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="docs"

echo "[1/3] Clean output directory: ${OUT_DIR}"
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}"

echo "[2/3] Copy static assets to ${OUT_DIR} (excluding templates and build scripts)"
rsync -av \
  --exclude "${OUT_DIR}" \
  --exclude ".git" \
  --exclude "publish.template.html" \
  --exclude "projects.template.html" \
  --exclude "index.template.html" \
  --exclude "project.template.html" \
  --exclude "publish.static.html" \
  --exclude "projects.static.html" \
  --exclude "index.static.html" \
  --exclude "build_publish.py" \
  --exclude "build_projects.py" \
  --exclude "build_project_pages.py" \
  --exclude "build_index.py" \
  --exclude "inject_menu.py" \
  --exclude "build.sh" \
  --exclude "menu.json" \
  --exclude "index_images.json" \
  --exclude "projects_data" \
  --exclude "README.md" \
  --exclude ".gitignore" \
  --exclude "publish.html" \
  --exclude "projects.html" \
  ./ "${OUT_DIR}"/

CACHE_DIR=".cache"
mkdir -p "${CACHE_DIR}"

# Detect whether raw images changed; if unchanged, skip optimization
IMAGES_DIR="images"
LATEST_MTIME=0
if [ -d "${IMAGES_DIR}" ]; then
  # macOS compatible stat -f %m to get epoch mtime
  # Only take the first (latest) number; if empty, default to 0
  LATEST_MTIME=$(find "${IMAGES_DIR}" -type f -exec stat -f "%m" {} + 2>/dev/null | sort -nr | awk 'NR==1{print; exit}')
fi
LATEST_MTIME=${LATEST_MTIME:-0}
LATEST_MTIME=$(printf "%s" "${LATEST_MTIME}" | tr -d '\r' | awk 'NF{print $1}' )
LATEST_MTIME=${LATEST_MTIME:-0}

STAMP_FILE="${CACHE_DIR}/images_latest_mtime"
PREV_MTIME=$(sed -n '1p' "${STAMP_FILE}" 2>/dev/null || true)
PREV_MTIME=${PREV_MTIME:-0}
PREV_MTIME=$(printf "%s" "${PREV_MTIME}" | tr -d '\r' | awk 'NF{print $1}')
PREV_MTIME=${PREV_MTIME:-0}

if [[ ${LATEST_MTIME} -eq 0 ]]; then
  echo "[2.5/3] No raw images found; skip optimization"
elif [[ ${PREV_MTIME} -ne 0 && ${LATEST_MTIME} -le ${PREV_MTIME} ]]; then
  echo "[2.5/3] Images unchanged; skip optimization"
else
  echo "[2.5/3] Optimize project images only (to projects_data/<slug>/images)"
  python3 ./optimize_projects.py
  # Update stamp only if we actually had images
  if [[ ${LATEST_MTIME} -ne 0 ]]; then echo "${LATEST_MTIME}" > "${STAMP_FILE}"; fi
fi

echo "[2.6/3] Copy optimized project images into ${OUT_DIR}/projects_data"
mkdir -p "${OUT_DIR}/projects_data"
rsync -av \
  --prune-empty-dirs \
  --include '*/' \
  --include '*/images/**' \
  --exclude '*' \
  ./projects_data/ "${OUT_DIR}/projects_data/"

echo "[3/3] Build and replace HTML (en & zh)"

# Build EN
export LOCALE=en
python3 build_publish.py
mv -f "${OUT_DIR}/publish.static.html" "${OUT_DIR}/publish.html"
python3 build_projects.py
mv -f "${OUT_DIR}/projects.static.html" "${OUT_DIR}/projects.html"
python3 build_index.py
mv -f "${OUT_DIR}/index.static.html" "${OUT_DIR}/index.html"
python3 build_project_pages.py
python3 build_bio.py

# Build ZH
mkdir -p "${OUT_DIR}/zh"
export LOCALE=zh
python3 build_publish.py
mv -f "${OUT_DIR}/zh/publish.static.html" "${OUT_DIR}/zh/publish.html"
python3 build_projects.py
mv -f "${OUT_DIR}/zh/projects.static.html" "${OUT_DIR}/zh/projects.html"
python3 build_index.py
mv -f "${OUT_DIR}/zh/index.static.html" "${OUT_DIR}/zh/index.html"
python3 build_project_pages.py
python3 build_bio.py
unset LOCALE

echo "[post] Inject unified header menu into docs/*.html"
python3 inject_menu.py

echo "[post] Sync docs/*.html back to project root"
cp -f "${OUT_DIR}"/*.html ./

# Also inject menu into root-level html (mirrors docs/)
echo "[post] Re-inject menu for root-level html"
python3 inject_menu.py

# Sync zh pages to project root for local browsing
echo "[post] Sync docs/zh/*.html to ./zh/"
mkdir -p ./zh
cp -f "${OUT_DIR}/zh"/*.html ./zh/
# Inject again to adjust paths for root-level zh
python3 inject_menu.py

# Ensure root zh pages have clean names (no .static suffix)
for f in ./zh/*.static.html; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .static.html)"
  mv -f "$f" "./zh/${base}.html"
done

echo "Done. Open docs/publish.html or publish.html, or serve the docs/ folder."


