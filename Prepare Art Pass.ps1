param([switch]$Open, [string]$Python='')
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'scripts/resolve-python.ps1')
$fftaPython=Resolve-FftaPython -Python $Python
Push-Location -LiteralPath $PSScriptRoot
try {
    $fftaAuditText = & $fftaPython 'scripts/prepare-placeholder-art-pass.py'
    if ($LASTEXITCODE -ne 0) { throw 'Placeholder audit failed; inspect the reported evidence.' }
    Write-Output $fftaAuditText
    if ($Open) {
        $fftaAudit = $fftaAuditText | ConvertFrom-Json
        Start-Process -FilePath $fftaAudit.gallery -WindowStyle Normal
    }
} finally { Pop-Location }
