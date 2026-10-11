@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul
cl /nologo /std:c++17 /EHsc /O2 /Fe:launch_command_host.exe /Fo:launch_command_host.obj launch_command_host.cpp
if errorlevel 1 exit /b 1
launch_command_host.exe
