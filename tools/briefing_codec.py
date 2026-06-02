#!/usr/bin/env python3
"""Shared codec for the IP-clean briefing translation format (à la u6-cht).

The original English briefing prose (EA copyright) is NEVER stored — only the
FNV-1a 64-bit hash of each original section, mapped to the Traditional Chinese
translation. A player with their own legal Synd_1993 data can recompute the
hashes and apply the translations locally.

Section layout of a decoded MISSxx.DAT (CP437, `|`-separated):
  0 = info costs   1 = enhancement costs   2..5 = briefing prose (default + 3
  info levels). Only prose sections are translated; cost sections are copied
  verbatim from the player's own original at apply time.
"""
import struct, subprocess, tempfile, os
from pathlib import Path

FNV_OFFSET = 0xcbf29ce484222325
FNV_PRIME = 0x100000001b3
MASK64 = 0xffffffffffffffff

def fnv1a64(b: bytes) -> int:
    h = FNV_OFFSET
    for byte in b:
        h ^= byte
        h = (h * FNV_PRIME) & MASK64
    return h

def hash_en(s: str) -> str:
    """16-hex FNV-1a64 of an original English section (utf-8 bytes)."""
    return f"{fnv1a64(s.encode('utf-8')):016x}"

# Mapping prose section index -> human note.
SECTION_NOTES = {2: "default briefing", 3: "info level 1",
                 4: "info level 2", 5: "info level 3"}

def decode_dat(dat_path: Path, unrnc: Path):
    """RNC-decompress one MISSxx.DAT and return its CP437 sections (split on '|').
    Deterministic: both the exporter and apply step hash exactly these strings."""
    with tempfile.NamedTemporaryFile(delete=False) as fo:
        out = fo.name
    try:
        subprocess.run([str(unrnc), str(dat_path), out], check=True, capture_output=True)
        raw = Path(out).read_bytes()
    finally:
        os.unlink(out)
    text = raw.rstrip(b"\x00").decode("cp437", errors="replace")
    parts = text.split("|")
    while len(parts) < 6:
        parts.append("")
    return parts[:6]
