//! 17x9 進行波アニメ（所有権・イテレータ・Result）
//! 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。

use std::io::{self, IsTerminal, Write};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

const WIDTH: usize = 17;
const HEIGHT: usize = 9;
const TEXT: &str = "Hello, World!";
const FPS: u64 = 24;
const TIME_SCALE: f64 = 1.25;

const HIDE_CURSOR: &str = "\x1b[?25l";
const SHOW_CURSOR: &str = "\x1b[?25h";
const CLEAR_HOME: &str = "\x1b[2J\x1b[H";
const RESET: &str = "\x1b[0m";
const DIM: &str = "\x1b[2m";
const FG: &str = "\x1b[36m";

#[derive(Clone, Copy)]
enum Style {
    Plain,
    Dim,
    Fg,
}

#[derive(Clone, Copy)]
struct Cell {
    ch: char,
    style: Style,
}

impl Default for Cell {
    fn default() -> Self {
        Self {
            ch: ' ',
            style: Style::Plain,
        }
    }
}

struct Glyph {
    ch: char,
    x: f64,
    y: f64,
}

fn smoothstep_arrive(behind: f64) -> f64 {
    if behind <= 0.0 {
        0.0
    } else if behind >= 2.0 {
        1.0
    } else {
        let p = behind / 2.0;
        p * p * (3.0 - 2.0 * p)
    }
}

fn layout(t: f64) -> Vec<Glyph> {
    let n = TEXT.chars().count();
    let mid_y = (HEIGHT - 1) as f64 / 2.0;
    let base_x = (WIDTH - n) / 2;

    TEXT.chars()
        .enumerate()
        .map(|(i, ch)| {
            let front = t * 7.0;
            let behind = front - i as f64;
            let arrive = smoothstep_arrive(behind);
            let local_t = (t - i as f64 / 7.0).max(0.0);
            let phase = local_t * 3.2;
            let amp = 2.0 * arrive;
            let y = mid_y - phase.sin() * amp;
            Glyph {
                ch,
                x: (base_x + i) as f64,
                y,
            }
        })
        .collect()
}

fn clear_grid(grid: &mut [[Cell; WIDTH]; HEIGHT]) {
    for row in grid.iter_mut() {
        for cell in row.iter_mut() {
            *cell = Cell::default();
        }
    }
}

fn draw_border(grid: &mut [[Cell; WIDTH]; HEIGHT]) {
    for x in 0..WIDTH {
        let c = if x == 0 || x == WIDTH - 1 { '+' } else { '-' };
        grid[0][x] = Cell {
            ch: c,
            style: Style::Dim,
        };
        grid[HEIGHT - 1][x] = Cell {
            ch: c,
            style: Style::Dim,
        };
    }
    for y in 1..HEIGHT - 1 {
        grid[y][0] = Cell {
            ch: '|',
            style: Style::Dim,
        };
        grid[y][WIDTH - 1] = Cell {
            ch: '|',
            style: Style::Dim,
        };
    }
}

fn place_text(grid: &mut [[Cell; WIDTH]; HEIGHT], glyphs: &[Glyph]) {
    for g in glyphs {
        let xi = g.x.round() as isize;
        let yi = g.y.round() as isize;
        if xi <= 0 || xi >= WIDTH as isize - 1 || yi <= 0 || yi >= HEIGHT as isize - 1 {
            continue;
        }
        let style = if g.ch == ' ' {
            Style::Plain
        } else {
            Style::Fg
        };
        grid[yi as usize][xi as usize] = Cell { ch: g.ch, style };
    }
}

fn render(out: &mut impl Write, grid: &[[Cell; WIDTH]; HEIGHT]) -> io::Result<()> {
    write!(out, "{CLEAR_HOME}")?;
    for row in grid {
        for cell in row {
            match cell.style {
                Style::Dim => write!(out, "{DIM}")?,
                Style::Fg => write!(out, "{FG}")?,
                Style::Plain => {}
            }
            write!(out, "{}", cell.ch)?;
            if !matches!(cell.style, Style::Plain) {
                write!(out, "{RESET}")?;
            }
        }
        writeln!(out)?;
    }
    out.flush()
}

fn frame(out: &mut impl Write, grid: &mut [[Cell; WIDTH]; HEIGHT], t: f64) -> io::Result<()> {
    clear_grid(grid);
    draw_border(grid);
    let glyphs = layout(t);
    place_text(grid, &glyphs);
    render(out, grid)
}

fn main() -> io::Result<()> {
    if !io::stdout().is_terminal() {
        eprintln!("このデモはインタラクティブなターミナルで実行してください。");
        std::process::exit(1);
    }

    let running = Arc::new(AtomicBool::new(true));
    {
        let flag = Arc::clone(&running);
        ctrlc::set_handler(move || {
            flag.store(false, Ordering::SeqCst);
        })
        .expect("SIGINT ハンドラを設定できません");
    }

    let mut out = io::stdout();
    write!(out, "{HIDE_CURSOR}")?;
    out.flush()?;

    let mut grid = [[Cell::default(); WIDTH]; HEIGHT];
    let started = Instant::now();
    let frame_ms = Duration::from_millis(1000 / FPS);

    while running.load(Ordering::SeqCst) {
        let t = started.elapsed().as_secs_f64() / TIME_SCALE;
        frame(&mut out, &mut grid, t)?;
        thread::sleep(frame_ms);
    }

    write!(out, "{SHOW_CURSOR}{RESET}\n")?;
    out.flush()?;
    Ok(())
}
