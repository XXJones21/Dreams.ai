@echo off
echo Testing Dreams.ai GUI API...
echo.

REM Check if server is running
python test_gui_simple.py

echo.
echo Test completed. Press any key to exit...
pause >nul 