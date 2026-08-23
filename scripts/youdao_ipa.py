# -*- coding: utf-8 -*-
"""用有道词典接口批量查询英式音标(ukphone)。

用法: python youdao_ipa.py --words words_data.json --out ipa_data.json [--cache youdao_cache.json]
输出: ipa_data.json，键为 {no, word, meaning, ipa}。
"""
import argparse, json, sys, io, time, urllib.request, urllib.parse, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SKILL = Path(__file__).resolve().parent.parent
UK_TXT = SKILL / "assets" / "en_UK.txt"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def fetch_ukphone(word):
    url = "https://dict.youdao.com/jsonapi?" + urllib.parse.urlencode({"q": word})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.youdao.com/"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode("utf-8"))
            ec = d.get("ec") or {}
            wl = ec.get("word") or []
            if wl:
                return (wl[0].get("ukphone") or wl[0].get("usphone") or "")
            return ""
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", default="words_data.json")
    ap.add_argument("--out", default="ipa_data.json")
    ap.add_argument("--cache", default="youdao_cache.json")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    try:
        import eng_to_ipa
    except Exception:
        eng_to_ipa = None

    words_data = json.loads(Path(a.words).read_text(encoding="utf-8"))
    words = set()
    for k in words_data:
        for e in words_data[k]:
            words.add(e["word"].strip().lower())

    cache = {}
    if Path(a.cache).exists():
        cache = json.loads(Path(a.cache).read_text(encoding="utf-8"))

    todo = [w for w in words if w not in cache]
    print(f"词数(去重)={len(words)} 已缓存={len(cache)} 待查={len(todo)}", flush=True)
    lock = threading.Lock()
    done = 0

    def worker(w):
        nonlocal done
        val = fetch_ukphone(w)
        with lock:
            cache[w] = val
            done += 1
            if done % 100 == 0:
                print(f"  已查 {done}/{len(todo)}", flush=True)

    if todo:
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            list(ex.map(worker, todo))
    Path(a.cache).write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    # 备选词典
    uk_dict = {}
    if UK_TXT.exists():
        for line in UK_TXT.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                w, ipa = line.split("\t", 1)
                uk_dict[w.strip().lower()] = ipa.strip().strip("/")

    def final_ipa(word):
        lw = word.strip().lower()
        if cache.get(lw):
            return cache[lw].strip().strip("/")
        if lw in uk_dict:
            return uk_dict[lw].replace("ɐ", "ə")
        if eng_to_ipa:
            try:
                r = eng_to_ipa.convert(lw)
                if r and "*" not in r:
                    return r
            except Exception:
                pass
        return ""

    result = {}
    for k in words_data:
        out = []
        for e in words_data[k]:
            out.append({"no": e["no"], "word": e["word"], "meaning": e["meaning"],
                        "ipa": final_ipa(e["word"])})
        result[k] = out
        print(f"[{k}] count={len(out)} found={sum(1 for x in out if x['ipa'])}")
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print("written", a.out)


if __name__ == "__main__":
    main()
