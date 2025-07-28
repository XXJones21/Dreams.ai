@echo off
echo ========================================
echo Dreams.ai GUI Test Suite Launcher
echo ========================================
echo.

:: Change to the correct directory
cd /d "%~dp0"

:: Check if Python is available
python --version
if errorlevel 1 (
    echo ERROR: Python is not available
    echo Please install Python 3.13+ and try again
    pause
    exit /b 1
)

echo Python found. Starting GUI server...
echo.

:: Check if server is already running
netstat -an | findstr ":5000" | findstr "LISTENING"
if not errorlevel 1 (
    echo Server is already running on port 5000
    echo Opening browser...
    start http://localhost:5000
    echo.
    echo GUI Test Suite is ready!
    echo URL: http://localhost:5000
    echo.
    echo Press any key to stop the server...
    pause
    echo Stopping server...
    taskkill /f /im python.exe
    echo Server stopped.
) else (
    echo Starting Dreams.ai GUI Test Suite...
    echo Open http://localhost:5000 in your browser
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    
    :: Start the GUI server
    python test_gui.py
    
    echo.
    echo Server stopped.
)

echo.
echo ========================================
echo GUI Test Suite Launcher Complete
echo ========================================
pause 