#!/usr/bin/env python3
"""Render Hello / wave terminal captures (PNG + animated SVG) for README."""

from __future__ import annotations

import html
import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"

WIDTH = 17
HEIGHT = 9
TEXT = "Hello, World!"
CELL_W = 12
CELL_H = 20
PAD = 14
TITLE_H = 26

BG = "#121216"
BORDER = "#5a5a64"
FG = "#50c8d2"
DIM = "#6e6e78"
TITLE = "#b4b4be"


def smoothstep_arrive(behind: float) -> float:
    if behind <= 0:
        return 0.0
    if behind >= 2:
        return 1.0
    p = behind / 2.0
    return p * p * (3.0 - 2.0 * p)


def layout(t: float, amp_scale: float = 1.0) -> list[tuple[str, float, float]]:
    n = len(TEXT)
    mid_y = (HEIGHT - 1) / 2.0
    base_x = (WIDTH - n) // 2
    out = []
    for i, ch in enumerate(TEXT):
        front = t * 7.0
        behind = front - i
        arrive = smoothstep_arrive(behind)
        local_t = max(0.0, t - i / 7.0)
        phase = local_t * 3.2
        amp = 2.0 * arrive * amp_scale
        y = mid_y - math.sin(phase) * amp
        out.append((ch, float(base_x + i), y))
    return out


def make_grid(t: float | None, amp_scale: float = 1.0) -> list[list[tuple[str, str]]]:
    grid = [[(" ", "plain") for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x in range(WIDTH):
        c = "+" if x in (0, WIDTH - 1) else "-"
        grid[0][x] = (c, "dim")
        grid[HEIGHT - 1][x] = (c, "dim")
    for y in range(1, HEIGHT - 1):
        grid[y][0] = ("|", "dim")
        grid[y][WIDTH - 1] = ("|", "dim")

    if t is None or amp_scale <= 0.0:
        n = len(TEXT)
        mid_y = (HEIGHT - 1) // 2
        base_x = (WIDTH - n) // 2
        for i, ch in enumerate(TEXT):
            grid[mid_y][base_x + i] = (ch, "fg")
    else:
        for ch, x, y in layout(t, amp_scale):
            xi = int(round(x))
            yi = int(round(y))
            if 0 < xi < WIDTH - 1 and 0 < yi < HEIGHT - 1:
                style = "plain" if ch == " " else "fg"
                grid[yi][xi] = (ch, style)
    return grid


def _capture_segments() -> tuple[float, float, float]:
    """hold, t_wave_end, settle — keep the loop short for README."""
    phase_speed = 3.2
    period = 2.0 * math.pi / phase_speed
    # Arrive, one short wave beat, then settle back to rest.
    t_wave_end = 1.55 + period * 0.65
    hold = 0.1
    settle = 0.28
    return hold, t_wave_end, settle


def capture_timeline(u: float) -> tuple[float, float]:
    """Map loop time u∈[0, total) → (t, amp_scale). Starts/ends at rest."""
    hold, t_wave_end, settle = _capture_segments()
    total = hold + t_wave_end + settle + hold
    u = u % total

    if u < hold:
        return 0.0, 0.0
    u -= hold
    if u < t_wave_end:
        return u, 1.0
    u -= t_wave_end
    if u < settle:
        p = u / settle
        fade = 1.0 - (p * p * (3.0 - 2.0 * p))
        return t_wave_end, fade
    return 0.0, 0.0


def capture_loop_duration() -> float:
    hold, t_wave_end, settle = _capture_segments()
    return hold + t_wave_end + settle + hold


def style_color(style: str) -> str:
    return {
        "plain": "#dcdcdc",
        "dim": DIM,
        "fg": FG,
    }[style]


def canvas_size() -> tuple[int, int]:
    return PAD * 2 + WIDTH * CELL_W, PAD * 2 + TITLE_H + HEIGHT * CELL_H


def grid_to_svg(grid: list[list[tuple[str, str]]], title: str, frame_id: str | None = None) -> str:
    img_w, img_h = canvas_size()
    ox = PAD
    oy = PAD + TITLE_H
    parts = [
        f'<rect width="{img_w}" height="{img_h}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>',
        f'<text x="{PAD}" y="22" fill="{TITLE}" font-family="ui-monospace, Consolas, monospace" font-size="13">{html.escape(title)}</text>',
    ]
    group_open = f'<g id="{frame_id}">' if frame_id else "<g>"
    parts.append(group_open)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ch, style = grid[y][x]
            if ch == " ":
                continue
            cx = ox + x * CELL_W + CELL_W / 2
            cy = oy + y * CELL_H + CELL_H / 2 + 4
            parts.append(
                f'<text x="{cx:.1f}" y="{cy:.1f}" fill="{style_color(style)}" '
                f'font-family="ui-monospace, Consolas, monospace" font-size="14" '
                f'text-anchor="middle">{html.escape(ch)}</text>'
            )
    parts.append("</g>")
    return "\n".join(parts)


def write_svg(path: Path, inner: str) -> None:
    img_w, img_h = canvas_size()
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" '
        f'viewBox="0 0 {img_w} {img_h}">\n{inner}\n</svg>\n'
    )
    path.write_text(svg, encoding="utf-8")


def write_animated_svg(path: Path, frames: list[str], duration: float) -> None:
    """Loop frames with discrete opacity; end state matches start (no blank gap)."""
    img_w, img_h = canvas_size()
    n = len(frames)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_w}" height="{img_h}" '
        f'viewBox="0 0 {img_w} {img_h}">',
        f'<rect width="{img_w}" height="{img_h}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>',
        f'<text x="{PAD}" y="22" fill="{TITLE}" font-family="ui-monospace, Consolas, monospace" font-size="13">wave animate</text>',
    ]
    for i, body in enumerate(frames):
        # At keyTime=1, restore frame 0 so the loop restart has no empty flash.
        vals = ";".join("1" if j == i else "0" for j in range(n))
        vals += ";1" if i == 0 else ";0"
        keys = ";".join(f"{j / n:.6f}" for j in range(n)) + ";1"
        parts.append(f'<g id="f{i}" opacity="{"1" if i == 0 else "0"}">')
        parts.append(body)
        parts.append(
            f'<animate attributeName="opacity" dur="{duration:.3f}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="{vals}" keyTimes="{keys}"/>'
        )
        parts.append("</g>")
    parts.append("</svg>\n")
    path.write_text("\n".join(parts), encoding="utf-8")


