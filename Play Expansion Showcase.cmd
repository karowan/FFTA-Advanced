@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch-expansion-showcase.ps1"
if errorlevel 1 pause
