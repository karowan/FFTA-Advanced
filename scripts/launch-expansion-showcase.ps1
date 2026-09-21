param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$fftaRoot = Split-Path -Parent $PSScriptRoot
$fftaRom = Join-Path $fftaRoot 'roms/play/expansion-showcase-v0.7/FFTA_Expansion_Showcase_v0.7.gba'
$fftaSave = Join-Path $fftaRoot 'saves/expansion-showcase-v0.7'
$fftaEmulator = Join-Path $fftaRoot 'tools/mgba/mGBA-0.10.5-win64/mGBA.exe'
foreach ($fftaFile in @($fftaRom, (Join-Path $fftaSave 'FFTA_Expansion_Showcase_v0.7.sav'), $fftaEmulator)) {
    if (-not (Test-Path -LiteralPath $fftaFile)) { throw "Showcase file is missing: $fftaFile" }
    $fftaPart = [IO.Path]::GetFullPath($fftaFile)
    while ($fftaPart -and $fftaPart -ne $fftaRoot) {
        if ((Get-Item -LiteralPath $fftaPart -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Showcase path contains a link: $fftaPart"
        }
        $fftaPart = Split-Path -Parent $fftaPart
    }
}
$fftaHasher = [Security.Cryptography.SHA1]::Create()
$fftaStream = [IO.File]::OpenRead($fftaRom)
try { $fftaDigest = ([BitConverter]::ToString($fftaHasher.ComputeHash($fftaStream))).Replace('-', '').ToLowerInvariant() }
finally { $fftaStream.Dispose(); $fftaHasher.Dispose() }
if ($fftaDigest -ne '1b070824a8dad4995434eee3ab40fa08187a6120') { throw 'Wrong showcase ROM.' }
$fftaArguments = @('-C', ('"savegamePath=' + $fftaSave + '"'),
    '-C', ('"savestatePath=' + $fftaSave + '"'),
    '-C', ('"screenshotPath=' + $fftaSave + '"'), ('"' + $fftaRom + '"'))
if ($ValidateOnly) {
    [ordered]@{validated=$true; launched=$false; rom=$fftaRom; saveDirectory=$fftaSave; arguments=$fftaArguments} | ConvertTo-Json
    exit 0
}
Start-Process -FilePath $fftaEmulator -ArgumentList $fftaArguments -WorkingDirectory (Split-Path $fftaRom) -WindowStyle Normal
