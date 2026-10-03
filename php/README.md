# PHP

CLI の **PHP** で動かす Hello World と、進行波アニメーションです。  
アニメは **`declare(strict_types=1)`・配列・`array_map`・クラス・`match`** で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.php` | シンプルな Hello World |
| `animate.php` | 17×9 枠の進行波テキストアニメーション |

## WSL Ubuntu の環境構築

**PHP CLI**（PHP 8 以降想定）が必要です。

```bash
sudo apt update
sudo apt install -y php-cli
```

確認:

```bash
php --version
```

> Ubuntu のパッケージ版は最新より古いことがあります。より新しい版が必要な場合は [公式のインストール手順](https://www.php.net/manual/ja/install.php) を参照してください。

## 実行

```bash
# シンプル版
php hello.php

# アニメーションデモ（17×9、Ctrl+C で終了）
php animate.php
```

`hello.php` の出力:

```text
Hello, World!
```

`animate.php` は、正弦波が左端から右へ伝わって各文字が上下する動きです。  
`pcntl` 拡張がある環境では Ctrl+C でカーソルを戻して終了します（無くても shutdown 時に復元します）。
