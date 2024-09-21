@echo off
python -m pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Pip is not installed. Please install Python and Pip.
    exit /b 1
)

echo Installing required Python packages...

pip install datetime
pip install interactions.py

echo Packages installed successfully!
pause
