param(
    [string]$JarPath = "C:\tmp\antlr-4.13.2-complete.jar"
)

if (-not (Test-Path $JarPath)) {
    throw "ANTLR jar not found at '$JarPath'."
}

$grammarDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$grammarDir = Join-Path $grammarDir "grammar"
$outputDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "generated"

java -jar $JarPath -Dlanguage=Python3 -visitor -no-listener -o $outputDir (Join-Path $grammarDir "WasteQuery.g4")
