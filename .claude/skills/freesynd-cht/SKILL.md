---
name: freesynd-cht
description: Build, run, package, or extend 極道梟雄 — the Traditional Chinese localization of Syndicate (1993) on the open-source FreeSynd engine. Use when applying this repo's translations to a legally-owned copy of Syndicate, reproducing the Chinese build, packaging it (AppImage / Windows), or working on the CJK font / menu-layout / Windows-path code.
---

# 極道梟雄 — FreeSynd Traditional Chinese

This repo (`freesynd-cht`) is an **IP-clean translation record**, not the game. It ships only the
translations + GPL engine patches. The original English (EA copyright) is **never** stored — mission
briefings are keyed by the FNV-1a-64 hash of the player's *own* data, reconstructed locally.

## Reproduce the Chinese build

**Prereq:** a legally-owned copy of Syndicate 1993 → extract its `.DAT` files into a `synd-data/`
folder. Engine is GPLv3 FreeSynd.

1. **Clone + checkout the patch baseline**
   ```bash
   git clone https://github.com/bni/freesynd.git && cd freesynd && git checkout fa27909
   ```
2. **Apply patches** — `01` (core CHT) is required; then pick **one** display variant:
   ```bash
   git apply ../freesynd-cht/patches/01-freesynd-chinese-tc.patch
   git apply ../freesynd-cht/patches/02-hd-640x480-crisp.patch     # 640×480 sharp (recommended)
   #   or
   git apply ../freesynd-cht/patches/03-hd-1024x768-smooth.patch   # 1024×768 bilinear
   ```
3. **Copy fonts + UI strings**
   ```bash
   cp ../freesynd-cht/fonts/*.fnt        data/fonts/
   cp ../freesynd-cht/data/lang/chinese-tw.lng data/lang/
   ```
4. **Apply briefing translations from YOUR data** (reconstructs `data/lang/chinese-tw/missNN.txt`;
   the repo holds only hashes + zh, no EA prose):
   ```bash
   python3 ../freesynd-cht/tools/apply_public.py <your-synd-data-dir>
   ```
5. **Build & run** — set `language = 5` in `user.conf` for Traditional Chinese. Ubuntu 22.04 host
   g++ 11 can't build (`<format>`); use the docker image. See `patches/README.md` for full steps.

## Conventions & gotchas (when extending the localization)

- **The font is charset-driven — regenerate it AFTER translating.** `tools/build_charset.py` collects
  every used char into `tools/charset.txt`; `tools/ttf2fnt.py` renders `chinese-{12,16}.fnt` from a
  host TTF. **Use Noto Sans CJK TC (or another quality TTF); Cubic 11 is banned.** The `.fnt` only
  covers chars in the charset — a translation pass that introduces new chars renders them **blank**
  until you regenerate. (`ttf2fnt.py` packs each glyph row with the leftmost pixel at bit
  `size-1`; the loader must decode with the same alignment — keep encoder/decoder in sync.)
- **The `x2`-default-true `drawText` trap.** `MenuFont::drawText(x, y, text, bool lighted, bool x2 = true)`
  — a **4-arg** call sets `lighted`, and **`x2` defaults to `true`**, so a 12px CJK SIZE_1 glyph
  renders at 24px and overlaps tight info panels. Fix: pass `x2=false` **explicitly** as the 5th arg
  (see the equip/research weapon-info panels). For `MenuText` statics, call
  `setDoubleSize(false)`. The ListBox already draws at single size — match it.
- **HD layout maps every legacy Y with `Menu::mapY(y) = y * kScreenHeight / 400`.** The 4:3 variants
  raise `kScreenHeight` 400→480; widget factories (`addOption`/`addStatic`/…) apply `mapY`, but any
  element drawn at a **raw** legacy coordinate (e.g. the briefing minimap `kMiniMapScreenPos`, custom
  `handleRender` draws) sits ~1.2× too high/wrong. Map both its render position **and** its hit-test.
- **Windows + CJK paths crash `std::filesystem`.** A path containing CJK (e.g. `極道梟雄`) throws
  *"Cannot convert character sequence"* under the C locale → the game dies right after the window opens.
  Two fixes (in `utils/src/file.cpp` + `game/freesynd.cpp`): build `exeFolder()` from the **wide**
  `GetModuleFileNameW` as an `fs::path`; and in `main()` install a UTF-8 codecvt globally —
  `std::locale::global(std::locale(std::locale(), new std::codecvt_utf8_utf16<wchar_t>))` (wrap in
  `#pragma GCC diagnostic ignored "-Wdeprecated-declarations"` for `-Werror`). Also read `user.conf`
  + saves from the **exe folder**, not `%USERPROFILE%`. Verify by running the bare exe from a path
  that contains CJK — window must open and a `save/` folder must be created there.

## Packaging (author's local pipeline — not in this repo)

- **AppImage:** built in an Ubuntu-22.04 `freesynd-dist` docker image (glibc 2.34 → portable),
  bundling the player's data. **Windows:** mingw-w64 `freesynd-win` image; the zip ships
  `極道梟雄.sh` / `極道梟雄.bat` launchers. Both bundle EA data, so **they are gitignored and
  never pushed**.
- **macOS:** `.github/workflows/macos.yml` builds the **engine-only** `極道梟雄.app` on a real
  `macos-14` runner (IP-clean — no EA data), per arch. arm64 is native; **x86_64 is cross-built
  on the same Apple-Silicon runner** via Rosetta + Intel Homebrew (`arch -x86_64 /usr/local/bin/brew
  install sdl2 …`, `-DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_PREFIX_PATH=/usr/local`) because free
  Intel `macos-13` runners are deprecated and queue for ~an hour. Build notes: SDL is *system*
  (Homebrew) but **libpng/cli11/crcpp/utfcpp come from conan** (`-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=
  cmake/conan_provider.cmake`); set `-DCMAKE_OSX_DEPLOYMENT_TARGET=13.4` for `std::format`; check out
  the engine by **full 40-char SHA**; `mkdir -p data/fonts` before copying the CHT fonts;
  `dylibbundler` self-contains the bundle. Then **locally** inject EA data + briefings into
  `Contents/Resources/data/` and `…/lang/chinese-tw/`, and ship a `啟用.command` that ad-hoc-signs on
  the user's Mac (`xattr -cr` + `codesign --force --deep -s -`) — adding files invalidates the
  signature and Apple Silicon won't launch an unsigned/invalid bundle.

## Hard IP rule

Never commit or push EA content: `synd-data`, original English prose, or any AppImage/zip that
bundles them. The public repo stores **only** translations + FNV-1a-64 hashes. `.gitignore` excludes
`/synd-data`, `/dist/`, `*.AppImage`, `*.zip`.
