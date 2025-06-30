@echo off
REM Get the directory of this script
set SCRIPT_DIR=%~dp0

echo Script directory is: %SCRIPT_DIR%
echo Attempting to change to: "%SCRIPT_DIR%Python"
cd /d "%SCRIPT_DIR%Python"

echo Current directory is: %cd%
echo Attempting to run: python3.13 -m uvicorn api_server:app --reload

start cmd /k "python3.13 -m uvicorn api_server:app --reload" 