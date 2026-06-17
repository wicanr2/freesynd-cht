# tools/ — 工具流程

這個目錄是《極道梟雄》中文化的兩條建構流程。重點是**順序**：

1. **字型流程**：把翻好的字 → 點陣字型（`.fnt`）。
2. **IP-clean 簡報流程**：把維護者的簡報譯文匯出成只含**雜湊 + 中譯**的公開檔，玩家再以**自己合法擁有的** `Synd_1993` `.DAT` 在本機重建可玩的簡報文字。EA 原文一律不入庫。

| 檔案 | 角色 |
|---|---|
| `build_charset.py` | 掃描所有用到的字 → 生成 `charset.txt`（字集白名單） |
| `ttf2fnt.py` | 以 host TTF（Noto Sans CJK TC）把 `charset.txt` 點陣化成 `.fnt` |
| `briefing_codec.py` | 共用 codec：FNV-1a-64 雜湊 + RNC `.DAT` 解碼（被下面兩支匯入） |
| `briefings_to_public.py` | 維護者匯出：簡報譯文 → `translations_public/missNN.json`（雜湊 + zh，**永不含英文**） |
| `apply_public.py` | 玩家重建：以**自有** `.DAT` + 公開 json → `data/lang/chinese-tw/missNN.txt` |
| `unrnc` | 解壓 RNC-1 封裝的 `.DAT`（由 `briefing_codec.py` 呼叫；編譯方式見下） |
| `charset.txt` | 字集白名單（`build_charset.py` 產物，已入庫） |

---

## 1. 字型流程（Font pipeline）

點陣字型是**字集驅動**的：`.fnt` 只收錄 `charset.txt` 裡列到的 codepoint。
**任何 UI 字串或簡報改動、或出現新字後，必須重跑這條流程**，否則新字在遊戲裡會顯示成**空白**。
而且**必須在簡報 / 字串都已就位之後**重生 —— 若在簡報還沒套用時就生字集，會漏掉簡報用到的字。

```bash
# (1) 掃 data/lang/chinese-tw.lng + data/lang/chinese-tw/*.txt → tools/charset.txt
#     （十六進位碼點、一行一個，例如 0x8070；外加 CJK 標點與一段 ASCII fallback）
python3 tools/build_charset.py

# (2) 以 Noto Sans CJK TC 點陣化成 12px / 16px 兩個字型檔
#     --face-index 3  = NotoSansCJK-Regular.ttc 裡的 'Noto Sans CJK TC'
#     --render-size 必須等於 --size（否則 glyph 對不上格子）
python3 tools/ttf2fnt.py NotoSansCJK-Regular.ttc fonts/chinese-16.fnt tools/charset.txt --size 16 --render-size 16 --face-index 3
python3 tools/ttf2fnt.py NotoSansCJK-Regular.ttc fonts/chinese-12.fnt tools/charset.txt --size 12 --render-size 12 --face-index 3
```

產物 `fonts/chinese-{12,16}.fnt`（建構時複製到引擎的 `data/fonts/`）。
`ttf2fnt.py` 輸出自家二進位 atlas（magic `FSCJK16` / `FSCJK12`，1bpp，每列 glyph 最左 pixel 放在 bit `size-1`）—— 編碼端與引擎 loader 的對齊規則必須一致，改一邊就要改另一邊。**字型一律從高品質 host TTF 點陣化，Cubic 11 禁用。**

---

## 2. IP-clean 簡報流程（Briefing pipeline）

原始英文簡報（EA 版權）**從不入庫**。維護者只匯出每段原文的 **FNV-1a-64 雜湊** 對應到中譯；玩家用自己合法擁有的 `Synd_1993` `.DAT` 重算雜湊、在本機套回譯文。

`briefing_codec.py` 是共用 codec：以 `unrnc` 把 `MISSxx.DAT` 解 RNC、CP437 解碼、依 `|` 切成 6 段（段 0/1 為成本整數，段 2–5 為簡報文字＝預設簡報 + 3 個情報等級），並提供 `fnv1a64` 雜湊。

### 維護者：匯出公開檔

```bash
# 讀自有 MISS01..50.DAT（取原文雜湊，原文本身丟棄）+ data/lang/chinese-tw/missNN.txt
# → translations_public/missNN.json = [{hash, zh, note}, ...]（不含英文）
python3 tools/briefings_to_public.py <你的 Synd_1993 解壓資料夾>
```

### 玩家：以自有資料重建

```bash
# 讀自有 MISS01..50.DAT + translations_public/missNN.json
# → data/lang/chinese-tw/missNN.txt（成本段照抄原版；簡報段以原文雜湊查表套中譯）
python3 tools/apply_public.py <你的 Synd_1993 解壓資料夾>
```

### 編譯 `unrnc`

`unrnc` 是包住 FreeSynd `dernc` 的小 CLI，解壓 RNC-1 封裝的 `.DAT`。需在 clone 好的 FreeSynd 樹旁編譯：

```bash
# 於 tools/ 下，freesynd/ 與 freesynd-cht/ 同層時：
g++ -std=c++17 -I ../../freesynd/utils/include unrnc.cpp ../../freesynd/utils/src/dernc.cpp -o unrnc
```

`unrnc.cpp` 引入 `fs-utils/io/dernc.h`，依你 FreeSynd checkout 的實際相對路徑調整 `-I` 與 `dernc.cpp` 位置即可。
