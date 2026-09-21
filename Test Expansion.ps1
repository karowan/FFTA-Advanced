param(
    [string]$Suite='full',
    [string]$Plan='',
    [string[]]$Only=@(),
    [switch]$List,
    [string]$Python=''
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$fftaPython=Resolve-FftaPython -Python $Python
Push-Location -LiteralPath $PSScriptRoot
try {
    $fftaArguments=@('scripts/run-expansion-tests.py','--suite',$Suite)
    if ($Plan) { $fftaArguments+=@('--plan',$Plan) }
    foreach ($fftaStep in $Only) { $fftaArguments+=@('--only',$fftaStep) }
    if ($List) { $fftaArguments+='--list' }
    & $fftaPython @fftaArguments
    if ($LASTEXITCODE -ne 0) { throw 'Expansion tests failed; see build/expansion/test-runs/latest.json' }
} finally { Pop-Location }
