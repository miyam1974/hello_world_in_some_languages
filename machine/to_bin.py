#!/usr/bin/env python3
"""Convert a commented hex dump into a binary file under out/."""

from __future__ import annotations

import re
import sys
from pathlib import Path


HEX_BYTE = re.compile(r"\b([0-9a-fA-F]{2})\b")
HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE / "hello.hex"
DEFAULT_DST = HERE / "out" / "hello.bin"


def hex_to_bytes(text: str) -> bytes:
    out = bytearray()
    for line in text.splitlines():
        code = line.split("#", 1)[0]
        out.extend(int(match.group(1), 16) for match in HEX_BYTE.finditer(code))
    return bytes(out)


def main() -> int:
    if len(sys.argv) > 3:
        print(
            f"Usage: {sys.argv[0]} [input.hex] [output.bin]\n"
            f"Defaults: {DEFAULT_SRC.name} -> {DEFAULT_DST.relative_to(HERE)}",
            file=sys.stderr,
        )
        return 1

    src = Path(sys.argv[1]) if len(sys.argv) >= 2 else DEFAULT_SRC
    dst = Path(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_DST

    if not src.is_absolute():
        src = (Path.cwd() / src).resolve()
    if not dst.is_absolute():
        dst = (Path.cwd() / dst).resolve()

    data = hex_to_bytes(src.read_text(encoding="utf-8"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    print(f"Wrote {len(data)} bytes -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
