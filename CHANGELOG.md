# 更新紀錄 Changelog

本檔記錄《極道梟雄》（Syndicate 1993，建構於開源引擎 **FreeSynd** GPLv3）繁體中文化的重要里程碑。
格式參照 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)。

本專案無版本標籤（git tag），下列以**日期 + 主題**標示邏輯里程碑，新者在上。
專案僅收錄翻譯與 GPL 引擎 patch；EA 原始素材一律不入庫（簡報以 FNV-1a-64 雜湊對照，玩家以**自有正版**在本機重建）。

---

## AI 模式 + 文件 — 2026-06-17

### 新增 Added
- **AI 正常／聰明可切換選項**（patch `04-ai-improvements`）：補完上游 README 標 *IN PROGRESS* 的兩個 AI roadmap 項目，做成可切換、可持久化（`ai_smart`）的選項。介面位於 **公司設定 → AI：正常 / AI：聰明**（正常＝忠於原版，聰明＝強化）。
  - **玩家特工**（依 IPA 自衛）：受威脅自動拔最強武器、腎上腺素加快反應、智力收緊命中散布。
  - **敵方**：失去目標逾 **4 秒**放棄追擊；守衛改用 `GuardAreaBehaviourComponent` 守崗位。
  - 涉及 `appcontext`（設定）、`confmenu` / `widget`（選單切換鈕）、`english.lng`（按鈕字串）。
- 工程文件：`docs/syndicate-ai-logic.md`（AI 邏輯）、`docs/ENGINE-NOTES.md`（移植踩雷紀錄）、`CONTEXT.md`（術語表）、`LICENSE`、README TOC。

### 修正 Fixed
- **平民恐慌 AI 交火 crash**（patch `00-fix-panic-crash`）：上游引擎 bug，`PanicComponent::pArmedPed_` 未初始化，平民恐慌 AI 在進入任務交火約 **5–7 秒**時對未初始化指標呼叫 `isAlive()` → SIGSEGV（Windows / Linux 皆會）。初始化為 `nullptr` 即修正；純引擎 bug，與中文化無關，可單獨回饋上游。
- **隊伍選擇畫面 HD 版面**（patches `02` / `03`）：自繪元素 `mapY` 映射修正，立繪不再撕裂。
- 為新標籤（`AI：聰明` 等）重新生成點陣字型，避免新字顯示空白。

---

## macOS 版本 — 2026-06-03

### 新增 Added
- **GitHub Actions macOS CI build**：universal `.app`（arm64 + x86_64），引擎於 macOS-14（Apple Silicon）runner 上建構，x86_64 為交叉編譯（Intel runner 稀缺）。
- conan 提供 `libpng` / `cli11` / `crcpp` / `utfcpp` 依賴（SDL 維持系統版）。
- 本機注入正版資料後重打為私用 `.app`；ad-hoc codesign 由 Mac 端 `啟用.command` 完成。

### 修正 Fixed
- FreeSynd checkout 改用完整 SHA（縮寫 SHA 失敗）。
- 複製 CHT 字型前先 `mkdir data/fonts`（基準 commit `fa27909` 無此目錄）。

---

## 打包與 HD 版本 — 2026-06-02 / 06-03

### 新增 Added
- **AppImage ×2**：可攜（glibc 2.34）Linux 執行檔，內含玩家資料。
- **Windows zip ×2**：mingw-w64 交叉編譯。
- **HD 畫面雙版本**（擇一套用）：
  - `02-hd-640x480-crisp`：內部畫布 640×480，nearest 銳利點陣放大（推薦，16×16 字方正不變形）。
  - `03-hd-1024x768-smooth`：1024×768 雙線性平滑放大（含 `SDL_SetTextureScaleMode` → `RENDER_SCALE_QUALITY` hint 相容性修正，避免舊版 SDL2 啟動 segfault）。

### 修正 Fixed
- **Windows + CJK 路徑 crash**（patch `01` 後續）：含中文的安裝路徑（如 `…\極道梟雄\`）下視窗剛開即靜默死亡。改用寬字元 `GetModuleFileNameW` 建 `fs::path`，並全域安裝 UTF-8 / UTF-16 codecvt locale。
- **裝備／研究面板字重疊**：`MenuFont::drawText` 的 `x2` 預設 `true`，SIZE_1 中文被放大成 24px 溢位；明確傳 `x2=false` 修正。

---

## 核心中文化 — 2026-06-02

### 新增 Added
- **`CHINESE_TC` 語系**（patch `01-freesynd-chinese-tc`，涉及 17 檔），`user.conf` 設 `language = 5` 即繁體中文。
- **373 條 UI 字串** + **50 關任務簡報**全數翻譯。
- **CJK 點陣字型**：12px（內文／清單）與 16px（大標題／按鈕）雙尺寸，由 **Noto Sans CJK TC** 點陣化（`font.cpp` / `fontmanager.cpp` CJK 分流）。
- **`loadBriefingUtf8`**：以 UTF-8 讀取簡報、跳過 `#` 註解行。
- **IP-clean 簡報對照機制**：以 **FNV-1a-64** 雜湊對應原文，僅存雜湊 + 中譯（不存 EA 原文），玩家以自有 `.DAT` 在本機重建（見 `tools/`）。
- `widget` / `menu` 的 IME 與行距調整、Catch2 單元測試。
