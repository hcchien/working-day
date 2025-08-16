#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
PROJECTS_DIR = ROOT / 'projects_data'
SIZES = [960, 1280, 1600, 1920, 2560]


def natural_key(name: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', name)]


def is_source_image(p: Path) -> bool:
    if p.name.startswith('.'):
        return False
    if re.search(r'_w\d+\.(jpg|jpeg|png|tif|tiff|webp)$', p.name, re.IGNORECASE):
        return False
    return p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp'}


def run_cmd(cmd: list) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def convert_to_jpg(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Prefer sips; fallback to simple copy if already jpg
    if src.suffix.lower() in {'.jpg', '.jpeg'}:
        shutil.copy2(src, dst)
        return
    if not run_cmd(["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)]):
        shutil.copy2(src, dst)


def generate_derivatives(numbered_jpg: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    base = numbered_jpg.stem
    tmp_jpg = numbered_jpg
    for w in SIZES:
        out_jpg = out_dir / f"{base}_w{w}.jpg"
        out_webp = out_dir / f"{base}_w{w}.webp"
        if (not out_jpg.exists()) or (out_jpg.stat().st_mtime < tmp_jpg.stat().st_mtime):
            run_cmd(["sips", "-s", "format", "jpeg", "-Z", str(w), str(tmp_jpg), "--out", str(out_jpg)])
        # webp via cwebp if available
        if shutil.which('cwebp'):
            if (not out_webp.exists()) or (out_webp.stat().st_mtime < out_jpg.stat().st_mtime):
                run_cmd(["cwebp", "-quiet", "-q", "82", str(out_jpg), "-o", str(out_webp)])


def process_project(json_path: Path):
    data = json.loads(json_path.read_text(encoding='utf-8'))
    slug = data.get('slug') or json_path.stem
    title = data.get('title', slug)

    # Determine raw source dir: prefer explicit rawDir, else baseDir if under images/, else images/<slug>
    raw_dir = data.get('rawDir')
    if not raw_dir:
        base_dir = data.get('baseDir', '')
        if base_dir.startswith('images/'):
            raw_dir = base_dir
        else:
            raw_dir = f'images/{slug}'
    raw_dir_path = ROOT / raw_dir
    if not raw_dir_path.exists():
        print(f"Skip {slug}: raw dir not found: {raw_dir_path}")
        return

    # Renumber to temp as 01.jpg, 02.jpg...
    sources = [p for p in raw_dir_path.iterdir() if p.is_file() and is_source_image(p)]
    if not sources:
        print(f"Skip {slug}: no images")
        return
    sources.sort(key=lambda p: natural_key(p.name))

    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        numbered = []
        for i, src in enumerate(sources, start=1):
            pad = f"{i:02d}"
            dst = tmp / f"{pad}.jpg"
            convert_to_jpg(src, dst)
            numbered.append(dst)

        # Output directory inside projects_data/<slug>/images
        out_dir = PROJECTS_DIR / slug / 'images'
        # Clear old outputs
        if out_dir.exists():
            for p in out_dir.glob('*'):
                if p.is_file():
                    p.unlink()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Generate derivatives for each numbered file
        for jpg in numbered:
            generate_derivatives(jpg, out_dir)

    # Update JSON: baseDir -> projects_data/<slug>/images, slides -> 01..NN
    slides = []
    files = sorted(out_dir.glob('[0-9][0-9]_w960.jpg'))
    for f in files:
        num = f.name.split('_', 1)[0]
        slides.append({"src": f"{num}.jpg", "alt": f"{title} {int(num)}"})
    data['baseDir'] = f"projects_data/{slug}/images"
    data['slides'] = slides
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    # Delete original raw files (keep folder)
    for p in raw_dir_path.glob('*'):
        if p.is_file() and is_source_image(p):
            p.unlink()
        elif p.is_file() and re.search(r'_w\d+\.(jpg|jpeg|png|tif|tiff|webp)$', p.name, re.IGNORECASE):
            p.unlink()
    print(f"Optimized {slug}: {len(slides)} images -> {out_dir}")


def main():
    for json_path in sorted(PROJECTS_DIR.glob('*.json')):
        process_project(json_path)


if __name__ == '__main__':
    main()


