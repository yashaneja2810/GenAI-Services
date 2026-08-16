@echo off
REM Batch script to run tests
REM Usage: run_tests.bat

echo.
echo Running PrayogAI Tests...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Run setup_backend.ps1 first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if dev dependencies are installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo Installing test dependencies...
    pip install -r requirements-dev.txt
)

echo.
echo Running tests...
echo.

REM Run pytest with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

if %errorlevel% equ 0 (
    echo.
    echo All tests passed!
    echo Coverage report: htmlcov\index.html
) else (
    echo.
    echo Some tests failed! Check output above.
)

echo.
pause
