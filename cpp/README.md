# C++

標準出力ストリーム `std::cout` を使う Hello World と、進行波アニメーションです。  
アニメは **OOP**（`WaveAnimator` クラスとメンバ関数）で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.cpp` | シンプルな Hello World |
| `animate.cpp` | 17×9 進行波アニメ |
| `out/` | 生成物の出力先 |

## WSL Ubuntu の環境構築

コンパイラ **g++** が必要です（`build-essential` に含まれます）。

```bash
sudo apt update
sudo apt install -y build-essential
```

確認:

```bash
g++ --version
```

## ビルドと実行

```bash
g++ hello.cpp -o out/hello
./out/hello

# アニメ（Ctrl+C で終了）
g++ animate.cpp -o out/animate
./out/animate
```

`hello` の出力:

```text
Hello, World!
```
