#!/usr/bin/env python3
"""Export the IP-clean public translation files.

Reads the player's original MISS01..50.DAT (for the FNV-1a64 hashes of the
English prose — the English itself is discarded) and the locally-translated
data/lang/chinese-tw/missNN.txt (for the Traditional Chinese), and writes
translations_public/missNN.json = [{hash, zh, note}, ...]. No English is stored.

Usage: briefings_to_public.py <synd-data-dir> [<out-dir>]
"""
import json, sys
from pathlib import Path
from briefing_codec import decode_dat, hash_en, SECTION_NOTES

HERE = Path(__file__).resolve().parent
UNRNC = HERE / "unrnc"
ZH_DIR = HERE.parent / "data" / "lang" / "chinese-tw"

def zh_sections(p: Path):
    """Parse a translated missNN.txt into its 6 `|`-sections (comments skipped)."""
    lines = p.read_text(encoding="utf-8").split("\n")
    started, body = False, []
    for ln in lines:
        if not started and (ln.startswith("#") or ln.strip() == ""):
            continue
        started = True
        body.append(ln)
    parts = "\n".join(body).split("|")
    while len(parts) < 6:
        parts.append("")
    return parts[:6]

def main(argv):
    if len(argv) < 2:
        print(__doc__); sys.exit(1)
    src = Path(argv[1])
    out = Path(argv[2]) if len(argv) >= 3 else HERE.parent / "translations_public"
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for n in range(1, 51):
        dat = src / f"MISS{n:02d}.DAT"
        zh_txt = ZH_DIR / f"miss{n:02d}.txt"
        if not dat.exists() or not zh_txt.exists():
            continue
        en = decode_dat(dat, UNRNC)
        zh = zh_sections(zh_txt)
        trans = []
        for i in (2, 3, 4, 5):
            en_sec, zh_sec = en[i], zh[i].strip("\n")
            if en_sec.strip() and zh_sec.strip():
                trans.append({"hash": hash_en(en_sec), "zh": zh_sec,
                              "note": SECTION_NOTES.get(i, "")})
        data = {"_meta": {"mission": n, "game": "Syndicate (1993)",
                          "sections": len(trans)},
                "translations": trans}
        (out / f"miss{n:02d}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        count += 1
    print(f"wrote {count} public translation files to {out}")

if __name__ == "__main__":
    main(sys.argv)
