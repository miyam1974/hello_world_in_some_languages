/**
 * 17x9 進行波アニメ（関数型寄り: case class / map / zipWithIndex）
 * 左上 (0,0)、+Y は下。波の初動は -Y（上）。Ctrl+C で終了。
 */
object Animate {
  val Width = 17
  val Height = 9
  val Text = "Hello, World!"
  val Fps = 24
  val TimeScale = 1.25

  val HideCursor = "\u001b[?25l"
  val ShowCursor = "\u001b[?25h"
  val ClearHome = "\u001b[2J\u001b[H"
  val Reset = "\u001b[0m"
  val Dim = "\u001b[2m"
  val Fg = "\u001b[36m"

  sealed trait Style
  case object Plain extends Style
  case object DimStyle extends Style
  case object FgStyle extends Style

  case class Cell(ch: Char = ' ', style: Style = Plain)
  case class Glyph(ch: Char, x: Double, y: Double)

  def arriveAt(behind: Double): Double =
    if (behind <= 0) 0.0
    else if (behind >= 2) 1.0
    else {
      val p = behind / 2.0
      p * p * (3.0 - 2.0 * p)
    }

  def layout(t: Double): Vector[Glyph] = {
    val n = Text.length
    val midY = (Height - 1) / 2.0
    val baseX = (Width - n) / 2

    Text.zipWithIndex.map { case (ch, i) =>
      val front = t * 7.0
      val behind = front - i
      val arrive = arriveAt(behind)
      val localT = math.max(0.0, t - i / 7.0)
      val phase = localT * 3.2
      val amp = 2.0 * arrive
      val y = midY - math.sin(phase) * amp
      Glyph(ch, baseX + i, y)
    }.toVector
  }

  def emptyGrid: Vector[Vector[Cell]] =
    Vector.fill(Height, Width)(Cell())

  def drawBorder(grid: Vector[Vector[Cell]]): Vector[Vector[Cell]] = {
    var g = grid
    for (x <- 0 until Width) {
      val c = if (x == 0 || x == Width - 1) '+' else '-'
      g = g.updated(0, g(0).updated(x, Cell(c, DimStyle)))
      g = g.updated(Height - 1, g(Height - 1).updated(x, Cell(c, DimStyle)))
    }
    for (y <- 1 until Height - 1) {
      g = g.updated(y, g(y).updated(0, Cell('|', DimStyle)))
      g = g.updated(y, g(y).updated(Width - 1, Cell('|', DimStyle)))
    }
    g
  }

  def placeText(grid: Vector[Vector[Cell]], glyphs: Vector[Glyph]): Vector[Vector[Cell]] =
    glyphs.foldLeft(grid) { (g, glyph) =>
      val xi = math.round(glyph.x).toInt
      val yi = math.round(glyph.y).toInt
      if (xi <= 0 || xi >= Width - 1 || yi <= 0 || yi >= Height - 1) g
      else {
        val style = if (glyph.ch == ' ') Plain else FgStyle
        g.updated(yi, g(yi).updated(xi, Cell(glyph.ch, style)))
      }
    }

  def render(grid: Vector[Vector[Cell]]): String = {
    val sb = new StringBuilder(ClearHome)
    for (row <- grid) {
      for (cell <- row) {
        cell.style match {
          case DimStyle => sb.append(Dim)
          case FgStyle  => sb.append(Fg)
          case Plain    => ()
        }
        sb.append(cell.ch)
        if (cell.style != Plain) sb.append(Reset)
      }
      sb.append('\n')
    }
    sb.toString
  }

  def frame(t: Double): String = {
    val glyphs = layout(t)
    val grid = placeText(drawBorder(emptyGrid), glyphs)
    render(grid)
  }

  def main(args: Array[String]): Unit = {
    if (System.console() == null) {
      System.err.println("このデモはインタラクティブなターミナルで実行してください。")
      sys.exit(1)
    }

    print(HideCursor)
    sys.addShutdownHook {
      print(ShowCursor + Reset + "\n")
    }

    val started = System.nanoTime()
    val frameNs = 1000000000L / Fps

    while (true) {
      val t = (System.nanoTime() - started) / 1e9 / TimeScale
      print(frame(t))
      Thread.sleep(frameNs / 1000000L)
    }
  }
}
