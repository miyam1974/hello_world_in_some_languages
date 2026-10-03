# Rust

`println!` マクロを使う Hello World と、進行波アニメーションです。  
アニメは **所有権・イテレータ・`Result`** を意識して書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `src/main.rs` | シンプルな Hello World |
| `src/animate.rs` | 17×9 進行波アニメ（バイナリ名 `animate`） |
| `out/` | Cargo の生成物（`target-dir`） |

## WSL Ubuntu の環境構築

公式の **rustup** で Rust（`rustc` / `cargo`）を入れます。ビルドに必要な C ツールチェーンも先に入れておきます。

```bash
sudo apt update
sudo apt install -y build-essential curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

インストール後、同じシェルで反映するか、新しいターミナルを開きます。

```bash
source "$HOME/.cargo/env"
```

確認:

```bash
rustc --version
cargo --version
```

## ビルドと実行

```bash
cargo run --bin hello

# アニメ（Ctrl+C で終了）
cargo run --bin animate
```

`hello` の出力:

```text
Hello, World!
```
