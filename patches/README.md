# FreeSynd 引擎修改 patch — 極道梟雄繁體中文化

要玩中文版，得把這些修改套到開源引擎 **FreeSynd**（GPLv3）上自行編譯。
這裡**只放程式碼修改**（GPL 授權），不含任何 EA 原始素材。

## 套用步驟

```bash
git clone https://github.com/bni/freesynd.git
cd freesynd
git checkout fa27909      # 本 patch 對應的上游基準（≈ upstream main）

# 0) 上游 crash 修正（強烈建議；與中文化無關，純引擎 bug）
git apply ../freesynd-cht/patches/00-fix-panic-crash.patch

# 1) 核心繁體中文化（必套）
git apply ../freesynd-cht/patches/01-freesynd-chinese-tc.patch

# 2) 選一個畫面版本（擇一）
git apply ../freesynd-cht/patches/02-hd-640x480-crisp.patch    # 640×480 銳利點陣（推薦）
#   或
git apply ../freesynd-cht/patches/03-hd-1024x768-smooth.patch  # 1024×768 平滑 HD
```

## 套完之後（補上資料與字型）

1. 複製字型：`freesynd-cht/fonts/*.fnt` → `data/fonts/`
2. 複製 UI 字串：`freesynd-cht/data/lang/chinese-tw.lng` → `data/lang/`
3. 用**你自己的正版**套用簡報譯文（不含 EA 原文，見上層 README 的雜湊機制）：
   ```bash
   python3 ../freesynd-cht/tools/apply_public.py <你的 Synd_1993 解壓資料夾>
   ```
4. 依 FreeSynd 說明編譯；`user.conf` 設 `language = 5` 即為繁體中文。

## 各 patch 內容

| patch | 範圍 | 重點 |
|---|---|---|
| `00-fix-panic-crash.patch` | 2 檔 | 上游引擎 bug：`PanicComponent::pArmedPed_` 未初始化，平民恐慌 AI 在**進入任務交火約 5–7 秒**時對未初始化指標呼叫 `isAlive()` → SIGSEGV（Windows/Linux 皆會）。初始化為 `nullptr` 即修正。與中文化無關，可單獨回饋上游 |
| `01-freesynd-chinese-tc.patch` | 17 檔 | `CHINESE_TC` 語系；`font.cpp`/`fontmanager.cpp` CJK 分流與 **12px/16px 雙尺寸**字型；`missionbriefing` 的 **`loadBriefingUtf8`**（UTF-8、跳過 `#` 註解）；`widget`/`menu` 的 IME 與行距；Catch2 單元測試 |
| `02-hd-640x480-crisp.patch` | 5 檔 | 內部畫布 **640×480**（16×16 字方正不變形）+ nearest 銳利縮放；`Menu::mapY` 版面映射 |
| `03-hd-1024x768-smooth.patch` | 6 檔 | 1024×768 雙線性平滑放大；含 `SDL_SetTextureScaleMode` → `RENDER_SCALE_QUALITY` hint 的相容性修正（避免舊版 SDL2 啟動 segfault） |

> 上游基準：FreeSynd commit `fa27909`。patch 僅含原始碼，無 EA 內容；遊戲原版資料請自備正版。
