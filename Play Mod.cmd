@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch-mod-release.ps1"
if errorlevel 1 pause
