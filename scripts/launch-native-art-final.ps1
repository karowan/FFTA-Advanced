param([switch]$ValidateOnly)
$ErrorActionPreference='Stop'
$fftaRoot=Split-Path -Parent $PSScriptRoot
$fftaPackage=Join-Path $fftaRoot 'build/releases/native-art-final/current.json'
$fftaData=Get-Content -LiteralPath $fftaPackage -Raw | ConvertFrom-Json
$fftaExpected='316a40524b960c49ad7213ac4b0bea539bfa9513'
$fftaRom=Join-Path $fftaRoot 'build/releases/native-art-final/FFTA_Reviewed_All_Classes.gba'
$fftaSave=Join-Path $fftaRoot 'saves/native-art-final-2026-09-20'
$fftaEmulator=Join-Path $fftaRoot 'tools/mgba/mGBA-0.10.5-win64/mGBA.exe'
foreach($fftaPath in @($fftaRom,$fftaSave,$fftaEmulator,$fftaPackage)) {
    $fftaFull=[IO.Path]::GetFullPath($fftaPath)
    if(-not $fftaFull.StartsWith($fftaRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Path outside checkout'}
    if(-not(Test-Path -LiteralPath $fftaFull)){throw "Missing package component: $fftaFull"}
    while($fftaFull -and $fftaFull -ne $fftaRoot) {
        if((Get-Item -LiteralPath $fftaFull -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Linked package path: $fftaFull"}
        $fftaFull=Split-Path -Parent $fftaFull
    }
}
if($fftaData.romSha1 -ne $fftaExpected -or (Get-FileHash -LiteralPath $fftaRom -Algorithm SHA1).Hash.ToLowerInvariant() -ne $fftaExpected){throw 'Release ROM differs from verified build'}
$fftaArguments=@('-C',('"savegamePath='+$fftaSave+'"'),'-C',('"savestatePath='+$fftaSave+'"'),'-C',('"screenshotPath='+$fftaSave+'"'),('"'+$fftaRom+'"'))
if($ValidateOnly) {
    [ordered]@{validated=$true;launched=$false;rom=$fftaRom;romSha1=$fftaExpected;saveDirectory=$fftaSave;arguments=$fftaArguments}|ConvertTo-Json
    exit 0
}
Start-Process -FilePath $fftaEmulator -ArgumentList $fftaArguments -WorkingDirectory (Split-Path $fftaRom) -WindowStyle Normal
