# 極道梟雄 — Syndicate (1993) 繁體中文化

> *Syndicate*（Bullfrog／EA, 1993）的繁體中文化紀錄 ✦ 建構於開源引擎 **FreeSynd**
> 全 373 條 UI 字串 + 50 關任務簡報全翻譯 ✦ Noto Sans CJK TC 點陣字 ✦ 系統 IME 中文輸入

這個 repo 是一份 **「翻譯紀錄 / 補丁」**，不是遊戲本體。它只收錄**我的翻譯成果**——
**原版英文文字（EA 版權）一個字都沒有**，只用雜湊值（FNV-1a 64-bit）對應。
你用自己的正版 *Synd_1993* 資料，在本機算回雜湊套用即可。

---

## 📸 實機截圖

| 主選單 | 隊伍選擇 |
|---|---|
| ![主選單](docs/screenshots/main-menu.png) | ![隊伍選擇](docs/screenshots/squad-select.png) |

| 戰場（即時 HUD：觀察中／移動中） | 遊戲暫停 |
|---|---|
| ![戰場](docs/screenshots/battlefield.png) | ![暫停](docs/screenshots/paused.png) |

---

## ⚡ 快速開始

### 你需要準備
1. **你自己的正版 Syndicate (1993)** — `Synd_1993.zip` 解壓出的 `MISS01.DAT`…`MISS50.DAT` 等原始檔。
2. **支援 `CHINESE_TC` 的 FreeSynd 建置** — 含繁中引擎修改（字型 CJK 分流、UTF-8 簡報 loader、IME）。
   引擎修改以 GPL patch 形式收錄於 [`patches/`](patches/)（核心繁中化 + 兩個畫面版本：640×480 銳利 / 1024×768 平滑），套用方式見 [`patches/README.md`](patches/README.md)。

### 三步套用
```bash
# 1. 取得本 repo
git clone https://github.com/wicanr2/freesynd-cht.git && cd freesynd-cht

# 2. 編譯 unrnc(解原版 RNC 壓縮),把你的原版資料放到 ./synd-data/
g++ -std=c++17 -I <freesynd>/utils/include tools/unrnc.cpp \
    <freesynd>/utils/src/dernc.cpp -o tools/unrnc

# 3. 用你自己的原版套用翻譯 → 產生可玩的 data/lang/chinese-tw/missNN.txt
python3 tools/apply_public.py ./synd-data
```
接著把 `data/lang/chinese-tw.lng`、`data/lang/chinese-tw/`、`fonts/*.fnt` 放進 FreeSynd
的 data 目錄，`user.conf` 設 `language = 5` 即可。

---

## 🔒 IP 乾淨設計 — 為什麼只有雜湊

EA 仍持有 Syndicate 的版權。**散布原版英文文字（任務簡報敘事）是不允許的。**
所以本 repo 採與 [u6-cht](https://github.com/wicanr2/u6-cht) 相同的做法：

```jsonc
// translations_public/miss01.json
{ "translations": [
  { "hash": "5b9247244dbec93f",      // = fnv1a64(原版英文段落) — 原文「不」存
    "zh":   "傭兵營區。\n\n暗殺。\n…", // 只存我的中譯
    "note": "default briefing" }
]}
```

- **原版英文**：只以 `fnv1a64()` 雜湊存在，無法還原成原文 → 不構成散布。
- **中譯**：是我的創作成果，公開分享。
- `tools/apply_public.py` 讀**你**的 `MISS*.DAT`，算每段英文的雜湊，對回中譯，
  在你本機組出可玩的簡報檔。原文永遠只存在你的正版裡。
- 成本數字、簡報結構等也都來自你的原版（apply 時逐字複製）。

> 短功能 UI 字串（選單、武器名、國名…）收錄於 `data/lang/chinese-tw.lng`，
> 與 FreeSynd 既有的法／德／義 `.lng` 同等性質（社群公認的在地化合理使用）。

---

## 🔧 技術筆記

- **字型**：`fonts/chinese-16.fnt`（大標題／按鈕）與 `chinese-12.fnt`（內文／清單），
  皆由 **Noto Sans CJK TC**（OFL）以 `tools/ttf2fnt.py` 點陣化，1bpp、依格子尺寸填滿。
  16×16 在 4:3 畫布下方正不變形。字集白名單見 `tools/charset.txt`（`build_charset.py` 生成）。
- **簡報格式**：六段以 `|` 分隔——段 0/1 為情報／強化成本（整數，含原版 sentinel 如 `200O`），
  段 2–5 為預設簡報＋三個情報等級的散文。引擎以 `loadBriefingUtf8` 讀取（跳過 `#` 註解、
  單一 `\n` 折成空格、空行為段落）。
- **斷行**：中文無空白,工具與譯文以全形字寬對齊簡報欄寬。

---

## 📰 1994 台灣遊戲媒體裡的「極道梟雄」

本中文化沿用的台灣譯名「**極道梟雄**」，可追溯到 1990 年代的台灣遊戲媒體。
《**軟體世界**》月刊第 61 期（**1994 年 4 月號**）在〈GAME 林秘笈〉專欄，以
**〈極道梟雄新手上機篇〉**（廖奇建，pp.70–71）介紹本作，開頭這樣勾勒這個賽博龐克世界：

> 「在被黑道組織主宰的未來世界中，只有武力才是唯一的真理。身為某一黑道組織的頭兒，
> 你當然要想辦法把其他的人從你的地盤趕出去……所以暗殺、破壞、掃蕩就是家常便飯了。」

文中歸納的五項上手要訣，三十年後仍是 Syndicate 的精髓：

| | 要訣 | 重點（1994 軟體世界） |
|---|---|---|
| ① | 要有花錢的哲學 | 經費有限，生財器具（感化器／Persuadertron）優先於武器研究 |
| ② | 認清任務的內容 | **務必看任務簡報的最後一段**，主目標以 `< >` 標出 — 本中文化簡報正照此格式呈現 |
| ③ | 了解武器的性能 | 迷你機槍最划算、雷射槍射程遠、高斯槍威力最大但彈藥稀少昂貴 |
| ④ | 善用地形效果 | 佔據高樓制高點俯射，「就像〈誰殺了甘迺迪〉裡躲在高樓的狙擊手」 |
| ⑤ | 借助敵人，壯大自己 | 撿敵人掉落的武器，尤以定時炸彈最值錢 |

> 當年雜誌把 Persuadertron 譯為「感化器」，把暗殺潛入的氛圍寫得活靈活現。
> 三十年後，這份在地化讓新玩家能用母語，重走廖奇建筆下那條「稱霸世界」的漫漫長路。
>
> 史料出處：《軟體世界》月刊第 61 期（中華民國 83 年〔1994〕4 月），軟體世界雜誌社，pp.70–71。
> 本 repo 僅作引用與評述，未轉載原文掃描頁。

---

## 🙏 致謝與授權

- **遊戲引擎**：[FreeSynd](https://github.com/bni/freesynd)（GPLv3）——Syndicate 的開源重製。本中文化的引擎側修改基於它。
- **字型**：[Noto Sans CJK](https://github.com/notofonts/noto-cjk)（SIL Open Font License 1.1）。
- **原版遊戲**：*Syndicate* © 1993 Bullfrog Productions / Electronic Arts。**本 repo 不含、也不散布任何 EA 原始素材**；請使用你自己的正版。
- **翻譯／工具**：© 本專案作者，個人非商業性質的中文化成果。
- 同系列紀錄：[u6-cht](https://github.com/wicanr2/u6-cht)（創世紀VI 繁中化）。
