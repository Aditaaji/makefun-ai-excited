#!/usr/bin/env python3
"""Cosmic Kitten — make.fun entry for "Make the AI judge excited".

This program ships one picture: a cheerful kitten astronaut riding a
rainbow rocket through a candy-coloured nebula. The picture is rendered
in advance by generate_image.py and stored in this repo as asset.png;
running this file only copies that asset to the judge's output folder,
so the result is identical on every run.

Only the Python standard library is used. No network, no secrets, no
model calls, no clock reads. Output is always entry.png, a PNG of at
most 1 MiB.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSET = HERE / "asset.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def check_png(path):
    """Return True when *path* starts with the 8-byte PNG signature."""
    with open(path, "rb") as stream:
        return stream.read(len(PNG_SIGNATURE)) == PNG_SIGNATURE


def deliver():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination = out_dir / "entry.png"
    if not check_png(ASSET):
        return fail(f"{ASSET} does not look like a PNG file")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = ASSET.read_bytes()
    if len(data) > MAX_BYTES:
        return fail(f"asset is {len(data)} bytes, over the {MAX_BYTES} limit")
    destination.write_bytes(data)
    print(f"wrote {destination} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
