#!/usr/bin/env python3
"""Apply the public translations to the player's own original game data.

Reads the player's MISS01..50.DAT + translations_public/missNN.json and writes
the playable data/lang/chinese-tw/missNN.txt (cost sections copied verbatim from
the original; prose looked up by the FNV-1a64 hash of the original English).
No English text is read from the repo — it only ever lives in the player's DAT.

Usage: apply_public.py <synd-data-dir> [<translations_public-dir>]
"""
import json, sys
from pathlib import Path
from briefing_codec import decode_dat, hash_en

HERE = Path(__file__).resolve().parent
UNRNC = HERE / "unrnc"
OUT_DIR = HERE.parent / "data" / "lang" / "chinese-tw"

def cost_lines(section: str):
    """Just the non-blank integer/sentinel tokens of a cost section."""
    return [ln.strip() for ln in section.split("\n") if ln.strip()]

def main(argv):
    if len(argv) < 2:
        print(__doc__); sys.exit(1)
    src = Path(argv[1])
    pub = Path(argv[2]) if len(argv) >= 3 else HERE.parent / "translations_public"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for n in range(1, 51):
        dat = src / f"MISS{n:02d}.DAT"
        js = pub / f"miss{n:02d}.json"
        if not dat.exists() or not js.exists():
            continue
        en = decode_dat(dat, UNRNC)
        lut = {t["hash"]: t["zh"] for t in json.loads(js.read_text(encoding="utf-8"))["translations"]}
        out = [f"# 第 {n:02d} 關任務簡報（繁體中文）— 由你的原版 MISS{n:02d}.DAT 套用，個人用途",
               "# 段 0/1 為成本整數（來自原版），段 2 起為譯文。", ""]
        out += cost_lines(en[0]); out.append("|")
        out += cost_lines(en[1]); out.append("|")
        for i in (2, 3, 4, 5):
            if i >= len(en) or not en[i].strip():
                continue
            zh = lut.get(hash_en(en[i]))
            out.append(zh if zh is not None else "（未翻譯 / untranslated）")
            if i != 5:
                out.append("|")
        (OUT_DIR / f"miss{n:02d}.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
        count += 1
    print(f"applied {count} briefings to {OUT_DIR}")

if __name__ == "__main__":
    main(sys.argv)
