# 機械語 (Machine Code)

CPU が直接実行する **バイト列** としての Hello World です。  
対象は Linux x86-64（システムコールで `write` / `exit` を呼びます）。

> 進行波アニメ（`animate`）は、端末制御と浮動小数演算の都合で上位言語のみ用意しています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.hex` | 実行可能な機械語の 16 進ダンプ（コメント付き） |
| `to_bin.py` | `hello.hex` からバイナリを生成するスクリプト |
| `out/` | 生成物（`hello.bin`）の出力先 |

## WSL Ubuntu の環境構築

変換スクリプトに **Python 3** が必要です。

```bash
sudo apt update
sudo apt install -y python3
```

確認:

```bash
python3 --version
```

## ビルドと実行（WSL / Linux）

```bash
python3 to_bin.py
chmod +x out/hello.bin
./out/hello.bin
```

出力:

```text
Hello, World!
```

> `out/hello.bin` は最小構成の ELF64 実行ファイルです。Windows ネイティブでは動きません。WSL を使ってください。

## 読み方のヒント

- `b8 01 00 00 00` → `mov eax, 1`（sys_write）
- `bf 01 00 00 00` → `mov edi, 1`（stdout）
- `48 be 9c 00 40 00 ...` → メッセージアドレスを RSI へ
- `0f 05` → `syscall`
- `b8 3c 00 00 00` → `mov eax, 60`（sys_exit）

アセンブリ版（同じ内容をニーモニックで書いたもの）は [`../assembly/`](../assembly/) にあります。
