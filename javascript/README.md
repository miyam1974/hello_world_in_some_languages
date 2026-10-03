# JavaScript (Node.js)

ランタイム **Node.js** 上で動かす Hello World です。  
コンパイルは不要で、ソースをそのまま解釈実行します。

## ファイル

| ファイル | 内容 |
|----------|------|
| `hello.js` | シンプルな Hello World |
| `animate.js` | 17×9 枠の進行波テキストアニメーション |

## WSL Ubuntu の環境構築

**Node.js** が必要です。

```bash
sudo apt update
sudo apt install -y nodejs npm
```

確認:

```bash
node --version
npm --version
```

> Ubuntu のパッケージ版は最新より古いことがあります。より新しい版が必要な場合は [NodeSource](https://github.com/nodesource/distributions) や [nvm](https://github.com/nvm-sh/nvm) を参照してください。

## 実行

```bash
# シンプル版
node hello.js

# アニメーションデモ（17×9、Ctrl+C で終了）
node animate.js
```

`hello.js` の出力:

```text
Hello, World!
```

`animate.js` は、正弦波が左端から右へ伝わって各文字が上下する動きです。
