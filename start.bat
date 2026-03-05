@echo off
echo.
echo ============================================
echo   Feel Comfort - Setup and Run
echo ============================================
echo.

REM Check if venv exists, create if not
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/4] Virtual environment found.
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements
echo [2/4] Installing requirements...
pip install -r requirements.txt -q

REM Delete old broken database if it exists
if exist "db.sqlite3" (
    echo [3/4] Resetting database...
    del db.sqlite3
) else (
    echo [3/4] No existing database found.
)

REM Run all migrations fresh
echo [4/4] Running migrations...
python manage.py migrate

echo.
echo ============================================
echo   All done! Starting server...
echo   Open: http://127.0.0.1:8000
echo ============================================
echo.

python manage.py runserver
