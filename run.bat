@echo off
echo ====================================
echo Starting Geotags Chatbot Server
echo ====================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment tidak ditemukan!
    echo Jalankan setup.bat terlebih dahulu.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo WARNING: File .env tidak ditemukan!
    echo Menggunakan konfigurasi default dari .env.example
    echo.
)

REM Run the server
echo Starting server...
echo Server akan berjalan di http://localhost:8000
echo Tekan Ctrl+C untuk menghentikan server
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
