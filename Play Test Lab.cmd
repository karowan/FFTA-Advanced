@echo off
if not exist "%~dp0roms\play\test-lab\FFTA_test_lab.sav" (
  echo Build the test lab first. See TESTING.md.
  pause
  exit /b 1
)
start "" /D "%~dp0roms\play\test-lab" "%~dp0tools\mgba\mGBA-0.10.5-win64\mGBA.exe" "%~dp0roms\play\test-lab\FFTA_test_lab.gba"
