@echo off
@chcp 65001 >nul
title Virtual MCP - Dry Audio Processor
color 0e

echo ========================================================
echo   🎙️ Auto-Dry Audio Processor (Python-based)
echo   Simulates FL Studio Noise Gate and EQ
echo ========================================================
echo.

:: 1. Define Candidate Paths for Venv
set "VENV_LOCAL=.\venv"
set "VENV_PORTABLE=D:\Music_Sound_Level_Up_Portable\venv"

:: 2. Check Local Venv
if exist "%VENV_LOCAL%\Scripts\python.exe" (
    set "PYTHON_EXE=%VENV_LOCAL%\Scripts\python.exe"
    set "PIP_EXE=%VENV_LOCAL%\Scripts\pip.exe"
    echo ✅ Found Local Venv: %VENV_LOCAL%
) else (
    :: 3. Check Portable Venv (from config.json logic)
    if exist "%VENV_PORTABLE%\Scripts\python.exe" (
        set "PYTHON_EXE=%VENV_PORTABLE%\Scripts\python.exe"
        set "PIP_EXE=%VENV_PORTABLE%\Scripts\pip.exe"
        echo ✅ Found Portable Venv: %VENV_PORTABLE%
    ) else (
        echo [ERROR] Virtual Environment not found!
        echo Checked: %VENV_LOCAL% AND %VENV_PORTABLE%
        echo Please run setup.bat first.
        pause
        exit /b
    )
)

:: Check/Install Pedalboard
echo [Checking Dependencies]
"%PIP_EXE%" show pedalboard >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pedalboard...
    "%PIP_EXE%" install pedalboard --quiet
)

:: Ask for Input
set /p TARGET_DIR="Enter Input Folder Path (Drag & Drop folder here): "
if "%TARGET_DIR%"=="" set TARGET_DIR=ffmpeg

echo.
echo 🚀 Processing Audio Files...
echo.

"%PYTHON_EXE%" dry_processor.py -i "%TARGET_DIR%" -o "output_dry"

echo.
echo ========================================================
echo 🎉 Processing Complete!
echo Check the 'output_dry' folder for results.
echo ========================================================
pause
