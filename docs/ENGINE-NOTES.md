# ENGINE-NOTES — 移植與工程踩雷紀錄

> 把《極道梟雄》（Syndicate 1993，建構於開源引擎 **FreeSynd** GPLv3）繁中化的過程中，
> 真正花時間的不是翻譯，而是引擎側那幾個會讓畫面錯位、Windows 直接消失、或 CI 編不過的坑。
> 這份文件把這些經驗從**未進版控的 agent skill** 提升成 git-tracked 工程筆記，給接手的人少踩一次。
>
> 每節格式：**症狀（symptom）→ 根因（root cause）→ 修法（fix）**，能附原始碼處就附 `檔名:行號`。
> 補丁對照見 [`patches/README.md`](../patches/README.md)（`00`–`04` 共五個 patch）。

---

## 1. `MenuFont::drawText` 的 `x2` 預設 `true` 陷阱

**症狀**：在裝備／研究等資訊面板上，SIZE_1 的中文（本來就只有 12px）被畫成 24px，
撐爆狹窄欄位、字跟字疊在一起。

**根因**：介面是 `MenuFont::drawText(x, y, text, bool lighted, bool x2 = true)`。
只傳 **4 個參數**時，第 4 個對到 `lighted`，而 `x2` **沿用預設值 `true`** —— 於是字被放大兩倍。
英文原版字小、放大兩倍剛好；中文 12px 已是目標尺寸，再放大就溢位。

**修法**：第 5 個參數 **明確傳 `x2=false`**（裝備／研究的武器資訊面板）。
`MenuText` 靜態文字則呼叫 `setDoubleSize(false)`。ListBox 本來就畫單倍尺寸，跟著它對齊即可。

---

## 2. HD 版面：每個自繪座標都要 `Menu::mapY()`

**症狀**：套上 640×480 / 1024×768 的 HD 版本後，簡報選單（briefmenu）、隊伍選擇（selectmenu）
裡某些自繪元素（迷你地圖、自訂 `handleRender` 畫的東西）位置偏高約 1.2 倍、對不齊背景。

**根因**：引擎內部其實是渲染一張 **640×400** 畫布；HD 版把 `kScreenHeight` 由 400 改成 480，
並把烘焙好的背景框 400→480 拉伸。元件工廠（`addOption` / `addStatic` …）會自動套
`Menu::mapY(y) = y * kScreenHeight / 400`，但任何用 **原始 legacy 座標** 直接畫的東西沒被映射，
就停在舊的 400 基準上。**render 位置與 hit-test 兩邊都要 mapY**，否則點得到、看不到（或反之）。

**修法**：自繪座標一律經 `mapY()`。
**唯一例外是隊伍選擇畫面那個立繪** —— 它是 3 張固定尺寸的 sprite **上下疊**成一個人形，
逐張 `mapY` 會把三段拉開、人形被「撕裂」。正解是 **整個人形用一個統一的 `figShift` 垂直平移**，
只對它周邊的 **標籤、裝備格、連接線** 做 `mapY`。固定圖形整體位移，文字與線條才做比例映射。

---

## 3. Windows + CJK 路徑讓 `std::filesystem` 當掉

**症狀**：在含中文的安裝路徑（例如 `…\極道梟雄\`）下，視窗剛開就**靜默死亡**，沒有任何錯誤視窗。

**根因**：ANSI 版 `GetModuleFileNameW` 的對應 `GetModuleFileNameA` 把中文路徑用 C locale 編碼搞爛，
`std::filesystem` 拿到壞掉的位元組序列丟出 *"Cannot convert character sequence"* 例外。
因為是 `-mwindows`（GUI 子系統，**沒有 console**），例外與 abort 訊息都沒地方輸出 → 看起來就是「點了沒反應」。

**修法**（改 `utils/src/file.cpp` + `game/freesynd.cpp`）：

- `exeFolder()` 改用 **寬字元** `GetModuleFileNameW`，直接建成 `fs::path`，不經 ANSI。
- 在 `main()` 啟動時 **全域安裝 UTF-8 / UTF-16 codecvt locale**：
  `std::locale::global(std::locale(std::locale(), new std::codecvt_utf8_utf16<wchar_t>))`
  （`codecvt_utf8_utf16` 在 `-Werror` 下要用 `#pragma GCC diagnostic ignored "-Wdeprecated-declarations"` 包住）。
- 順帶把 `user.conf` 與存檔讀寫改成 **exe 所在資料夾**，不要 `%USERPROFILE%`。

**驗法**：把裸 exe 丟到一個含中文的路徑跑 —— 視窗要能開，且該路徑下要長出 `save/` 資料夾。

