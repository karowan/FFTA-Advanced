@echo off
if not exist "%~dp0build\foundation\FFTA_vanillaplus_dev.gba" (
  echo The development ROM has not been built. See IMPLEMENTATION-STATUS.md.
  pause
  exit /b 1
)
start "" /D "%~dp0build\foundation" "%~dp0tools\mgba\mGBA-0.10.5-win64\mGBA.exe" "%~dp0build\foundation\FFTA_vanillaplus_dev.gba"
