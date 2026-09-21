param([switch]$ValidateOnly,[switch]$NativePalette)
$ErrorActionPreference='Stop'
$fftaRoot=Split-Path -Parent $PSScriptRoot
$fftaManifest=Join-Path $fftaRoot 'build/art/reviewed-integration/complete-candidate.json'
$fftaExpected='3db563a978a17ae517a5c2b4e7b39dd00b1c2fb7'
$fftaData=Get-Content -LiteralPath $fftaManifest -Raw | ConvertFrom-Json
$fftaRom=[IO.Path]::GetFullPath($fftaData.path)
$fftaSave=Join-Path $fftaRoot 'saves/reviewed-art-2026-09-20'
if($NativePalette) {
    $fftaManifest=Join-Path $fftaRoot 'build/art/reviewed-integration/native-complete-candidate.json'
    $fftaExpected='e11b2603b93f7b74cbe497291af22cd9a3f9f468'
    $fftaData=Get-Content -LiteralPath $fftaManifest -Raw | ConvertFrom-Json
    $fftaRom=[IO.Path]::GetFullPath($fftaData.path)
    $fftaSave=Join-Path $fftaRoot 'saves/reviewed-native-art-2026-09-20'
    if($fftaData.components.reviewedActions.paletteMode -ne 'native-shared'){throw 'Native shared palettes required'}
}
$fftaEmulator=Join-Path $fftaRoot 'tools/mgba/mGBA-0.10.5-win64/mGBA.exe'
foreach($fftaPath in @($fftaRom,$fftaSave,$fftaEmulator,$fftaManifest)) {
    $fftaFull=[IO.Path]::GetFullPath($fftaPath)
    if(-not $fftaFull.StartsWith($fftaRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Preview path outside checkout'}
    while($fftaFull -and $fftaFull -ne $fftaRoot) {
        if((Test-Path -LiteralPath $fftaFull) -and ((Get-Item -LiteralPath $fftaFull -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw "Linked preview path: $fftaFull"}
        $fftaFull=Split-Path -Parent $fftaFull
    }
}
if($fftaData.romSha1 -ne $fftaExpected -or (Get-FileHash -LiteralPath $fftaRom -Algorithm SHA1).Hash.ToLowerInvariant() -ne $fftaExpected){throw 'Preview ROM differs from the reviewed combined candidate'}
if(-not(Test-Path -LiteralPath $fftaEmulator)){throw 'Local mGBA installation missing'}
if($fftaData.components.reviewedActions.missing.Count -or $fftaData.components.reviewedActions.provisional.Count){throw 'Incomplete class animation artwork'}
$fftaArguments=@('-C',('"savegamePath='+$fftaSave+'"'),'-C',('"savestatePath='+$fftaSave+'"'),'-C',('"screenshotPath='+$fftaSave+'"'),('"'+$fftaRom+'"'))
if($ValidateOnly) {
    [ordered]@{validated=$true;launched=$false;status=$(if($NativePalette){'native-palette artwork preview'}else{'historical custom-palette preview; retired'});rom=$fftaRom;romSha1=$fftaExpected;saveDirectory=$fftaSave;emulator=$fftaEmulator;arguments=$fftaArguments}|ConvertTo-Json
    exit 0
}
New-Item -ItemType Directory -Path $fftaSave -Force|Out-Null
Start-Process -FilePath $fftaEmulator -ArgumentList $fftaArguments -WorkingDirectory (Split-Path $fftaRom) -WindowStyle Normal
