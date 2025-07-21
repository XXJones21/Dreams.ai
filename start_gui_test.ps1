# Dreams.ai GUI Test Suite Launcher (Project Root)
# Launches the GUI test suite from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dreams.ai GUI Test Suite Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to the Backend/Python directory
$guiPath = Join-Path $PSScriptRoot "Backend\Python"
Set-Location $guiPath

# Check if the GUI test suite exists
if (-not (Test-Path "test_gui.py")) {
    Write-Host "ERROR: GUI test suite not found" -ForegroundColor Red
    Write-Host "Expected location: Backend\Python\test_gui.py" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run the GUI launcher
& ".\start_gui_test.ps1" 