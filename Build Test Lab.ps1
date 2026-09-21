param([string]$Python = '')
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
Push-Location -LiteralPath $PSScriptRoot
try {
    node scripts/prepare-test-lab.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Test-save source preparation failed' }
    Push-Location -LiteralPath (Join-Path $PSScriptRoot 'tools/event-assembler')
    try {
        $fftaLabLog = & './ColorzCore.exe' A FE8 "-output:$PSScriptRoot/build/test-lab/setup-only.gba" "-input:$PSScriptRoot/build/test-lab/setup-only.event" 2>&1
        $fftaLabExit = $LASTEXITCODE
        $fftaLabLog | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'build/test-lab/setup-assembler.log')
        if ($fftaLabExit -ne 0 -or ($fftaLabLog -join "`n") -notmatch 'No errors\.') { throw 'Test-save assembler failed' }
    } finally { Pop-Location }
    & $Python scripts/build-test-lab.py
    if ($LASTEXITCODE -ne 0) { throw 'Test lab verification failed' }
} finally { Pop-Location }
