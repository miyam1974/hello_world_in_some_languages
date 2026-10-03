# Java

JVM 上で動く Hello World と、進行波アニメーションです。  
アニメは **クラスとメソッド中心の OOP** で書いています。

## ファイル

| ファイル | 内容 |
|----------|------|
| `Hello.java` | シンプルな Hello World |
| `Animate.java` | 17×9 進行波アニメ |
| `out/` | 生成物（`.class`）の出力先 |

## WSL Ubuntu の環境構築

**JDK**（`javac` / `java`）が必要です。

```bash
sudo apt update
sudo apt install -y openjdk-25-jdk
```

> 現行の LTS は Java 25 です。パッケージが無い古い Ubuntu では `openjdk-21-jdk` でも構いません。

確認:

```bash
javac -version
java -version
```

## ビルドと実行

```bash
javac -d out Hello.java
java -cp out Hello

# アニメ（Ctrl+C で終了）
javac -d out Animate.java
java -cp out Animate
```

`Hello` の出力:

```text
Hello, World!
```
