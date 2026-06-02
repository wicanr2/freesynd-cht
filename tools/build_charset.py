#!/usr/bin/env python3
"""
Build the codepoint charset list for chinese-16.fnt.

Strategy: union of
  1. Every non-ASCII codepoint that actually appears in
     data/lang/chinese-tw.lng and data/lang/chinese-tw/*.txt (so whatever the
     translator has typed will render).
  2. CJK punctuation blocks the translator is likely to use.
  3. A small ASCII range so embedded English text in Chinese strings (file
     names, slot numbers) still renders if for some reason the original CP437
     font is missing.

Writes one codepoint per line, hex with 0x prefix, sorted.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG_FILE = ROOT / "data" / "lang" / "chinese-tw.lng"
BRIEFING_DIR = ROOT / "data" / "lang" / "chinese-tw"
OUT = ROOT / "tools" / "charset.txt"


def scan(path: Path, cps: set):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for ch in text:
        cp = ord(ch)
        if cp >= 0x80:
            cps.add(cp)


def main():
    cps: set[int] = set()

    # 1. From actual translated content
    scan(LANG_FILE, cps)
    if BRIEFING_DIR.is_dir():
        for p in sorted(BRIEFING_DIR.glob("*.txt")):
            scan(p, cps)

    # 2. Always-on CJK punctuation + fullwidth ASCII forms
    for cp in range(0x3000, 0x3040):      # CJK symbols and punctuation
        cps.add(cp)
    for cp in range(0xFF00, 0xFFF0):      # Halfwidth/Fullwidth forms
        cps.add(cp)

    # 3. A baseline of common traditional Chinese — just the chars used in this
    #    project's plan/UI vocab. Translators can rebuild the .fnt later with a
    #    bigger list if needed (see plan.md).
    baseline = (
        "極道梟雄選單接受取消空強化裝備主公司設定開始任務"
        "載入儲存重新遊戲退出顏色標誌名稱玩家確定人口稅未知擁有狀態"
        "非常滿意普通不悅反叛簡報情報增強地圖隊伍選擇低溫艙研究"
        "重裝填購買賣費用彈藥射程射擊最低經費最高檢討統計"
        "已派幹員新增耗時擊殺敵方罪犯誤平民警察守衛說服命中率"
        "未發子失敗完成撤退登中自動型突雜項勸服迷你機槍火焰噴"
        "射器長距離能量護盾烏茲衝雷高斯散彈醫療包掃描門禁卡"
        "炸彈暗保護取得武消滅摧毀使用載具移動觀察拾按空白鍵跟隨"
        "被車撞著火丟下暫腿手胸臟眼大腦城市西歐遠東蒙古伊朗加州"
        "拉克印度北領哈薩東西澳堪察莫三比克秘魯歐格陵蘭阿斯加"
        "烏爾方斯堪那維亞育西伯利洛磯山美國南部尼墨哥薩伊爾及亞"
        "新英根廷南科羅多西部比波內瑞拉大洋速器伯西北肯亞茅利"
        "塔尼紐芬蘭威士哥倫日及巴拉烏圭環太平洋拉圭中關於"
        "前後左右上下進次號是否回到主目前無第個碼配置"
    )
    for ch in baseline:
        cps.add(ord(ch))

    # 4. Basic Latin so ASCII fallback works through the CJK path too (cheap).
    for cp in range(0x20, 0x7F):
        cps.add(cp)

    lines = [f"0x{cp:04X}\n" for cp in sorted(cps)]
    OUT.write_text("".join(lines), encoding="ascii")
    print(f"wrote {len(lines)} codepoints to {OUT}")


if __name__ == "__main__":
    main()
