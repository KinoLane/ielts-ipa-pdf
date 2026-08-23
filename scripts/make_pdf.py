# -*- coding: utf-8 -*-
"""用 fpdf2 生成带音标的 PDF（完整嵌入字体，避免口口）。

用法: python make_pdf.py --data ipa_data.json --out <输出目录> [--cjk <中文字体>]
"""
import argparse, json, sys, io
from pathlib import Path
from fpdf import FPDF
from fpdf.fonts import FontFace

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
DEJAVU = SKILL / "assets" / "DejaVuSans.ttf"
WIN_CJK = r"C:\Windows\Fonts\simhei.ttf"


def make_pdf(out_dir, key, rows, cjk_path):
    out = Path(out_dir) / f"{key}_带音标.pdf"
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_font("CJK", "", cjk_path)
    pdf.add_font("DejaVu", "", str(DEJAVU))
    pdf.set_left_margin(10); pdf.set_right_margin(10); pdf.set_top_margin(12)
    pdf.add_page()

    with pdf.table(col_widths=(13, 40, 90, 42), text_align="LEFT", line_height=4.3,
                   padding=1, borders_layout="ALL",
                   headings_style=FontFace(emphasis="")) as table:
        head = table.row()
        pdf.set_font("CJK", size=9)
        for h in ["编号", "单词", "释义", "音标"]:
            head.cell(h)
        for r in rows:
            row = table.row()
            pdf.set_font("helvetica", size=7.5)
            row.cell(str(r["no"]))
            pdf.set_font("DejaVu", size=8.5)
            row.cell(str(r["word"]))
            pdf.set_font("CJK", size=8)
            row.cell(str(r["meaning"]))
            pdf.set_font("DejaVu", size=8.5)
            row.cell(str(r["ipa"] or ""))
    pdf.output(str(out))
    print(f"[ok] {key} rows={len(rows)} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="ipa_data.json")
    ap.add_argument("--out", default=".")
    ap.add_argument("--cjk", default=WIN_CJK)
    a = ap.parse_args()
    data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for key, rows in data.items():
        make_pdf(a.out, key, rows, a.cjk)


if __name__ == "__main__":
    main()
