# アセンブリ (Assembly)

機械語をニーモニックで書いた Hello World です。  
対象は Linux x86-64 / NASM。

> 進行波アニメ（`animate`）は、端末制御と浮動小数演算の都合で上位言語のみ用意しています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.asm` | NASM ソース |
| `out/` | 生成物（`hello.o`, `hello`）の出力先 |

## WSL Ubuntu の環境構築

アセンブラ **NASM** とリンカ **ld**（`binutils` に含まれる）が必要です。

```bash
sudo apt update
sudo apt install -y nasm binutils
```

確認:

```bash
nasm -v
ld --version
```

## ビルドと実行（WSL / Linux）

```bash
# 1. アセンブル → オブジェクトファイル（まだ実行不可）
nasm -f elf64 hello.asm -o out/hello.o

# 2. リンク → 実行ファイル
ld out/hello.o -o out/hello

# 3. 実行（.o ではなくリンク後の out/hello）
./out/hello
```

出力:

```text
Hello, World!
```

## 機械語との対応

このソースの命令列は [`../machine/hello.hex`](../machine/hello.hex) のコード部と同じ意味です。

| アセンブリ | 機械語（例） |
|------------|--------------|
| `mov rax, 1` | `b8 01 00 00 00` |
| `syscall` | `0f 05` |
| `mov rax, 60` | `b8 3c 00 00 00` |
