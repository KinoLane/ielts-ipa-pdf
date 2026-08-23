# -*- coding: utf-8 -*-
"""一键流程：提取 PDF 词表 + 有道音标 + 生成带音标 PDF。

用法: python run_all.py --out <输出目录> <pdf1> <pdf2> ...
输出: <输出目录> 下的 words_data.json、youdao_cache.json、ipa_data.json、<书名>_带音标.pdf
"""
import argparse, subprocess, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SCRIPTS = Path(__file__).resolve().parent


def run(script, *args):
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".")
    ap.add_argument("pdfs", nargs="+")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    wd = str(out / "words_data.json")
    run("extract_words.py", "--out", wd, *a.pdfs)
    run("youdao_ipa.py", "--words", wd, "--out", str(out / "ipa_data.json"),
        "--cache", str(out / "youdao_cache.json"))
    run("make_pdf.py", "--data", str(out / "ipa_data.json"), "--out", str(out))
    print("\n完成。输出文件在:", out)


if __name__ == "__main__":
    main()