---

## 4. 字集驅動的點陣字 —— 改字串後一定要重生

**症狀**：新加的 UI 字串（例如 `AI：聰明` 這個標籤）在遊戲裡顯示成**空白**，整段不見字。

**根因**：`.fnt` 是 1bpp 點陣字，**只收錄 `tools/charset.txt` 裡列到的 codepoint**。
charset 檔是**十六進位碼點、一行一個**（例如 `0x8070`，**不是**字元本身）。
任何新字串引進的新字，如果沒有重新跑字集流程，loader 在字型裡找不到該 glyph，就畫成空白。

**修法**：改完翻譯／字串後重跑

```
tools/build_charset.py   # 掃所有用到的字 → tools/charset.txt
tools/ttf2fnt.py         # 以 Noto Sans CJK TC 點陣化 → chinese-{12,16}.fnt
```

要點：
- `ttf2fnt.py` 用 **Noto face-index 3**；`--render-size` 必須等於 `--size`（否則 glyph 對不上格子）。
- **必須在簡報／字串已就位的狀態下、且在它們之後重生**。若在簡報還沒套用時就生字集，
  會漏掉簡報用到的字 —— 那些字之後就全變空白。
- 編碼端（`ttf2fnt.py` 把每列 glyph 的最左 pixel 放在 bit `size-1`）與 loader 解碼端**對齊規則必須一致**，
  改一邊就要改另一邊。
- 字型一律從**高品質 host TTF**（Noto Sans CJK TC 等）點陣化；**Cubic 11 禁用**。

---

## 5. 平民恐慌 AI 的未初始化指標 crash

**症狀**：進入任務、開始交火約 **5–7 秒**時 SIGSEGV（Windows / Linux 皆會），沒有規律、很難重現。

**根因**：上游引擎 bug —— `PanicComponent::pArmedPed_` **未初始化**。
平民恐慌元件被喚醒後對這顆指向垃圾記憶體的指標呼叫 `isAlive()`，撞上隨機的非法位址。
因為要等場上有人掏槍、`PanicComponent` 才被喚醒，所以總是「開打幾秒後」才炸。

**修法**：把 `pArmedPed_` 初始化為 `nullptr`（**patch `00-fix-panic-crash.patch`**，2 檔）。
這是純引擎 bug、與中文化無關，可單獨回饋上游。

---

## 6. 原始碼 patch：每個 `.cpp` 都要連它的 header 一起收

**症狀**：`patch 04`（AI 補完）第一版只收了 `behaviour.cpp`、**漏了 `behaviour.h`**。
本機 worktree 編譯**過**，但**基於 patch 的 macOS CI build 失敗**，報
`no member named 'kBaseScanPeriod'`。

**根因**：本機 worktree 早就有**已 commit 的 header**，所以缺 header 的 patch 在本機也編得過 ——
假象。CI 是從乾淨上游 + 套 patch 重建的，header 沒被 patch 帶進去，新加的常數
（`kBaseScanPeriod` 等）在標頭裡不存在，編譯就掛。

**修法 / 教訓**：用**明確檔案清單**重新產 patch 時，**每個 `.cpp` 都要把對應的 `.h` 一起列入**。
不要相信「本機編得過」—— 本機有已 commit 的標頭，patch-based 的乾淨重建才是真考驗。

---

## Build / Test 迴圈

引擎在 Ubuntu 22.04 host 的 g++ 11 上因 `<format>` 編不過，一律走 docker：

| Docker image | 用途 |
|---|---|
| `freesynd-build` | 一般編譯（含 `<format>` 的工具鏈），日常改碼用 |
| `freesynd-dist` | 出 AppImage（glibc 2.34 → 可攜），打包玩家資料 |
| `freesynd-win` | mingw-w64 跨編 Windows zip（含 `極道梟雄.bat` 啟動器） |
| `freesynd-dbgrun` | gdb 交火驗證用的 runtime（見下） |

**gdb 交火 harness**：`00`（panic crash 修正）與 `04`（AI 補完）這類涉及戰場 AI 的改動，
都在 `freesynd-dbgrun` 裡用 gdb 跑進任務、實際交火，確認 §5 那類「開打幾秒後才炸」的 crash 已消失、
新 AI 行為（依 IPA 自衛、失聯放棄追擊）按預期運作 —— 先建一個**決定性的進戰場 pass/fail 訊號**，再動 AI 邏輯。

> 打包產物（AppImage / Windows zip）都會 bundle EA 原始資料，因此 **gitignore、永不 push**；
> 公開 repo 只收翻譯 + GPL 引擎 patch + FNV-1a-64 雜湊。
