#!/usr/bin/env python3
"""Cosmic Kitten entry point.

Copies the pre-generated asset.png into the make.fun output directory
as entry.png, after validating that it is a real PNG under 1 MiB.

Stdlib only. Exit code 0 on success, 1 on any failure.
"""
import os
import shutil
import sys

SOURCE = "asset.png"
TARGET_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    return 1


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")

    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SOURCE)
    if not os.path.isfile(src):
        return fail(f"{SOURCE} not found next to main.py")

    # Validate the source file before touching the output directory.
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        return fail(f"{SOURCE} is {size} bytes, over the 1 MiB limit")
    if size == 0:
        return fail(f"{SOURCE} is empty")

    with open(src, "rb") as fh:
        header = fh.read(len(PNG_MAGIC))
    if header != PNG_MAGIC:
        return fail(f"{SOURCE} is not a PNG file (bad header)")

    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, TARGET_NAME)
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
