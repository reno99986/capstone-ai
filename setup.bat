@echo off
echo ====================================
echo Geotags Chatbot - Setup Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python 3.11 terlebih dahulu.
    pause
    exit /b 1
)

echo [1/5] Membuat virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Gagal membuat virtual environment!
    pause
    exit /b 1
)

echo [2/5] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrade pip...
python -m pip install --upgrade pip

echo [4/5] Install dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Gagal install dependencies!
    pause
    exit /b 1
)

echo [5/5] Setup environment file...
if not exist .env (
    copy .env.example .env
    echo File .env telah dibuat. Silakan edit file .env dengan konfigurasi Anda.
) else (
    echo File .env sudah ada.
)

echo.
echo ====================================
echo Setup selesai!
echo ====================================
echo.
echo Langkah selanjutnya:
echo 1. Edit file .env dengan konfigurasi database Anda
echo 2. Pastikan Ollama sudah running: ollama serve
echo 3. Pull model llama3.2: ollama pull llama3.2
echo 4. Jalankan server: run.bat
echo.
pause
