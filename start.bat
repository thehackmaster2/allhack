@echo off
echo ========================================
echo    NeoxSecBot - Starting...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [+] Python found
echo.

REM Check if dependencies are installed
echo [+] Checking dependencies...
pip show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies not found. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [+] Dependencies OK
)

echo.
echo [+] Starting NeoxSecBot...
echo.
echo ========================================
echo.

python bot.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Bot crashed or stopped
    echo ========================================
    pause
)
