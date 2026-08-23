# -*- coding: utf-8 -*-
"""校验生成的 PDF：中文/音标正常、无口口(替换字符/方框)。

用法: python verify.py <生成的pdf>
"""
import sys, io
from pathlib import Path
import pymupdf

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main():
    pdf_path = sys.argv[1]
    d = pymupdf.open(pdf_path)
    text = d[0].get_text()
    cjk = sum(1 for c in text if 0x4E00 <= ord(c) <= 0x9FFF)
    has_schwa = "ə" in text or "ˈ" in text
    has_repl = "\ufffd" in text
    print(f"文件: {pdf_path}")
    print(f"页数: {d.page_count}")
    print(f"第一页中文字符数: {cjk}")
    print(f"第一页含音标: {has_schwa}")
    print(f"第一页含「放弃」: {'放弃' in text}")
    print(f"出现口口/替换字符: {has_repl}")
    print("→ 建议用 Chrome / Edge / Adobe Acrobat 打开查看。")


if __name__ == "__main__":
    main()
