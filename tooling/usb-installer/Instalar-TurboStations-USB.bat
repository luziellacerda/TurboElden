@echo off
setlocal
chcp 65001 >nul
title Instalar TurboStations por USB
set "TS_INSTALLER=%~dp0Instalar-TurboStations-USB.ps1"
if not exist "%TS_INSTALLER%" goto :MISSING
if "%~1"=="" goto :DEFAULT
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TS_INSTALLER%" -ApkPath "%~1"
goto :DONE
:DEFAULT
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TS_INSTALLER%"
:DONE
set "TS_INSTALL_RC=%ERRORLEVEL%"
echo.
pause
exit /b %TS_INSTALL_RC%
:MISSING
echo O arquivo Instalar-TurboStations-USB.ps1 precisa estar ao lado deste BAT.
echo.
pause
exit /b 1
