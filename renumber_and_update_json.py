#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent

def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def is_source_image(p: Path) -> bool:
    if p.name.startswith('.'):
        return False
    if re.search(r"_w\d+\.(jpg|jpeg|png|tif|tiff|webp)$", p.name, re.IGNORECASE):
        return False
    return p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp'}

def convert_to_jpg(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["sips", "-s", "format", "jpeg", str(src), "--out", str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # 直接拷貝（若已是 jpg）
        shutil.copy2(src, dst)

def clean_old_numbered_and_derivatives(folder: Path):
    for p in folder.glob("*"):
        if p.name.startswith('.'):
            continue
        if re.fullmatch(r"\d{2}\.jpg", p.name):
            p.unlink(missing_ok=True)
        elif re.search(r"_w\d+\.(jpg|jpeg|png|tif|tiff|webp)$", p.name, re.IGNORECASE):
            p.unlink(missing_ok=True)

def renumber(dir_path: Path, json_path: Path):
    # 收集來源影像
    sources = [p for p in dir_path.iterdir() if p.is_file() and is_source_image(p)]
    sources.sort(key=lambda p: natural_key(p.name))
    if not sources:
        print(f"No images found in {dir_path}")
        return

    # 轉檔到暫存資料夾
    with tempfile.TemporaryDirectory() as tmpd:
        tmp = Path(tmpd)
        for i, src in enumerate(sources, start=1):
            pad = f"{i:02d}"
            dst = tmp / f"{pad}.jpg"
            convert_to_jpg(src, dst)

        # 清除舊的數字檔與衍生檔，再搬回
        clean_old_numbered_and_derivatives(dir_path)
        for p in sorted(tmp.iterdir()):
            shutil.move(str(p), str(dir_path / p.name))

    # 更新 JSON slides
    data = json.loads(json_path.read_text(encoding='utf-8'))
    slides = []
    for p in sorted(dir_path.glob("[0-9][0-9].jpg")):
        num = p.stem
        slides.append({"src": f"{num}.jpg", "alt": f"{data.get('title', data.get('slug',''))} {int(num)}"})
    data['slides'] = slides
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Updated {json_path} with {len(slides)} slides")

def main():
    # 目前針對 scooters_in_taipei
    img_dir = ROOT / 'images' / 'scooters_in_taipei'
    json_file = ROOT / 'projects_data' / 'scootersintaipei.json'
    renumber(img_dir, json_file)

if __name__ == '__main__':
    main()


