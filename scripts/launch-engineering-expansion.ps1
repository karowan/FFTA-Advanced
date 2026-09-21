param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$fftaRoot = Split-Path -Parent $PSScriptRoot
$fftaRom = Join-Path $fftaRoot 'roms/play/expansion-v0.7-engineering/FFTA_Expansion_v0.7.gba'
$fftaSave = Join-Path $fftaRoot 'saves/expansion-v0.7-engineering'
$fftaEmulator = Join-Path $fftaRoot 'tools/mgba/mGBA-0.10.5-win64/mGBA.exe'
$fftaManifest = Join-Path $fftaRoot 'build/releases/v0.7-engineering/current.json'
function Assert-LocalPath([string]$Path) {
    $fftaFull = [IO.Path]::GetFullPath($Path)
    if (-not $fftaFull.StartsWith($fftaRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Expansion path is outside this checkout.'
    }
    $fftaPart = $fftaFull
    while ($fftaPart -and $fftaPart -ne $fftaRoot) {
        if (Test-Path -LiteralPath $fftaPart) {
            if ((Get-Item -LiteralPath $fftaPart -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Expansion path contains a link: $fftaPart"
            }
        }
        $fftaPart = Split-Path -Parent $fftaPart
    }
}
foreach ($fftaPath in @($fftaRom, $fftaSave, $fftaEmulator, $fftaManifest)) { Assert-LocalPath $fftaPath }
if (-not (Test-Path -LiteralPath $fftaRom) -or -not (Test-Path -LiteralPath $fftaManifest)) {
    throw 'Expansion delivery is missing. See EXPANSION-PLAYER-GUIDE.md.'
}
$fftaData = Get-Content -LiteralPath $fftaManifest -Raw | ConvertFrom-Json
$fftaExpected = 'a28b624bb13c8f2f2597a4d4bd3999b17c234b99'
$fftaHasher = [Security.Cryptography.SHA1]::Create()
$fftaStream = [IO.File]::OpenRead($fftaRom)
try { $fftaDigest = ([BitConverter]::ToString($fftaHasher.ComputeHash($fftaStream))).Replace('-', '').ToLowerInvariant() }
finally { $fftaStream.Dispose(); $fftaHasher.Dispose() }
if ($fftaData.rom.sha1 -ne $fftaExpected -or $fftaDigest -ne $fftaExpected) {
    throw 'Expansion ROM differs from the verified v0.7 engineering release.'
}
if (-not (Test-Path -LiteralPath $fftaEmulator)) { throw 'The local mGBA installation is missing.' }
# Explicit command-line overrides take precedence over a user's global save
# paths. These are consumed by mGBA 0.10.5's core config and Qt launcher.
$fftaArguments = @('-C', ('"savegamePath=' + $fftaSave + '"'),
    '-C', ('"savestatePath=' + $fftaSave + '"'),
    '-C', ('"screenshotPath=' + $fftaSave + '"'), ('"' + $fftaRom + '"'))
if ($ValidateOnly) {
    [ordered]@{ validated = $true; launched = $false; rom = $fftaRom;
        saveDirectory = $fftaSave; emulator = $fftaEmulator; arguments = $fftaArguments } | ConvertTo-Json
    exit 0
}
New-Item -ItemType Directory -Path $fftaSave -Force | Out-Null
# This branch runs only when the player invokes the launcher.
Start-Process -FilePath $fftaEmulator -ArgumentList $fftaArguments -WorkingDirectory (Split-Path $fftaRom) -WindowStyle Normal
