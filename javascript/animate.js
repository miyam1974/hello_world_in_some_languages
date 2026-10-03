#!/usr/bin/env node
"use strict";

/**
 * 17x9 ターミナル向け Hello World テキストアニメーション（進行波のみ）。
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。
 * Ctrl+C で終了。
 */

const WIDTH = 17;
const HEIGHT = 9;
const TEXT = "Hello, World!";
const FPS = 24;
const FRAME_MS = Math.round(1000 / FPS);
/** 大きいほど遅い。1.25 = 基準の 1.25 倍遅く */
const TIME_SCALE = 1.25;

const ESC = "\x1b[";
const HIDE_CURSOR = `${ESC}?25l`;
const SHOW_CURSOR = `${ESC}?25h`;
const CLEAR_HOME = `${ESC}2J${ESC}H`;
const RESET = `${ESC}0m`;

const DIM = `${ESC}2m`;
const FG = `${ESC}36m`;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function createGrid() {
  return Array.from({ length: HEIGHT }, () => Array(WIDTH).fill(" "));
}

function drawBorder(grid) {
  for (let x = 0; x < WIDTH; x++) {
    grid[0][x] = x === 0 || x === WIDTH - 1 ? "+" : "-";
    grid[HEIGHT - 1][x] = x === 0 || x === WIDTH - 1 ? "+" : "-";
  }
  for (let y = 1; y < HEIGHT - 1; y++) {
    grid[y][0] = "|";
    grid[y][WIDTH - 1] = "|";
  }
}

function placeText(grid, positions) {
  for (const { ch, x, y } of positions) {
    const xi = Math.round(x);
    const yi = Math.round(y);
    if (xi <= 0 || xi >= WIDTH - 1 || yi <= 0 || yi >= HEIGHT - 1) continue;
    grid[yi][xi] = ch === " " ? " " : `\u0001${ch}`;
  }
}

function render(grid) {
  const lines = grid.map((row) =>
    row
      .map((cell) => {
        if (cell.startsWith("\u0001")) return `${FG}${cell.slice(1)}${RESET}`;
        if (cell === "+" || cell === "-" || cell === "|") return `${DIM}${cell}${RESET}`;
        return cell;
      })
      .join(""),
  );
  return CLEAR_HOME + lines.join("\n");
}

/**
 * 左→右へ伝わる進行波。
 * 波面到達後、各文字は (t, i) から Y を決める。
 */
function layout(t) {
  const n = TEXT.length;
  const midY = (HEIGHT - 1) / 2;
  const baseX = Math.floor((WIDTH - n) / 2);
  const positions = [];

  for (let i = 0; i < n; i++) {
    const ch = TEXT[i];
    const x = baseX + i;

    // 波面が左端から右へ進み、通過した文字だけ揺れ始める
    const front = t * 7;
    const behind = front - i;
    let arrive = 0;
    if (behind <= 0) {
      arrive = 0;
    } else if (behind >= 2) {
      arrive = 1;
    } else {
      const p = behind / 2;
      arrive = p * p * (3 - 2 * p);
    }

    // 波面到達からの経過。初動は -Y（上）
    const localT = Math.max(0, t - i / 7);
    const phase = localT * 3.2;
    const amp = 2.0 * arrive;
    const y = midY - Math.sin(phase) * amp;

    positions.push({ ch, x, y });
  }

  return positions;
}

function frame(t) {
  const grid = createGrid();
  drawBorder(grid);
  placeText(grid, layout(t));
  return render(grid);
}

async function main() {
  if (!process.stdout.isTTY) {
    console.error("このデモはインタラクティブなターミナルで実行してください。");
    process.exit(1);
  }

  const restore = () => {
    process.stdout.write(SHOW_CURSOR + RESET + "\n");
  };

  process.on("SIGINT", () => {
    restore();
    process.exit(0);
  });
  process.on("exit", restore);

  process.stdout.write(HIDE_CURSOR);

  const started = Date.now();
  for (;;) {
    const t = (Date.now() - started) / 1000 / TIME_SCALE;
    process.stdout.write(frame(t));
    await sleep(FRAME_MS);
  }
}

main();
