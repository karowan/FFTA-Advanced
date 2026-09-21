@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\launch-patcher.ps1"
if errorlevel 1 pause
