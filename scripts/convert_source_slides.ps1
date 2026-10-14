param(
    [Parameter(Mandatory = $true)]
    [string] $SourceDirectory
)

$ErrorActionPreference = 'Stop'
$source = (Resolve-Path -LiteralPath $SourceDirectory).Path
$target = Join-Path (Split-Path -Parent $PSScriptRoot) 'content\readings\ucsf\assets'
New-Item -ItemType Directory -Force -Path $target | Out-Null
$decks = @(
    @('Unit 1 v2_ Intro to Informatics for FETP.pptx', 'unit-1-version-2-slides.pdf'),
    @('Unit 2_v2_ Detection and Diagonosis.pptx', 'unit-2-version-2-slides.pdf')
)
$powerpoint = New-Object -ComObject PowerPoint.Application
try {
    foreach ($entry in $decks) {
        $presentation = $powerpoint.Presentations.Open((Join-Path $source $entry[0]), -1, 0, 0)
        try {
            $presentation.SaveAs((Join-Path $target $entry[1]), 32)
            Write-Output "$($entry[1]): $($presentation.Slides.Count) PowerPoint slides"
        } finally {
            $presentation.Close()
        }
    }
} finally {
    $powerpoint.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerpoint) | Out-Null
}