def frame_texts_only(grid: list[list[tuple[str, str]]]) -> str:
    """SVG content for cells only (no chrome)."""
    ox = PAD
    oy = PAD + TITLE_H
    parts = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ch, style = grid[y][x]
            if ch == " ":
                continue
            cx = ox + x * CELL_W + CELL_W / 2
            cy = oy + y * CELL_H + CELL_H / 2 + 4
            parts.append(
                f'<text x="{cx:.1f}" y="{cy:.1f}" fill="{style_color(style)}" '
                f'font-family="ui-monospace, Consolas, monospace" font-size="14" '
                f'text-anchor="middle">{html.escape(ch)}</text>'
            )
    return "\n".join(parts)


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png_from_svg_like(path: Path, grid: list[list[tuple[str, str]]], title: str) -> None:
    """Rasterize with a tiny bitmap font for reliable PNG embeds."""
    font = {
        " ": ["00000"] * 7,
        "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
        ",": ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
        "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
        "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
        "|": ["00100", "00100", "00100", "00100", "00100", "00100", "00100"],
        "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
        "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
        "a": ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
        "e": ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
        "i": ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
        "l": ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
        "m": ["00000", "00000", "11010", "10101", "10101", "10101", "10101"],
        "n": ["00000", "00000", "10110", "11001", "10001", "10001", "10001"],
        "o": ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
        "r": ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
        "t": ["00100", "00100", "01110", "00100", "00100", "00100", "00010"],
        "v": ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
        "d": ["00001", "00001", "01101", "10011", "10001", "10001", "01110"],
        "w": ["00000", "00000", "10001", "10101", "10101", "10101", "01010"],
    }

    def bmp(ch: str) -> list[str]:
        return font.get(ch, ["11111", "10001", "10001", "10001", "10001", "10001", "11111"])

    def rgb(style: str) -> tuple[int, int, int]:
        c = style_color(style).lstrip("#")
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

    img_w, img_h = canvas_size()
    bg = (18, 18, 22)
    pixels = [[(*bg, 255) for _ in range(img_w)] for _ in range(img_h)]

    def plot(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < img_w and 0 <= y < img_h:
            pixels[y][x] = (*color, 255)

    tx, ty = PAD, 8
    for ch in title:
        for row_i, row in enumerate(bmp(ch)):
            for col_i, bit in enumerate(row):
                if bit == "1":
                    for dy in range(2):
                        for dx in range(2):
                            plot(tx + col_i * 2 + dx, ty + row_i * 2 + dy, (180, 180, 190))
        tx += 12

    ox, oy = PAD, PAD + TITLE_H
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ch, style = grid[y][x]
            color = rgb(style)
            for row_i, row in enumerate(bmp(ch)):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        for dy in range(2):
                            for dx in range(2):
                                plot(ox + x * CELL_W + 3 + col_i * 2 + dx, oy + y * CELL_H + 4 + row_i * 2 + dy, color)

    for x in range(img_w):
        plot(x, 0, (90, 90, 100))
        plot(x, img_h - 1, (90, 90, 100))
    for y in range(img_h):
        plot(0, y, (90, 90, 100))
        plot(img_w - 1, y, (90, 90, 100))

    raw = bytearray()
    for row in pixels:
        raw.append(0)
        for r, g, b, a in row:
            raw.extend((r, g, b, a))
    compressed = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", img_w, img_h, 8, 6, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", compressed)
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    hello_grid = make_grid(None)
    write_png_from_svg_like(OUT / "hello.png", hello_grid, "Hello, World!")
    write_svg(OUT / "hello.svg", grid_to_svg(hello_grid, "Hello, World!"))

    # Full cycle in the loop: rest → arrive → wave → settle → rest.
    duration = capture_loop_duration()
    frame_count = 40
    frame_bodies = []
    still_grid = None
    for i in range(frame_count):
        t, amp_scale = capture_timeline(duration * (i / frame_count))
        grid = make_grid(t, amp_scale)
        frame_bodies.append(frame_texts_only(grid))
        # Still: mid-wave after arrival (not the rest pose).
        if still_grid is None and amp_scale >= 1.0 and t >= 2.0:
            still_grid = grid
    write_png_from_svg_like(OUT / "wave.png", still_grid or make_grid(2.0), "wave animate")
    write_animated_svg(OUT / "wave.svg", frame_bodies, duration=duration)

    print(f"Wrote {OUT / 'hello.png'}")
    print(f"Wrote {OUT / 'hello.svg'}")
    print(f"Wrote {OUT / 'wave.png'}")
    print(f"Wrote {OUT / 'wave.svg'}")


if __name__ == "__main__":
    main()
