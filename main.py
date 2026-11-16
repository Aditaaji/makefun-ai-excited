#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered asset.png to $MAKEFUN_OUTPUT_DIR/entry.png.

Stdlib only. Validates that asset.png is a real PNG under 1 MiB before
copying. Exit 0 on success, 1 on any failure (message to stderr).
"""
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_000_000
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset.png")


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    return 1


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")
    if not os.path.isfile(SRC):
        return fail(f"asset not found: {SRC}")
    try:
        with open(SRC, "rb") as f:
            head = f.read(len(PNG_MAGIC))
            f.seek(0, os.SEEK_END)
            size = f.tell()
    except OSError as exc:
        return fail(f"cannot read {SRC}: {exc}")
    if head != PNG_MAGIC:
        return fail("asset.png is not a valid PNG (bad magic bytes)")
    if size >= MAX_BYTES:
        return fail(f"asset.png is {size} bytes, must be under {MAX_BYTES}")
    dest = os.path.join(out_dir, "entry.png")
    try:
        os.makedirs(out_dir, exist_ok=True)
        shutil.copyfile(SRC, dest)
    except OSError as exc:
        return fail(f"cannot write {dest}: {exc}")
    print(f"wrote {dest} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
