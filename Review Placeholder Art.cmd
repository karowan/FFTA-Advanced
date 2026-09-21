@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Prepare Art Pass.ps1" -Open
if errorlevel 1 pause
