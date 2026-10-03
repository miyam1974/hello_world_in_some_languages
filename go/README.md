# Go

標準パッケージ `fmt` を使う Hello World と、進行波アニメーションです。  
アニメは **`struct` + メソッド** と `time.Ticker` で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `main.go` | シンプルな Hello World |
| `animate/main.go` | 17×9 進行波アニメ |
| `out/` | 生成物の出力先 |

## WSL Ubuntu の環境構築

**Go** コンパイラ／ツールチェーンが必要です。

```bash
sudo apt update
sudo apt install -y golang-go
```

確認:

```bash
go version
```

> Ubuntu のパッケージ版は最新より古いことがあります。より新しい版が必要な場合は [公式のインストール手順](https://go.dev/doc/install) を参照してください。

## ビルドと実行

```bash
go run .
# または
go build -o out/hello .
./out/hello

# アニメ（Ctrl+C で終了）
go run ./animate
# または
go build -o out/animate ./animate
./out/animate
```

`hello` の出力:

```text
Hello, World!
```
