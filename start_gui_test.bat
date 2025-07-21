@echo off
echo ========================================
echo Dreams.ai GUI Test Suite Launcher
echo ========================================
echo.

:: Change to the Backend/Python directory
cd /d "%~dp0Backend\Python"

:: Check if the directory exists
if not exist "test_gui.py" (
    echo ERROR: GUI test suite not found
    echo Expected location: Backend\Python\test_gui.py
    pause
    exit /b 1
)

:: Run the GUI launcher
call start_gui_test.bat 