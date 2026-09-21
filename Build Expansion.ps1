param(
    [string]$Python = '',
    [switch]$CompareCurrent,
    [switch]$KeepWorkspace
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
$fftaArguments = @((Join-Path $PSScriptRoot 'scripts/rebuild-expansion.py'))
if ($CompareCurrent) { $fftaArguments += '--compare-current' }
if ($KeepWorkspace) { $fftaArguments += '--keep-workspace' }
& $Python @fftaArguments
if ($LASTEXITCODE -ne 0) { throw 'Clean expansion build failed; see build/reproducibility/latest.json' }
