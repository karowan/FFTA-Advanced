# Compatibility entry point; current release selection lives in the channel.
param([switch]$ValidateOnly)
& (Join-Path $PSScriptRoot 'launch-mod-release.ps1') -ValidateOnly:$ValidateOnly
