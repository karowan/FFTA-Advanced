param(
    [string]$Run='',
    [string]$Config='scripts/mod-release.json',
    [string]$Python=''
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
Push-Location -LiteralPath $PSScriptRoot
try {
    $fftaConfig=Get-Content -LiteralPath $Config -Raw | ConvertFrom-Json
    if(-not $Run) {
        & '.\Test Expansion.ps1' -Plan $fftaConfig.plan -Suite $fftaConfig.suite -Python $Python
        $Run=(Get-Content 'build/expansion/test-runs/latest.json' -Raw | ConvertFrom-Json).report
    }
    & $Python $fftaConfig.packager --config $Config --run $Run
    if($LASTEXITCODE -ne 0) { throw 'Release packaging failed.' }
    & '.\scripts\launch-mod-release.ps1' -ValidateOnly -Python $Python
} finally { Pop-Location }
