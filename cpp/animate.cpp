/*
 * 17x9 進行波アニメ（OOP: クラスとメンバ関数）
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。
 */

#include <cmath>
#include <csignal>
#include <chrono>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

#include <unistd.h>

namespace {

constexpr int kWidth = 17;
constexpr int kHeight = 9;
constexpr const char *kText = "Hello, World!";
constexpr int kFps = 24;
constexpr double kTimeScale = 1.25;

constexpr const char *kEsc = "\x1b[";
constexpr const char *kHideCursor = "\x1b[?25l";
constexpr const char *kShowCursor = "\x1b[?25h";
constexpr const char *kClearHome = "\x1b[2J\x1b[H";
constexpr const char *kReset = "\x1b[0m";
constexpr const char *kDim = "\x1b[2m";
constexpr const char *kFg = "\x1b[36m";

volatile std::sig_atomic_t g_running = 1;

void onSignal(int) { g_running = 0; }

enum class Style { Plain, Dim, Fg };

struct Cell {
    char ch = ' ';
    Style style = Style::Plain;
};

struct Glyph {
    char ch;
    double x;
    double y;
};

class WaveAnimator {
public:
    WaveAnimator() : grid_(kHeight, std::vector<Cell>(kWidth)) {}

    void clearGrid() {
        for (auto &row : grid_) {
            for (auto &cell : row) {
                cell = Cell{};
            }
        }
    }

    void drawBorder() {
        for (int x = 0; x < kWidth; ++x) {
            const char c = (x == 0 || x == kWidth - 1) ? '+' : '-';
            grid_[0][x] = {c, Style::Dim};
            grid_[kHeight - 1][x] = {c, Style::Dim};
        }
        for (int y = 1; y < kHeight - 1; ++y) {
            grid_[y][0] = {'|', Style::Dim};
            grid_[y][kWidth - 1] = {'|', Style::Dim};
        }
    }

    std::vector<Glyph> layout(double t) const {
        const std::string text = kText;
        const int n = static_cast<int>(text.size());
        const double midY = (kHeight - 1) / 2.0;
        const int baseX = (kWidth - n) / 2;
        std::vector<Glyph> glyphs;
        glyphs.reserve(n);

        for (int i = 0; i < n; ++i) {
            const double front = t * 7.0;
            const double behind = front - i;
            double arrive;
            if (behind <= 0.0) {
                arrive = 0.0;
            } else if (behind >= 2.0) {
                arrive = 1.0;
            } else {
                const double p = behind / 2.0;
                arrive = p * p * (3.0 - 2.0 * p);
            }

            const double localT = std::max(0.0, t - i / 7.0);
            const double phase = localT * 3.2;
            const double amp = 2.0 * arrive;
            const double y = midY - std::sin(phase) * amp;

            glyphs.push_back(Glyph{
                text[static_cast<size_t>(i)],
                static_cast<double>(baseX + i),
                y,
            });
        }
        return glyphs;
    }

    void placeText(const std::vector<Glyph> &glyphs) {
        for (const auto &g : glyphs) {
            const int xi = static_cast<int>(std::lround(g.x));
            const int yi = static_cast<int>(std::lround(g.y));
            if (xi <= 0 || xi >= kWidth - 1 || yi <= 0 || yi >= kHeight - 1) {
                continue;
            }
            grid_[yi][xi] = {g.ch, g.ch == ' ' ? Style::Plain : Style::Fg};
        }
    }

    void render() const {
        std::cout << kClearHome;
        for (const auto &row : grid_) {
            for (const auto &cell : row) {
                switch (cell.style) {
                case Style::Dim:
                    std::cout << kDim;
                    break;
                case Style::Fg:
                    std::cout << kFg;
                    break;
                default:
                    break;
                }
                std::cout << cell.ch;
                if (cell.style != Style::Plain) {
                    std::cout << kReset;
                }
            }
            std::cout << '\n';
        }
        std::cout.flush();
    }

    void frame(double t) {
        clearGrid();
        drawBorder();
        placeText(layout(t));
        render();
    }

private:
    std::vector<std::vector<Cell>> grid_;
};

}  // namespace

int main() {
    if (!isatty(STDOUT_FILENO)) {
        std::cerr << "このデモはインタラクティブなターミナルで実行してください。\n";
        return 1;
    }

    std::signal(SIGINT, onSignal);
    std::signal(SIGTERM, onSignal);

    std::cout << kHideCursor << std::flush;
    WaveAnimator animator;
    const auto started = std::chrono::steady_clock::now();
    const auto frameMs = std::chrono::milliseconds((1000 + kFps - 1) / kFps);

    while (g_running) {
        const auto elapsed = std::chrono::steady_clock::now() - started;
        const double t =
            std::chrono::duration<double>(elapsed).count() / kTimeScale;
        animator.frame(t);
        std::this_thread::sleep_for(frameMs);
    }

    std::cout << kShowCursor << kReset << '\n' << std::flush;
    return 0;
}
