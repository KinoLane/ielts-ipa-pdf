# -*- coding: utf-8 -*-
"""下载 skill 所需的英式 IPA 词典与 IPA 字体到 assets/ 目录。"""
import urllib.request, os, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

TARGETS = {
    "en_UK.txt": "https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/en_UK.txt",
    "DejaVuSans.ttf": "https://github.com/matplotlib/matplotlib/raw/main/lib/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf",
}

for name, url in TARGETS.items():
    dst = ASSETS / name
    if dst.exists() and dst.stat().st_size > 10000:
        print(f"[skip] {name} 已存在")
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        dst.write_bytes(data)
        print(f"[ok] {name} {len(data)} bytes -> {dst}")
    except Exception as e:
        print(f"[fail] {name} {e}")

print("assets:", [p.name for p in ASSETS.iterdir()])
