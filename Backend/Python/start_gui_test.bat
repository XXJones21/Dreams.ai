@echo off
echo ========================================
echo Dreams.ai GUI Test Suite Launcher
echo ========================================
echo.

:: Change to the correct directory
cd /d "%~dp0"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ and try again
    pause
    exit /b 1
)

echo Python found. Checking dependencies...

:: Check if required packages are installed
python -c "import flask, flask_cors, requests, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install flask flask-cors requests pillow
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
)

echo.
echo Checking if GUI server is already running...

:: Check if server is already running on port 5000
netstat -an | findstr ":5000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo Server is already running on port 5000
    echo Opening browser...
    start http://localhost:5000
    echo.
    echo GUI Test Suite is ready!
    echo URL: http://localhost:5000
    echo.
    echo Press any key to stop the server...
    pause >nul
    echo Stopping server...
    taskkill /f /im python.exe >nul 2>&1
    echo Server stopped.
) else (
    echo Starting GUI Test Suite server...
    echo.
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