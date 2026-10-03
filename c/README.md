# C

標準ライブラリの `printf` を使う Hello World と、進行波アニメーションです。  
アニメは **手続き型**（`struct` + 関数 + 配列）で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.c` | シンプルな Hello World |
| `animate.c` | 17×9 進行波アニメ |
| `out/` | 生成物の出力先 |

## WSL Ubuntu の環境構築

コンパイラ **GCC** が必要です（`build-essential` に含まれます）。

```bash
sudo apt update
sudo apt install -y build-essential
```

確認:

```bash
gcc --version
```

## ビルドと実行

```bash
gcc hello.c -o out/hello
./out/hello

# アニメ（-lm で数学ライブラリをリンク、Ctrl+C で終了）
gcc animate.c -o out/animate -lm
./out/animate
```

`hello` の出力:

```text
Hello, World!
```
