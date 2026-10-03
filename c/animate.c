/*
 * 17x9 進行波アニメ（手続き型: struct + 関数 + 配列）
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。
 */

#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define WIDTH 17
#define HEIGHT 9
#define TEXT "Hello, World!"
#define FPS 24
#define TIME_SCALE 1.25

#define ESC "\x1b["
#define HIDE_CURSOR ESC "?25l"
#define SHOW_CURSOR ESC "?25h"
#define CLEAR_HOME ESC "2J" ESC "H"
#define RESET ESC "0m"
#define DIM ESC "2m"
#define FG ESC "36m"

typedef enum { STYLE_PLAIN, STYLE_DIM, STYLE_FG } Style;

typedef struct {
    char ch;
    Style style;
} Cell;

typedef struct {
    char ch;
    double x;
    double y;
} Glyph;

static volatile sig_atomic_t running = 1;

static void on_signal(int sig) {
    (void)sig;
    running = 0;
}

static void sleep_ms(int ms) {
    struct timespec ts;
    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (long)(ms % 1000) * 1000000L;
    nanosleep(&ts, NULL);
}

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static void clear_grid(Cell grid[HEIGHT][WIDTH]) {
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            grid[y][x].ch = ' ';
            grid[y][x].style = STYLE_PLAIN;
        }
    }
}

static void draw_border(Cell grid[HEIGHT][WIDTH]) {
    for (int x = 0; x < WIDTH; x++) {
        char c = (x == 0 || x == WIDTH - 1) ? '+' : '-';
        grid[0][x].ch = c;
        grid[0][x].style = STYLE_DIM;
        grid[HEIGHT - 1][x].ch = c;
        grid[HEIGHT - 1][x].style = STYLE_DIM;
    }
    for (int y = 1; y < HEIGHT - 1; y++) {
        grid[y][0].ch = '|';
        grid[y][0].style = STYLE_DIM;
        grid[y][WIDTH - 1].ch = '|';
        grid[y][WIDTH - 1].style = STYLE_DIM;
    }
}

static void layout(double t, Glyph *out, int *count) {
    const int n = (int)strlen(TEXT);
    const double mid_y = (HEIGHT - 1) / 2.0;
    const int base_x = (WIDTH - n) / 2;

    for (int i = 0; i < n; i++) {
        double front = t * 7.0;
        double behind = front - i;
        double arrive;
        if (behind <= 0.0) {
            arrive = 0.0;
        } else if (behind >= 2.0) {
            arrive = 1.0;
        } else {
            double p = behind / 2.0;
            arrive = p * p * (3.0 - 2.0 * p);
        }

        double local_t = t - i / 7.0;
        if (local_t < 0.0) {
            local_t = 0.0;
        }
        double phase = local_t * 3.2;
        double amp = 2.0 * arrive;
        double y = mid_y - sin(phase) * amp;

        out[i].ch = TEXT[i];
        out[i].x = base_x + i;
        out[i].y = y;
    }
    *count = n;
}

static void place_text(Cell grid[HEIGHT][WIDTH], const Glyph *glyphs, int count) {
    for (int i = 0; i < count; i++) {
        int xi = (int)lround(glyphs[i].x);
        int yi = (int)lround(glyphs[i].y);
        if (xi <= 0 || xi >= WIDTH - 1 || yi <= 0 || yi >= HEIGHT - 1) {
            continue;
        }
        grid[yi][xi].ch = glyphs[i].ch;
        grid[yi][xi].style = glyphs[i].ch == ' ' ? STYLE_PLAIN : STYLE_FG;
    }
}

static void render(const Cell grid[HEIGHT][WIDTH]) {
    fputs(CLEAR_HOME, stdout);
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            const Cell *c = &grid[y][x];
            switch (c->style) {
            case STYLE_DIM:
                fputs(DIM, stdout);
                break;
            case STYLE_FG:
                fputs(FG, stdout);
                break;
            default:
                break;
            }
            fputc(c->ch, stdout);
            if (c->style != STYLE_PLAIN) {
                fputs(RESET, stdout);
            }
        }
        fputc('\n', stdout);
    }
    fflush(stdout);
}

int main(void) {
    if (!isatty(STDOUT_FILENO)) {
        fputs("このデモはインタラクティブなターミナルで実行してください。\n", stderr);
        return 1;
    }

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);

    fputs(HIDE_CURSOR, stdout);
    fflush(stdout);

    Cell grid[HEIGHT][WIDTH];
    Glyph glyphs[32];
    int count = 0;
    double started = now_sec();
    const int frame_ms = (1000 + FPS - 1) / FPS;

    while (running) {
        double t = (now_sec() - started) / TIME_SCALE;
        clear_grid(grid);
        draw_border(grid);
        layout(t, glyphs, &count);
        place_text(grid, glyphs, count);
        render(grid);
        sleep_ms(frame_ms);
    }

    fputs(SHOW_CURSOR RESET "\n", stdout);
    fflush(stdout);
    return 0;
}
