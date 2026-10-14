# The banner at the top of the organisation profile: the name on the left, the shelf on the right.
param([string]$Out)

Add-Type -AssemblyName System.Drawing

$W = 1000
$H = 520

function Hex($hex) {
    $hex = $hex.TrimStart('#')
    return [System.Drawing.Color]::FromArgb(255,
        [Convert]::ToInt32($hex.Substring(0, 2), 16),
        [Convert]::ToInt32($hex.Substring(2, 2), 16),
        [Convert]::ToInt32($hex.Substring(4, 2), 16))
}

function Soft($hex, $alpha) {
    $c = Hex $hex
    return [System.Drawing.Color]::FromArgb($alpha, $c.R, $c.G, $c.B)
}

function RoundRect($x, $y, $w, $h, $r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $r * 2
    $path.AddArc($x, $y, $d, $d, 180, 90)
    $path.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $path.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $path.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    return $path
}

$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

$g.Clear((Hex "0a0b0e"))

$line = [System.Drawing.Pen]::new((Soft "ffffff" 8), 1)
for ($x = 0; $x -lt $W; $x += 40) { $g.DrawLine($line, $x, 0, $x, $H) }
for ($y = 0; $y -lt $H; $y += 40) { $g.DrawLine($line, 0, $y, $W, $y) }

# a warm wash behind the shelf
$glow = New-Object System.Drawing.Drawing2D.GraphicsPath
$glow.AddEllipse(420, -140, 860, 800)
$brush = New-Object System.Drawing.Drawing2D.PathGradientBrush $glow
$brush.CenterColor = (Soft "d8a93f" 40)
$brush.SurroundColors = @((Soft "d8a93f" 0))
$g.FillPath($brush, $glow)

$left = 64
$white = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)

# the jar
$tile = RoundRect $left 92 60 60 17
$g.FillPath([System.Drawing.SolidBrush]::new((Soft "d8a93f" 235)), $tile)
$markFont = [System.Drawing.Font]::new("Segoe UI", 21, [System.Drawing.FontStyle]::Bold)
$fmt = New-Object System.Drawing.StringFormat
$fmt.Alignment = [System.Drawing.StringAlignment]::Center
$fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString("CJ", $markFont, $white, (New-Object System.Drawing.RectangleF $left, 92, 60, 60), $fmt)

# the name, over two lines so it stays large
$nameFont = [System.Drawing.Font]::new("Segoe UI", 40, [System.Drawing.FontStyle]::Bold)
$g.DrawString("CookieJar", $nameFont, [System.Drawing.SolidBrush]::new((Hex "f2f3f5")), ($left - 5), 184)
$g.DrawString("Tools", $nameFont, [System.Drawing.SolidBrush]::new((Hex "d8a93f")), ($left - 5), 240)

$tagFont = [System.Drawing.Font]::new("Segoe UI", 13.5, [System.Drawing.FontStyle]::Regular)
$tagBrush = [System.Drawing.SolidBrush]::new((Hex "949aa6"))
$g.DrawString("Editor tools for Unity, and the odd", $tagFont, $tagBrush, $left, 312)
$g.DrawString("desktop app, built while making games.", $tagFont, $tagBrush, $left, 336)

$pillFont = [System.Drawing.Font]::new("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$pillText = "Free for commercial use"
$pillWidth = [int]$g.MeasureString($pillText, $pillFont).Width + 44
$pill = RoundRect $left 382 $pillWidth 34 8
$g.FillPath([System.Drawing.SolidBrush]::new((Hex "d8a93f")), $pill)
$g.DrawString($pillText, $pillFont, [System.Drawing.SolidBrush]::new((Hex "1a1405")), ($left + 22), 390)

# the shelf: one tile a tool, in its own colour
$tools = @(
    @{ Mark = "BB"; Accent = "d8a93f"; Name = "Bakers Belt" },
    @{ Mark = "CK"; Accent = "3fa9a0"; Name = "CookBook" },
    @{ Mark = "CT"; Accent = "7f8bd6"; Name = "Crumb Trail" },
    @{ Mark = "ET"; Accent = "e0a33f"; Name = "Editor Toast" },
    @{ Mark = "CB"; Accent = "c9794f"; Name = "Crumb Baker" },
    @{ Mark = "TR"; Accent = "5e6ad2"; Name = "CrumbTree" },
    @{ Mark = "GB"; Accent = "4cb782"; Name = "GameBridge" }
)

$cardFont = [System.Drawing.Font]::new("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$chipFont = [System.Drawing.Font]::new("Segoe UI", 15, [System.Drawing.FontStyle]::Bold)
$startX = 520
$startY = 92
$cardW = 208
$cardH = 62
$gapX = 16
$gapY = 26

for ($i = 0; $i -lt $tools.Count; $i++) {
    $col = $i % 2
    $row = [Math]::Floor($i / 2)
    $x = $startX + $col * ($cardW + $gapX)
    $y = $startY + $row * ($cardH + $gapY)
    $t = $tools[$i]

    $card = RoundRect $x $y $cardW $cardH 10
    $g.FillPath([System.Drawing.SolidBrush]::new((Soft "ffffff" 10)), $card)
    $g.DrawPath([System.Drawing.Pen]::new((Soft "ffffff" 26), 1), $card)

    $chip = RoundRect ($x + 12) ($y + 13) 36 36 10
    $g.FillPath([System.Drawing.SolidBrush]::new((Soft $t.Accent 235)), $chip)
    $g.DrawString($t.Mark, $chipFont, $white, (New-Object System.Drawing.RectangleF ($x + 12), ($y + 13), 36, 36), $fmt)

    $nameBox = New-Object System.Drawing.RectangleF ($x + 60), $y, ($cardW - 68), $cardH
    $leftMid = New-Object System.Drawing.StringFormat
    $leftMid.Alignment = [System.Drawing.StringAlignment]::Near
    $leftMid.LineAlignment = [System.Drawing.StringAlignment]::Center
    $g.DrawString($t.Name, $cardFont, [System.Drawing.SolidBrush]::new((Hex "e3e6ea")), $nameBox, $leftMid)
}

$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "wrote $Out"
