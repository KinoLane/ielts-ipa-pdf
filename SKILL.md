---
name: ielts-ipa-pdf
description: '给雅思/英语单词 PDF 表格加「音标」列。Use when the user has vocabulary/word-list PDFs (编号|单词|释义 tables, e.g. 雅思单词N.pdf) and wants a new 音标 column with Youdao/UK IPA, or wants to extract words+meanings from such PDF tables and generate a formatted PDF (编号|单词|释义|音标). Multi-step: pdfplumber extraction with smart line-wrap repair & rebuild sequential numbers, Youdao dict API for UK phonetics, fpdf2 PDF generation with full font embedding (avoids tofu/口口).'
argument-hint: '指定源 PDF 路径，可选输出目录'
user-invocable: true
---

# IELTS 单词 PDF 加音标列

把一个或多个“雅思/英语单词”PDF 表格，转成带**有道词典英式音标**列的新 PDF。

输出格式：`编号 | 单词 | 释义 | 音标`，每册各一个 PDF，中文用 `simhei.ttf`、英文/音标用 `DejaVuSans.ttf`、编号用标准 Helvetica，**完整嵌入字体**避免显示为“口口”。

## When to Use
- 用户提供英语词汇 PDF 表格（每行含 编号/单词/释义），希望新增音标列。
- 用户想批量查某个词表的有道英式音标。
- 用户希望输出能正常显示中文+音标（无口口/方框）的 PDF。

## 关键前提与陷阱（务必遵守）
1. **原 PDF 表格结构**：每页一个表格、8 列，左右两栏各是 `编号|单词|释义`（取左栏 col0/1/2，右栏 col4/5/6），每页首行是表头。
2. **编号缺失陷阱**：`pdfplumber` 常把**每页最后一行左栏的“编号”识别为空**。**不要**直接使用表格里的编号列；改为按“每页左栏全部 → 右栏全部”的阅读顺序**重建连续编号 1..N**。
3. **换行拆词**：单词/释义可能被换行拆开（如 `accommodi\non`、`boarding\nschool`）。用 smart `fix_word`：无空格合并后是词典词或含连字符→连写；否则按空格重连（需 `en_UK.txt`）。
4. **表头行**：跳过含 `Word/Meaning/No.` 的行。
5. **音标来源**：有道词典接口 `https://dict.youdao.com/jsonapi?q=<word>` → `ec.word[0].ukphone`（英式）。短语拆词如单词分别查；查不到用备选（`eng_to_ipa` 或 `en_UK.txt`），仍无则留空。
6. **中文字体**：用 `C:\Windows\Fonts\simhei.ttf`；**不要**用 reportlab 的 `UnicodeCIDFont("STSong-Light")`（未嵌入→口口）。生成用 `fpdf2` 完整嵌入字体（比 reportlab 字体子集更兼容）。

## Procedure
1. 确认 `.venv` 已装依赖：`pdfplumber fpdf2 eng_to_ipa pymupdf`（`install_python_packages`）。确保 `en_UK.txt`、`DejaVuSans.ttf` 存在（缺失时先跑 [`fetch_assets.py`](./scripts/fetch_assets.py)）。
2. 一键流程：[`run_all.py`](./scripts/run_all.py) `--out <输出目录> <pdf1> <pdf2> ...`
   - 提取所有词条→重建编号→智能断词→存 `words_data.json`
   - 多线程查有道英式音标（缓存 `youdao_cache.json`，断点续查）→ 存 `ipa_data.json`
   - 用 fpdf2 生成 `雅思单词N_带音标.pdf`（在 `<输出目录>`）
3. 核对：每册应为 3000/3000/634 这类原书数量；用 [`verify.py`](./scripts/verify.py) `<生成的pdf>` 检查中文/音标是否正常、有无口口（`\ufffd`）。

## Scripts
- [`run_all.py`](./scripts/run_all.py) —— 一键：提取+有道音标+生成 PDF
- [`extract_words.py`](./scripts/extract_words.py) —— 仅提取词条并重建编号
- [`youdao_ipa.py`](./scripts/youdao_ipa.py) —— 仅查有道英式音标（多线程+缓存）
- [`make_pdf.py`](./scripts/make_pdf.py) —— 用 fpdf2 生成带音标 PDF（完整嵌入字体）
- [`fetch_assets.py`](./scripts/fetch_assets.py) —— 下载 `en_UK.txt` 与 `DejaVuSans.ttf`
- [`verify.py`](./scripts/verify.py) —— 用 pymupdf 校验渲染（无口口）

## Assets
- `assets/en_UK.txt`（open-dict-data/ipa-dict 的英式 IPA 词典，用于断词判断）
- `assets/DejaVuSans.ttf`（IPA 字体）
- 中文字体用系统 `C:\Windows\Fonts\simhei.ttf`

## Notes
- 有道接口无 key，但请控制并发（脚本默认 8 线程）避免限流；失败会重试。
- 输出 PDF 行高/字号可在 `make_pdf.py` 的 `line_height`/`FontFace` 处调整。
- `install_python_packages` 需 `configure_python_environment` 先设置。
