#!/usr/bin/env python3
"""Cosmic Kitten — entry for make.fun "Make the AI judge excited".

Writes a single image, $MAKEFUN_OUTPUT_DIR/entry.png: a joyful kitten
astronaut riding a rainbow rocket through a candy nebula, drawn to excite
the AI judge. The picture is pre-rendered and shipped in this repository
as asset.png (see generate_image.py for the drawing code); this program
only copies it, so every run produces exactly the same bytes.

Standard library only. No network access. No secrets. No model calls.
The output is byte-identical on every run: same asset, same bytes.
"""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "asset.png")
MAGIC = b"\x89PNG\r\n\x1a\n"
LIMIT = 1024 * 1024  # entry.png must fit in 1 MiB


def run() -> int:
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(target_dir, "entry.png")

    with open(SOURCE, "rb") as handle:
        magic = handle.read(len(MAGIC))
    if magic != MAGIC:
        print(f"error: {SOURCE} is not a PNG file", file=sys.stderr)
        return 1

    os.makedirs(target_dir, exist_ok=True)
    shutil.copyfile(SOURCE, target)

    nbytes = os.path.getsize(target)
    if nbytes > LIMIT:
        print(f"error: {target} is {nbytes} bytes (max {LIMIT})",
              file=sys.stderr)
        return 1
    print(f"wrote {target} ({nbytes} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
