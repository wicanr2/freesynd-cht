#!/usr/bin/env python3
"""
Rasterise a TTF/OTF to the FreeSynd binary FSCJK16 glyph atlas format.

Unlike unifont2fnt.py (which expects native bitmap glyphs in BDF), this script
uses FreeType to render vector outlines at a fixed pixel height — useful when
the source is a TC font with clean strokes (Arphic Mingti, LXGW WenKai,
Cubic 11, etc.). The bitmap is thresholded back to 1bpp so the engine still
gets the simple atlas it expects.

Usage:
    python3 ttf2fnt.py <input.ttf> <output.fnt> <charset.txt> [--size 16]
"""
import argparse
import struct
import sys

import freetype


def parse_charset(path):
    cps = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("0x", "0X")):
            cps.append(int(line, 16))
        else:
            cps.append(int(line, 10))
    return sorted(set(cps))


def render_glyph(face, cp: int, target: int) -> bytes:
    """Render one codepoint into `target` rows × 2 bytes/row 1bpp (MSB first).

    The font is already configured at the desired pixel size via
    face.set_pixel_sizes (caller decides — e.g. 11px for Cubic-11, 16px for a
    16px design). The rendered glyph is centred inside the 16-pixel cell and
    placed at a baseline near the bottom (gives CJK characters a stable
    visual bottom). Anything beyond the cell is clipped.
    """
    out = bytearray(target * 2)  # 16 rows × 2 bytes
    idx = face.get_char_index(cp)
    if idx == 0:
        return bytes(out)  # blank glyph

    face.load_glyph(idx, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
    bmp = face.glyph.bitmap
    w, h = bmp.width, bmp.rows
    if w == 0 or h == 0:
        return bytes(out)

    # Where to put this glyph in the 16x16 box.
    # Vertical: align so the rendered glyph's top sits at (target - rendered_h)/2,
    # giving symmetric top/bottom padding for fonts smaller than `target`.
    # Horizontal: centre within the cell.
    vert_pad = max(0, (target - h) // 2)
    top = vert_pad
    left = max(0, (target - w) // 2)

    pitch = bmp.pitch
    src = bmp.buffer

    for srcy in range(h):
        dsty = top + srcy
        if dsty < 0 or dsty >= target:
            continue
        row_bits_dst = 0
        for srcx in range(w):
            byte = src[srcy * pitch + (srcx >> 3)]
            bit = (byte >> (7 - (srcx & 7))) & 1
            if bit:
                dstx = left + srcx
                if 0 <= dstx < target:
                    row_bits_dst |= 1 << (target - 1 - dstx)
        out[dsty * 2] = (row_bits_dst >> 8) & 0xFF
        out[dsty * 2 + 1] = row_bits_dst & 0xFF

    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ttf")
    ap.add_argument("fnt")
    ap.add_argument("charset")
    ap.add_argument("--size", type=int, default=16,
                    help="atlas box size (one of 16 or 12)")
    ap.add_argument("--render-size", type=int, default=None,
                    help="font pixel height to set on FreeType. Defaults to "
                         "--size. For a quality outline TTF (Noto Sans CJK TC "
                         "etc.) keep it equal to --size so the glyph fills the "
                         "cell; only set it smaller for a native pixel font.")
    ap.add_argument("--face-index", type=int, default=0,
                    help="face index inside a .ttc collection. For "
                         "NotoSansCJK-Regular.ttc, 3 = 'Noto Sans CJK TC'.")
    args = ap.parse_args()

    face = freetype.Face(args.ttf, args.face_index)
    face.set_pixel_sizes(0, args.render_size or args.size)

    cps = parse_charset(args.charset)

    glyph_bytes = []
    kept = []
    for cp in cps:
        if face.get_char_index(cp) == 0:
            continue
        glyph_bytes.append(render_glyph(face, cp, args.size))
        kept.append(cp)

    magic = b"FSCJK16\0" if args.size == 16 else b"FSCJK12\0"
    with open(args.fnt, "wb") as f:
        f.write(magic)
        f.write(struct.pack("<I", len(kept)))
        for cp in kept:
            f.write(struct.pack("<I", cp))
        for g in glyph_bytes:
            f.write(g)

    print(f"wrote {args.fnt}: {len(kept)}/{len(cps)} glyphs at {args.size}px")


if __name__ == "__main__":
    main()
