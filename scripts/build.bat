@echo off
chcp 65001 >nul
title Build RemoveCodecvWatermark

echo ============================================
echo   Building RemoveCodecvWatermark.exe
echo ============================================
echo.

REM Move to project root so output lands in root-level dist/
cd /d "%~dp0.."

REM Check if pyinstaller is available
where pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] PyInstaller not found, installing...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PyInstaller. Make sure pip is available.
        pause
        exit /b 1
    )
)

echo [INFO] Building standalone executable ...
pyinstaller --onefile --noconsole --name RemoveCodecvWatermark src\remove_codecv_watermark.py

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build successful!
echo   Output: %CD%\dist\RemoveCodecvWatermark.exe
echo ============================================
echo.
echo Next steps:
echo   1. Run scripts\register_context_menu.ps1 to install right-click menu
echo   2. Right-click any PDF -> "Remove CodeCV Watermark"
echo.
pause
