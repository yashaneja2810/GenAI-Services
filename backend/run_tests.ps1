# PowerShell script to run tests
# Usage: .\run_tests.ps1

Write-Host "Running PrayogAI Tests..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run .\setup_backend.ps1 first to set up the environment." -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

# Check if dev dependencies are installed
$pytest_installed = & python -c "import pytest" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing test dependencies..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install test dependencies!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

$test_result = $LASTEXITCODE

Write-Host ""
if ($test_result -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Coverage report generated: htmlcov\index.html" -ForegroundColor Cyan
} else {
    Write-Host "Some tests failed!" -ForegroundColor Red
    Write-Host "Check the output above for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

exit $test_result
