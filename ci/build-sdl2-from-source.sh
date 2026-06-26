#!/bin/sh
# build-sdl2-from-source.sh PREFIX ARCH
#
# Build pinned REAL SDL2 + SDL2_image + SDL2_mixer from source into PREFIX,
# targeting macOS $MIN for arch ARCH (arm64 | x86_64).
#
# WHY (landmine, ref open-king-bounty-cht issue #3): macOS CI used to do
# `brew install sdl2`, but in 2026-06 Homebrew swapped `sdl2` for *sdl2-compat*
# — a thin (~0.5 MB) SDL2-API-on-SDL3 shim that dlopen()s libSDL3 at RUNTIME.
# dylibbundler only bundles static link deps, so it never copies libSDL3 into
# the .app → players get "Failed loading SDL3 library" / black screen. Building
# the real pinned SDL2 from source removes that whole class of "brew changed
# under us" breakage and pins the ABI.
#
# FreeSynd's needs are minimal, so we link NO external codecs (self-contained,
# reproducible, fewer dylibs to bundle):
#   * SDL_image: stb_image only (engine just does IMG_INIT_PNG).
#   * SDL_mixer: WAV (Mix_LoadWAV) + the Mix_HookMusic callback only — the XMI
#     music is rendered to PCM by FreeSynd's own ADLMIDI synth (adl_openFile),
#     so SDL_mixer needs zero music decoders (no ogg/flac/mod/midi/mp3).
#   * No SDL2_net (FreeSynd doesn't link it).
#
# After running, put "$PREFIX/bin" on PATH so FreeSynd's CMake FindSDL2 picks up
# this sdl2-config, and pass -DCMAKE_PREFIX_PATH="$PREFIX".
set -e

PREFIX="${1:?usage: build-sdl2-from-source.sh PREFIX ARCH}"
ARCH="${2:?need ARCH (arm64|x86_64)}"
SDL_VER=2.30.9
IMG_VER=2.8.2
MIX_VER=2.8.0
MIN=13.4
WORK="$(mktemp -d)"
mkdir -p "$PREFIX"

# Build for the requested arch + deployment target. For x86_64 this script is
# launched under `arch -x86_64`, so the toolchain runs as x86_64 and configure's
# run-tests execute natively (via Rosetta) — no fragile autotools cross setup.
export CFLAGS="-arch $ARCH -mmacosx-version-min=$MIN"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="-arch $ARCH -mmacosx-version-min=$MIN"
export MACOSX_DEPLOYMENT_TARGET="$MIN"

dl() { curl -fsSL "$1" -o "$2" || wget -q "$1" -O "$2"; }

cd "$WORK"
echo "[sdl-src] arch=$ARCH min=$MIN  SDL2 $SDL_VER / image $IMG_VER / mixer $MIX_VER"
dl "https://github.com/libsdl-org/SDL/releases/download/release-$SDL_VER/SDL2-$SDL_VER.tar.gz" sdl2.tgz
dl "https://github.com/libsdl-org/SDL_image/releases/download/release-$IMG_VER/SDL2_image-$IMG_VER.tar.gz" img.tgz
dl "https://github.com/libsdl-org/SDL_mixer/releases/download/release-$MIX_VER/SDL2_mixer-$MIX_VER.tar.gz" mix.tgz

echo "[sdl-src] 1/3 SDL2 (real, not sdl2-compat)"
tar xf sdl2.tgz && cd "SDL2-$SDL_VER"
./configure --prefix="$PREFIX" >/dev/null && make -j3 >/dev/null && make install >/dev/null
cd "$WORK"
export PATH="$PREFIX/bin:$PATH"

echo "[sdl-src] 2/3 SDL2_image (stb_image PNG; no external codec)"
tar xf img.tgz && cd "SDL2_image-$IMG_VER"
./configure --prefix="$PREFIX" --with-sdl-prefix="$PREFIX" \
  --disable-png --disable-jpg --disable-tif --disable-webp --disable-avif --disable-jxl \
  --enable-stb-image >/dev/null && make -j3 >/dev/null && make install >/dev/null
cd "$WORK"

echo "[sdl-src] 3/3 SDL2_mixer (WAV + Mix_HookMusic only; no music decoders)"
tar xf mix.tgz && cd "SDL2_mixer-$MIX_VER"
./configure --prefix="$PREFIX" --with-sdl-prefix="$PREFIX" \
  --disable-music-ogg --disable-music-ogg-stb --disable-music-ogg-vorbis \
  --disable-music-ogg-tremor --disable-music-flac-libflac \
  --disable-music-mod-modplug --disable-music-mod-xmp \
  --disable-music-midi --disable-music-midi-fluidsynth \
  --disable-music-mp3-mpg123 --disable-music-opus >/dev/null \
  && make -j3 >/dev/null && make install >/dev/null
cd /
rm -rf "$WORK"

echo "[sdl-src] done -> $PREFIX"
echo "[sdl-src] verify (should be ~2MB REAL SDL2, NOT a ~0.5MB sdl2-compat shim):"
ls -la "$PREFIX/lib/libSDL2-2.0.0.dylib" || true
# Fail loudly if we somehow built/grabbed the SDL3 compat shim.
if otool -L "$PREFIX/lib/libSDL2-2.0.0.dylib" 2>/dev/null | grep -qi SDL3; then
    echo "[sdl-src] ERROR: libSDL2 references SDL3 (sdl2-compat shim) — aborting"; exit 1
fi
echo "[sdl-src] sdl2-config: $PREFIX/bin/sdl2-config"
