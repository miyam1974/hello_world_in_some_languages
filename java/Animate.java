/**
 * 17x9 進行波アニメ（OOP: クラスとメソッド中心）
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。
 */
import java.util.ArrayList;
import java.util.List;

public class Animate {
    static final int WIDTH = 17;
    static final int HEIGHT = 9;
    static final String TEXT = "Hello, World!";
    static final int FPS = 24;
    static final double TIME_SCALE = 1.25;

    static final String HIDE_CURSOR = "\u001b[?25l";
    static final String SHOW_CURSOR = "\u001b[?25h";
    static final String CLEAR_HOME = "\u001b[2J\u001b[H";
    static final String RESET = "\u001b[0m";
    static final String DIM = "\u001b[2m";
    static final String FG = "\u001b[36m";

    enum Style {
        PLAIN, DIM, FG
    }

    static final class Cell {
        char ch = ' ';
        Style style = Style.PLAIN;
    }

    static final class Glyph {
        final char ch;
        final double x;
        final double y;

        Glyph(char ch, double x, double y) {
            this.ch = ch;
            this.x = x;
            this.y = y;
        }
    }

    static final class WaveAnimator {
        private final Cell[][] grid = new Cell[HEIGHT][WIDTH];

        WaveAnimator() {
            for (int y = 0; y < HEIGHT; y++) {
                for (int x = 0; x < WIDTH; x++) {
                    grid[y][x] = new Cell();
                }
            }
        }

        void clearGrid() {
            for (int y = 0; y < HEIGHT; y++) {
                for (int x = 0; x < WIDTH; x++) {
                    grid[y][x].ch = ' ';
                    grid[y][x].style = Style.PLAIN;
                }
            }
        }

        void drawBorder() {
            for (int x = 0; x < WIDTH; x++) {
                char c = (x == 0 || x == WIDTH - 1) ? '+' : '-';
                grid[0][x].ch = c;
                grid[0][x].style = Style.DIM;
                grid[HEIGHT - 1][x].ch = c;
                grid[HEIGHT - 1][x].style = Style.DIM;
            }
            for (int y = 1; y < HEIGHT - 1; y++) {
                grid[y][0].ch = '|';
                grid[y][0].style = Style.DIM;
                grid[y][WIDTH - 1].ch = '|';
                grid[y][WIDTH - 1].style = Style.DIM;
            }
        }

        List<Glyph> layout(double t) {
            int n = TEXT.length();
            double midY = (HEIGHT - 1) / 2.0;
            int baseX = (WIDTH - n) / 2;
            List<Glyph> glyphs = new ArrayList<>(n);

            for (int i = 0; i < n; i++) {
                double front = t * 7.0;
                double behind = front - i;
                double arrive;
                if (behind <= 0) {
                    arrive = 0;
                } else if (behind >= 2) {
                    arrive = 1;
                } else {
                    double p = behind / 2.0;
                    arrive = p * p * (3.0 - 2.0 * p);
                }

                double localT = Math.max(0, t - i / 7.0);
                double phase = localT * 3.2;
                double amp = 2.0 * arrive;
                double y = midY - Math.sin(phase) * amp;

                glyphs.add(new Glyph(TEXT.charAt(i), baseX + i, y));
            }
            return glyphs;
        }

        void placeText(List<Glyph> glyphs) {
            for (Glyph g : glyphs) {
                int xi = (int) Math.round(g.x);
                int yi = (int) Math.round(g.y);
                if (xi <= 0 || xi >= WIDTH - 1 || yi <= 0 || yi >= HEIGHT - 1) {
                    continue;
                }
                grid[yi][xi].ch = g.ch;
                grid[yi][xi].style = g.ch == ' ' ? Style.PLAIN : Style.FG;
            }
        }

        void render() {
            StringBuilder sb = new StringBuilder();
            sb.append(CLEAR_HOME);
            for (int y = 0; y < HEIGHT; y++) {
                for (int x = 0; x < WIDTH; x++) {
                    Cell c = grid[y][x];
                    switch (c.style) {
                        case DIM -> sb.append(DIM);
                        case FG -> sb.append(FG);
                        default -> {
                        }
                    }
                    sb.append(c.ch);
                    if (c.style != Style.PLAIN) {
                        sb.append(RESET);
                    }
                }
                sb.append('\n');
            }
            System.out.print(sb);
            System.out.flush();
        }

        void frame(double t) {
            clearGrid();
            drawBorder();
            placeText(layout(t));
            render();
        }
    }

    public static void main(String[] args) throws Exception {
        if (System.console() == null) {
            System.err.println("このデモはインタラクティブなターミナルで実行してください。");
            System.exit(1);
        }

        WaveAnimator animator = new WaveAnimator();
        System.out.print(HIDE_CURSOR);
        System.out.flush();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.print(SHOW_CURSOR + RESET + "\n");
            System.out.flush();
        }));

        long started = System.nanoTime();
        long frameNs = 1_000_000_000L / FPS;

        while (true) {
            double t = (System.nanoTime() - started) / 1_000_000_000.0 / TIME_SCALE;
            animator.frame(t);
            Thread.sleep(frameNs / 1_000_000L);
        }
    }
}
