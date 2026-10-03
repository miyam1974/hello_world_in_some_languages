#!/usr/bin/env php
<?php

declare(strict_types=1);

/**
 * 17x9 ターミナル向け Hello World テキストアニメーション（進行波のみ）。
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。
 * Ctrl+C で終了。
 *
 * PHP らしさ: strict_types、配列、array_map、クラス、match。
 */

const WIDTH = 17;
const HEIGHT = 9;
const TEXT = 'Hello, World!';
const FPS = 24;
const FRAME_US = (int) round(1_000_000 / FPS);
/** 大きいほど遅い。1.25 = 基準の 1.25 倍遅く */
const TIME_SCALE = 1.25;

const ESC = "\033[";
const HIDE_CURSOR = ESC . '?25l';
const SHOW_CURSOR = ESC . '?25h';
const CLEAR_HOME = ESC . '2J' . ESC . 'H';
const RESET = ESC . '0m';
const DIM = ESC . '2m';
const FG = ESC . '36m';

final class Glyph
{
    public function __construct(
        public readonly string $ch,
        public readonly float $x,
        public readonly float $y,
    ) {
    }
}

final class WaveAnimator
{
    /** @return list<list<string>> */
    public function emptyGrid(): array
    {
        return array_fill(
            0,
            HEIGHT,
            array_fill(0, WIDTH, ' '),
        );
    }

    /** @param list<list<string>> $grid */
    public function drawBorder(array &$grid): void
    {
        for ($x = 0; $x < WIDTH; $x++) {
            $edge = ($x === 0 || $x === WIDTH - 1) ? '+' : '-';
            $grid[0][$x] = $edge;
            $grid[HEIGHT - 1][$x] = $edge;
        }
        for ($y = 1; $y < HEIGHT - 1; $y++) {
            $grid[$y][0] = '|';
            $grid[$y][WIDTH - 1] = '|';
        }
    }

    /** @return list<Glyph> */
    public function layout(float $t): array
    {
        $n = strlen(TEXT);
        $midY = (HEIGHT - 1) / 2.0;
        $baseX = intdiv(WIDTH - $n, 2);
        $glyphs = [];

        for ($i = 0; $i < $n; $i++) {
            $ch = TEXT[$i];
            $front = $t * 7.0;
            $behind = $front - $i;

            if ($behind <= 0.0) {
                $arrive = 0.0;
            } elseif ($behind >= 2.0) {
                $arrive = 1.0;
            } else {
                $p = $behind / 2.0;
                $arrive = $p * $p * (3.0 - 2.0 * $p);
            }

            $localT = max(0.0, $t - $i / 7.0);
            $phase = $localT * 3.2;
            $amp = 2.0 * $arrive;
            $y = $midY - sin($phase) * $amp;

            $glyphs[] = new Glyph($ch, (float) ($baseX + $i), $y);
        }

        return $glyphs;
    }

    /**
     * @param list<list<string>> $grid
     * @param list<Glyph> $glyphs
     */
    public function placeText(array &$grid, array $glyphs): void
    {
        foreach ($glyphs as $g) {
            $xi = (int) round($g->x);
            $yi = (int) round($g->y);
            if ($xi <= 0 || $xi >= WIDTH - 1 || $yi <= 0 || $yi >= HEIGHT - 1) {
                continue;
            }
            if ($g->ch === ' ') {
                $grid[$yi][$xi] = ' ';
                continue;
            }
            $grid[$yi][$xi] = "\x01" . $g->ch;
        }
    }

    /** @param list<list<string>> $grid */
    public function render(array $grid): string
    {
        $lines = array_map(
            static function (array $row): string {
                $cells = array_map(
                    static function (string $cell): string {
                        return match (true) {
                            str_starts_with($cell, "\x01") => FG . substr($cell, 1) . RESET,
                            $cell === '+' || $cell === '-' || $cell === '|' => DIM . $cell . RESET,
                            default => $cell,
                        };
                    },
                    $row,
                );
                return implode('', $cells);
            },
            $grid,
        );

        return CLEAR_HOME . implode("\n", $lines);
    }

    public function frame(float $t): string
    {
        $grid = $this->emptyGrid();
        $this->drawBorder($grid);
        $this->placeText($grid, $this->layout($t));
        return $this->render($grid);
    }
}

function restoreTerminal(): void
{
    fwrite(STDOUT, SHOW_CURSOR . RESET . "\n");
}

function main(): void
{
    if (!stream_isatty(STDOUT)) {
        fwrite(STDERR, "このデモはインタラクティブなターミナルで実行してください。\n");
        exit(1);
    }

    register_shutdown_function('restoreTerminal');

    if (function_exists('pcntl_async_signals') && function_exists('pcntl_signal')) {
        pcntl_async_signals(true);
        pcntl_signal(SIGINT, static function (): void {
            exit(0);
        });
    }

    fwrite(STDOUT, HIDE_CURSOR);

    $animator = new WaveAnimator();
    $started = hrtime(true);

    while (true) {
        $elapsed = (hrtime(true) - $started) / 1e9 / TIME_SCALE;
        fwrite(STDOUT, $animator->frame($elapsed));
        usleep(FRAME_US);
    }
}

main();
