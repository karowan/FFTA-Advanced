param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$artRoot = Split-Path -Parent $PSScriptRoot
function Assert-ArtLocalPath([string]$Path) {
    $artFull = [IO.Path]::GetFullPath($Path)
    if (-not $artFull.StartsWith($artRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Art preview path is outside this checkout.'
    }
    for ($artPart = $artFull; $artPart -and $artPart -ne $artRoot; $artPart = Split-Path -Parent $artPart) {
        if ((Test-Path -LiteralPath $artPart) -and ((Get-Item -LiteralPath $artPart -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw 'Art preview path contains a link.'
        }
    }
    return $artFull
}
$artIndex = Assert-ArtLocalPath (Join-Path $artRoot 'build/art/pipeline/delivery/current.json')
$artData = Get-Content -LiteralPath $artIndex -Raw | ConvertFrom-Json
if ($artData.status -ne 'verified technical preview' -or $artData.rom.sha1 -notmatch '^[0-9a-f]{40}$') {
    throw 'Art preview delivery is not verified.'
}
$artSha = $artData.rom.sha1
$artRelative = "build/art/pipeline/delivery/" + $artSha
if ($artData.bundleId) {
    if ($artData.bundleId -notmatch '^[0-9a-f]{64}$') { throw 'Art preview bundle identity is invalid.' }
    $artRelative += '/bundle-' + $artData.bundleId.Substring(0,16)
}
$artRelative += '/FFTA_Art_Pipeline.gba'
if ($artData.rom.path -cne $artRelative) { throw 'Art preview bundle path differs from the verified manifest.' }
$artRom = Assert-ArtLocalPath (Join-Path $artRoot $artRelative)
$artSave = Assert-ArtLocalPath (Join-Path $artRoot ("saves/art-pipeline/" + $artSha))
$artEmulator = Assert-ArtLocalPath (Join-Path $artRoot 'tools/mgba/mGBA-0.10.5-win64/mGBA.exe')
$artHasher = [Security.Cryptography.SHA1]::Create()
$artStream = [IO.File]::OpenRead($artRom)
try { $artDigest = ([BitConverter]::ToString($artHasher.ComputeHash($artStream))).Replace('-', '').ToLowerInvariant() }
finally { $artStream.Dispose(); $artHasher.Dispose() }
if ($artDigest -ne $artSha) {
    throw 'Art preview ROM differs from the verified manifest.'
}
if (-not (Test-Path -LiteralPath $artEmulator)) { throw 'The local mGBA installation is missing.' }
$artArguments = @('-C', ('"savegamePath=' + $artSave + '"'),
    '-C', ('"savestatePath=' + $artSave + '"'),
    '-C', ('"screenshotPath=' + $artSave + '"'), ('"' + $artRom + '"'))
if ($ValidateOnly) {
    [ordered]@{validated=$true; launched=$false; rom=$artRom; saveDirectory=$artSave;
        emulator=$artEmulator; arguments=$artArguments; coverage=$artData.coverage} | ConvertTo-Json -Depth 6
    exit 0
}
New-Item -ItemType Directory -Path $artSave -Force | Out-Null
Start-Process -FilePath $artEmulator -ArgumentList $artArguments -WorkingDirectory (Split-Path $artRom) -WindowStyle Normal
