@echo off
REM --- Check for Python ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python isn't installed, please install Python 3.11 or later.
    goto :end
)

REM --- Create virtual environment ---
echo Creating a virtual Python environment for the project...
python -m venv venv

REM --- Activate venv ---
call venv\Scripts\activate

REM --- Install requirements ---
echo Installing project requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install

echo Successfully installed the project requirements!
:end
pause
