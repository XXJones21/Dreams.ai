# Dreams.ai GUI Test Suite Launcher
# PowerShell version with enhanced server checking

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dreams.ai GUI Test Suite Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.13+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Checking dependencies..." -ForegroundColor Yellow

# Check if required packages are installed
try {
    python -c "import flask, flask_cors, requests, PIL" 2>$null
    Write-Host "All dependencies are installed." -ForegroundColor Green
} catch {
    Write-Host "Installing required dependencies..." -ForegroundColor Yellow
    try {
        pip install flask flask-cors requests pillow
        Write-Host "Dependencies installed successfully." -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Checking if GUI server is already running..." -ForegroundColor Yellow

# Check if server is already running on port 5000
$serverRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/status" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $serverRunning = $true
    }
} catch {
    # Server not running or not responding
    $serverRunning = $false
}

if ($serverRunning) {
    Write-Host "Server is already running on port 5000" -ForegroundColor Green
    Write-Host "Opening browser..." -ForegroundColor Yellow
    Start-Process "http://localhost:5000"
    Write-Host ""
    Write-Host "GUI Test Suite is ready!" -ForegroundColor Green
    Write-Host "URL: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press any key to stop the server..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host "Stopping server..." -ForegroundColor Yellow
    
    # Try to gracefully stop the server
    try {
        $processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*test_gui.py*" }
        if ($processes) {
            $processes | Stop-Process -Force
            Write-Host "Server stopped." -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not stop server gracefully." -ForegroundColor Yellow
    }
} else {
    Write-Host "Starting GUI Test Suite server..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Starting Dreams.ai GUI Test Suite..." -ForegroundColor Cyan
    Write-Host "Open http://localhost:5000 in your browser" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Start the GUI server
    try {
        python test_gui.py
    } catch {
        Write-Host "Server stopped." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GUI Test Suite Launcher Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit" 