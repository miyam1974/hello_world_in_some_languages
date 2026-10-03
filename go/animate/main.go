// 17x9 進行波アニメ（struct + メソッド、スライスと range）
// 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。
package main

import (
	"fmt"
	"math"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

const (
	width     = 17
	height    = 9
	text      = "Hello, World!"
	fps       = 24
	timeScale = 1.25

	esc        = "\x1b["
	hideCursor = esc + "?25l"
	showCursor = esc + "?25h"
	clearHome  = esc + "2J" + esc + "H"
	reset      = esc + "0m"
	dim        = esc + "2m"
	fg = esc + "36m"
)

type style int

const (
	stylePlain style = iota
	styleDim
	styleFg
)

type cell struct {
	ch    byte
	style style
}

type glyph struct {
	ch   byte
	x, y float64
}

type animator struct {
	grid [][]cell
}

func newAnimator() *animator {
	g := make([][]cell, height)
	for y := range g {
		g[y] = make([]cell, width)
	}
	return &animator{grid: g}
}

func (a *animator) clear() {
	for y := range a.grid {
		for x := range a.grid[y] {
			a.grid[y][x] = cell{ch: ' ', style: stylePlain}
		}
	}
}

func (a *animator) drawBorder() {
	for x := 0; x < width; x++ {
		c := byte('-')
		if x == 0 || x == width-1 {
			c = '+'
		}
		a.grid[0][x] = cell{ch: c, style: styleDim}
		a.grid[height-1][x] = cell{ch: c, style: styleDim}
	}
	for y := 1; y < height-1; y++ {
		a.grid[y][0] = cell{ch: '|', style: styleDim}
		a.grid[y][width-1] = cell{ch: '|', style: styleDim}
	}
}

func (a *animator) layout(t float64) []glyph {
	n := len(text)
	midY := float64(height-1) / 2
	baseX := (width - n) / 2
	out := make([]glyph, 0, n)

	for i := 0; i < n; i++ {
		front := t * 7
		behind := front - float64(i)
		var arrive float64
		switch {
		case behind <= 0:
			arrive = 0
		case behind >= 2:
			arrive = 1
		default:
			p := behind / 2
			arrive = p * p * (3 - 2*p)
		}

		localT := math.Max(0, t-float64(i)/7)
		phase := localT * 3.2
		amp := 2.0 * arrive
		y := midY - math.Sin(phase)*amp

		out = append(out, glyph{
			ch: text[i],
			x:  float64(baseX + i),
			y:  y,
		})
	}
	return out
}

func (a *animator) place(glyphs []glyph) {
	for _, g := range glyphs {
		xi := int(math.Round(g.x))
		yi := int(math.Round(g.y))
		if xi <= 0 || xi >= width-1 || yi <= 0 || yi >= height-1 {
			continue
		}
		if g.ch == ' ' {
			a.grid[yi][xi] = cell{ch: ' ', style: stylePlain}
			continue
		}
		a.grid[yi][xi] = cell{ch: g.ch, style: styleFg}
	}
}

func (a *animator) render() {
	var b strings.Builder
	b.WriteString(clearHome)
	for y := 0; y < height; y++ {
		for x := 0; x < width; x++ {
			c := a.grid[y][x]
			switch c.style {
			case styleDim:
				b.WriteString(dim)
			case styleFg:
				b.WriteString(fg)
			}
			b.WriteByte(c.ch)
			if c.style != stylePlain {
				b.WriteString(reset)
			}
		}
		b.WriteByte('\n')
	}
	fmt.Fprint(os.Stdout, b.String())
}

func (a *animator) frame(t float64) {
	a.clear()
	a.drawBorder()
	a.place(a.layout(t))
	a.render()
}

func main() {
	if fi, err := os.Stdout.Stat(); err != nil || (fi.Mode()&os.ModeCharDevice) == 0 {
		fmt.Fprintln(os.Stderr, "このデモはインタラクティブなターミナルで実行してください。")
		os.Exit(1)
	}

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	fmt.Fprint(os.Stdout, hideCursor)
	defer fmt.Fprint(os.Stdout, showCursor+reset+"\n")

	a := newAnimator()
	started := time.Now()
	ticker := time.NewTicker(time.Second / fps)
	defer ticker.Stop()

	for {
		select {
		case <-sigCh:
			return
		case now := <-ticker.C:
			t := now.Sub(started).Seconds() / timeScale
			a.frame(t)
		}
	}
}
