param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path,
    [string]$OutputStem = 'field-demo'
)
$ErrorActionPreference = 'Stop'
function Color([string]$hex) {
    return [Convert]::ToInt32($hex.Substring(0,2),16) + 256*[Convert]::ToInt32($hex.Substring(2,2),16) + 65536*[Convert]::ToInt32($hex.Substring(4,2),16)
}
$modelPath = Join-Path $RepositoryRoot '.tools/field-demo-build/presentation.json'
$model = Get-Content -LiteralPath $modelPath -Raw -Encoding UTF8 | ConvertFrom-Json
$out = Join-Path $PSScriptRoot ($OutputStem + '.pptx')
$render = Join-Path $RepositoryRoot '.tools/field-demo-build/renders'
New-Item -ItemType Directory -Path $render -Force | Out-Null
$app = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $deck = $app.Presentations.Add(0)
    $deck.PageSetup.SlideWidth = 960
    $deck.PageSetup.SlideHeight = 540
    foreach ($data in $model.slides) {
        $slide = $deck.Slides.Add($deck.Slides.Count+1, 12)
        $slide.FollowMasterBackground = 0
        $slide.Background.Fill.Solid()
        $slide.Background.Fill.ForeColor.RGB = Color $data.background
        foreach ($e in $data.elements) {
            $x=[single]($e.x*.75);$y=[single]($e.y*.75);$w=[single]($e.w*.75);$h=[single]($e.h*.75)
            if ($e.kind -eq 'text') {
                $shape=$slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
                $shape.TextFrame.MarginLeft=0;$shape.TextFrame.MarginRight=0;$shape.TextFrame.MarginTop=0;$shape.TextFrame.MarginBottom=0
                $shape.TextFrame.WordWrap=-1;$shape.TextFrame.AutoSize=0
                $tr=$shape.TextFrame.TextRange
                $tr.Text=($e.text -replace "`n","`r")
                $tr.Font.Name=$e.font;$tr.Font.Size=[single]($e.size*.75);$tr.Font.Color.RGB=Color $e.color
                $tr.Font.Bold=$(if ($e.bold) {-1} else {0})
                $tr.ParagraphFormat.Alignment=$(if ($e.align -eq 'r') {3} else {1})
                $tr.ParagraphFormat.SpaceAfter=5.25
                if ($e.link) { $tr.ActionSettings.Item(1).Hyperlink.Address=$e.link; $tr.Font.Color.RGB=Color $e.color }
                $shape.TextFrame.AutoSize=0
                $shape.TextFrame2.AutoSize=0
                $shape.Left=$x;$shape.Top=$y;$shape.Width=$w;$shape.Height=$h
            } elseif ($e.kind -eq 'rect') {
                $shape=$slide.Shapes.AddShape(1,$x,$y,$w,$h)
                $shape.Fill.Solid();$shape.Fill.ForeColor.RGB=Color $e.color;$shape.Line.Visible=0
            } elseif ($e.kind -eq 'image') {
                $shape=$slide.Shapes.AddPicture($e.path,0,-1,$x,$y,$w,$h)
                $shape.AlternativeText=$e.alt
            } elseif ($e.kind -eq 'table') {
                $shape=$slide.Shapes.AddTable($e.rows.Count,$e.widths.Count,$x,$y,$w,$h)
                $table=$shape.Table
                for ($c=1;$c -le $e.widths.Count;$c++) { $table.Columns.Item($c).Width=[single]($e.widths[$c-1]*.75) }
                for ($r=1;$r -le $e.rows.Count;$r++) {
                    $table.Rows.Item($r).Height=[single]($e.rowh*.75)
                    for ($c=1;$c -le $e.widths.Count;$c++) {
                        $cell=$table.Cell($r,$c).Shape
                        $cell.TextFrame.TextRange.Text=[string]$e.rows[$r-1][$c-1]
                        $cell.TextFrame.MarginLeft=9;$cell.TextFrame.MarginRight=9;$cell.TextFrame.MarginTop=5;$cell.TextFrame.MarginBottom=5
                        $cell.TextFrame.VerticalAnchor=3
                        $cell.TextFrame.TextRange.Font.Name='Arial';$cell.TextFrame.TextRange.Font.Size=[single]($e.size*.75)
                        $cell.TextFrame.TextRange.Font.Bold=$(if ($r -eq 1) {-1} else {0})
                        $cell.TextFrame.TextRange.Font.Color.RGB=Color $(if ($r -eq 1) {'FFFFFF'} else {'173B49'})
                        $cell.Fill.Solid();$cell.Fill.ForeColor.RGB=Color $(if ($r -eq 1) {'007F83'} elseif ($r%2 -eq 0) {'F0F6F5'} else {'FFFFFF'})
                    }
                }
            }
        }
        $slide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text=$data.notes
    }
    $deck.SaveAs($out,24)
    $deck.Export($render,'PNG',1600,900)
    $deck.SaveAs((Join-Path $PSScriptRoot ($OutputStem + '.pdf')),32)
    Write-Output "Exported $($deck.Slides.Count) native PowerPoint slides, PNG previews, and PDF."
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($app.Presentations.Count -eq 0) { $app.Quit() }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($app) | Out-Null
}
& (Join-Path $RepositoryRoot '.venv/Scripts/python.exe') (Join-Path $PSScriptRoot 'clean_document_metadata.py') --stem $OutputStem
if ($LASTEXITCODE -ne 0) { throw 'Document metadata cleanup failed.' }
