# -*- coding: utf-8 -*-
"""从 PDF 词汇表提取 (编号/单词/释义)，重建连续编号，智能断词。

用法: python extract_words.py --out words_data.json <pdf1> <pdf2> ...
输出: JSON，键为源文件名(去扩展名)，值为 [{no, word, meaning}, ...]。
"""
import argparse, json, sys, io
from pathlib import Path
import pdfplumber

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
UK_TXT = SKILL / "assets" / "en_UK.txt"


def load_uk():
    uk = set()
    if UK_TXT.exists():
        for line in UK_TXT.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                uk.add(line.split("\t", 1)[0].strip().lower())
    return uk


def clean(s):
    if s is None:
        return ""
    return str(s).replace("\r", "").strip()


def fix_word(w):
    w = clean(w)
    if "\n" not in w:
        return w
    parts = [p.strip() for p in w.split("\n") if p.strip()]
    no_space = "".join(parts)
    if no_space.lower() in _UK or "-" in no_space:
        return no_space
    if len(parts) > 1 and all(p.lower() in _UK for p in parts):
        return " ".join(parts)
    return no_space


def is_header(row):
    for c in row:
        if clean(c).lower() in ("word", "meaning", "no.", "no"):
            return True
    return False


_UK = set()


def extract(pdf_path):
    entries = []
    counter = 1
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                left, right = [], []
                for row in table:
                    if is_header(row):
                        continue
                    lw = fix_word(row[1]) if len(row) > 1 else ""
                    lm = clean(row[2]) if len(row) > 2 else ""
                    if lw:
                        left.append((lw, lm))
                    rw = fix_word(row[5]) if len(row) > 5 else ""
                    rm = clean(row[6]) if len(row) > 6 else ""
                    if rw:
                        right.append((rw, rm))
                for w, m in left:
                    entries.append({"no": str(counter), "word": w, "meaning": m}); counter += 1
                for w, m in right:
                    entries.append({"no": str(counter), "word": w, "meaning": m}); counter += 1
    return entries


def main():
    global _UK
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="words_data.json")
    ap.add_argument("pdfs", nargs="+")
    a = ap.parse_args()

    _UK = load_uk()
    result = {}
    for p in a.pdfs:
        key = Path(p).stem
        entries = extract(p)
        result[key] = entries
        nos = [int(e["no"]) for e in entries]
        print(f"[{key}] count={len(entries)} 编号1..N连续={nos == list(range(1, len(nos) + 1))}")

    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written", a.out)


if __name__ == "__main__":
    main()
