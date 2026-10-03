# Scala

JVM 上で動く Hello World と、進行波アニメーションです。  
アニメは **関数型寄り**（`case class` / `map` / `zipWithIndex` / 不変コレクション）で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `Hello.scala` | シンプルな Hello World |
| `Animate.scala` | 17×9 進行波アニメ |
| `out/` | 生成物（`.class`）の出力先 |

## WSL Ubuntu の環境構築

**JDK** と **Scala**（`scalac` / `scala`）が必要です。

```bash
sudo apt update
sudo apt install -y openjdk-25-jdk scala
```

> 現行の LTS は Java 25 です。パッケージが無い古い Ubuntu では `openjdk-21-jdk` でも構いません。

確認:

```bash
javac -version
scalac -version
scala -version
```

> Ubuntu のパッケージ版は最新の Scala 3 より古いことがあります（多くは Scala 2）。より新しい版が必要な場合は [公式のインストール手順](https://www.scala-lang.org/download/) を参照してください。

## ビルドと実行

```bash
scalac -d out Hello.scala
scala -cp out Hello

# アニメ（Ctrl+C で終了）
scalac -d out Animate.scala
scala -cp out Animate
```

`Hello` の出力:

```text
Hello, World!
```
