param(
    [switch]$ValidateOnly,
    [string]$Channel='build/releases/current.json',
    [string]$Python=''
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'resolve-python.ps1')
$Python = Resolve-FftaPython -Python $Python
$fftaJson=& $Python (Join-Path $PSScriptRoot 'prepare-mod-release.py') --channel $Channel
if ($LASTEXITCODE -ne 0) { throw 'Release validation failed; no game launched.' }
$fftaData=$fftaJson | ConvertFrom-Json
$fftaRom=$fftaData.rom
$fftaSave=$fftaData.saveDirectory
$fftaArguments=@('-C',('"savegamePath='+$fftaSave+'"'),'-C',('"savestatePath='+$fftaSave+'"'),'-C',('"screenshotPath='+$fftaSave+'"'),('"'+$fftaRom+'"'))
if($ValidateOnly) {
    $fftaData | Add-Member -NotePropertyName arguments -NotePropertyValue $fftaArguments
    $fftaData | ConvertTo-Json
    exit 0
}
if(-not(Test-Path -LiteralPath $fftaSave)) { New-Item -ItemType Directory -Path $fftaSave | Out-Null }
Start-Process -FilePath $fftaData.emulator -ArgumentList $fftaArguments -WorkingDirectory (Split-Path $fftaRom) -WindowStyle Normal
