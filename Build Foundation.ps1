param(
    [string]$Python = '',
    [switch]$BuildOnly
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
$fftaRoot = $PSScriptRoot
Push-Location -LiteralPath $fftaRoot
try {
    node scripts/build-foundation.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Source preparation failed' }
    Push-Location -LiteralPath (Join-Path $fftaRoot 'tools/event-assembler')
    try {
        $fftaLog = & './ColorzCore.exe' A FE8 "-output:$fftaRoot/build/foundation/FFTA_vanillaplus_dev.gba" "-input:$fftaRoot/build/foundation/foundation.event" 2>&1
        $fftaResult = $LASTEXITCODE
        $fftaLog | Set-Content -LiteralPath (Join-Path $fftaRoot 'build/foundation/assembler.log')
        if ($fftaResult -ne 0) { throw "Assembler failed: $fftaLog" }
    } finally { Pop-Location }
    node scripts/build-foundation.mjs --finalize
    if ($LASTEXITCODE -ne 0) { throw 'Finalization failed' }
    if ($BuildOnly) { return }
    foreach ($fftaCheck in @('notes/validate-current-design.mjs', 'notes/validate-equipment-plan.mjs', 'scripts/verify-foundation.mjs')) {
        node $fftaCheck
        if ($LASTEXITCODE -ne 0) { throw "Verification failed: $fftaCheck" }
    }
    foreach ($fftaCheck in @('scripts/test-arm-routines.py', 'scripts/test-menu-routines.py', 'scripts/test-emulator-smoke.py')) {
        & $Python $fftaCheck
        if ($LASTEXITCODE -ne 0) { throw "Verification failed: $fftaCheck" }
    }
    node scripts/package-foundation.mjs
    if ($LASTEXITCODE -ne 0) { throw 'Patch packaging failed' }
} finally { Pop-Location }
