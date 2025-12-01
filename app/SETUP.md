# 🚀 Capstone AI - Quick Start Guide

Dokumentasi lengkap untuk setup dan menjalankan chatbot API di folder `app`.

---

## 📋 Prerequisites

Pastikan sistem Anda memiliki:

- **Windows 10/11** atau **Linux/Mac**
- **Administrator/Root access** untuk instalasi
- **Internet connection** untuk download dependencies
- **PostgreSQL** sudah berjalan (untuk database)

---

## 📥 STEP 1: Install Ollama

Ollama adalah local LLM server yang digunakan untuk chatbot.

### Windows

1. **Download Installer**
   - Buka browser → https://ollama.com/download
   - Download **OllamaSetup.exe** (Windows)

2. **Install Ollama**
   ```cmd
   # Double-click OllamaSetup.exe
   # Follow installation wizard
   # Default install path: C:\Users\<username>\AppData\Local\Programs\Ollama
   ```

3. **Verify Installation**
   ```cmd
   # Open Command Prompt atau PowerShell
   ollama --version
   # Output: ollama version is 0.x.x
   ```

4. **Start Ollama Service**
   ```cmd
   # Start Ollama server (biarkan terminal ini terbuka)
   ollama serve
   
   # Output:
   # Ollama is running on http://localhost:11434
   ```

5. **Pull LLM Model** (Terminal baru)
   ```cmd
   # Pull model llama3.2 (default, ~2GB)
   ollama pull llama3.2
   
   # Atau gunakan model lain:
   # ollama pull deepseek-r1:1.5b  # Lebih kecil (~900MB)
   # ollama pull llama3.2:1b        # Paling kecil (~700MB)
   
   # Verifikasi model terinstall
   ollama list
   # Output:
   # NAME                ID              SIZE      MODIFIED
   # llama3.2:latest    a80c4f17acd5    2.0 GB    2 hours ago
   ```

6. **Test Ollama API**
   ```cmd
   # Test connection
   curl http://localhost:11434/api/tags
   
   # Expected response: JSON dengan list models
   ```

### Linux

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start service
sudo systemctl start ollama
sudo systemctl enable ollama  # Auto-start on boot

# Verify
ollama --version

# Pull model
ollama pull llama3.2

# List models
ollama list
```

### macOS

```bash
# Install via Homebrew
brew install ollama

# Or download from https://ollama.com/download

# Start service
ollama serve

# Pull model
ollama pull llama3.2

# List models
ollama list
```

---

## 🐍 STEP 2: Install Python 3.11

### Windows

#### Option 1: Download dari Python.org (Recommended)

1. **Download Python 3.11**
   - Buka https://www.python.org/downloads/
   - Download **Python 3.11.x** (bukan 3.12+)
   - Pilih **Windows installer (64-bit)**

2. **Install Python**
   ```
   ✅ PENTING: Centang "Add Python to PATH"
   ✅ Pilih "Install Now"
   ```

3. **Verify Installation**
   ```cmd
   # Open new Command Prompt
   python --version
   # Output: Python 3.11.x
   
   # Check pip
   pip --version
   # Output: pip 24.x.x from ...
   ```

#### Option 2: Install via Chocolatey

```cmd
# Install Chocolatey (jika belum ada)
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python 3.11
choco install python311 -y

# Verify
python --version
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Verify
python3.11 --version

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### macOS

```bash
# Install via Homebrew
brew install python@3.11

# Verify
python3.11 --version

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/usr/local/opt/python@3.11/bin:$PATH"
```

---

## 📂 STEP 3: Setup Project Directory

### Navigate to App Folder

```cmd
# Windows
cd C:\laragon\www\capstone-ai\app

# Linux/Mac
cd /path/to/capstone-ai/app
```

### Verify Files Exist

```cmd
# Windows
dir

# Linux/Mac
ls -la
```

**Expected files:**
```
app.py
business_service.py
chatbot_service.py
requirements.txt
documentation.md
noteForFE
```

---

## 🌐 STEP 4: Create Virtual Environment

Virtual environment isolasi dependencies per project.

### Windows (PowerShell/CMD)

```cmd
# Navigate to app folder
cd C:\laragon\www\capstone-ai\app

# Create virtual environment (Python 3.11)
python -m venv venv

# Output:
# Creating virtual environment...
# (tunggu beberapa detik)

# Activate virtual environment
venv\Scripts\activate

# Prompt akan berubah menjadi:
# (venv) C:\laragon\www\capstone-ai\app>

# Verify Python in venv
where python
# Output: C:\laragon\www\capstone-ai\app\venv\Scripts\python.exe

python --version
# Output: Python 3.11.x
```

### Linux/Mac (Bash)

```bash
# Navigate to app folder
cd /path/to/capstone-ai/app

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Prompt akan berubah:
# (venv) user@host:~/capstone-ai/app$

# Verify
which python
# Output: /path/to/capstone-ai/app/venv/bin/python

python --version
# Output: Python 3.11.x
```

### Troubleshooting venv

**Error: "venv not found"**
```cmd
# Windows: Install venv
pip install virtualenv
virtualenv venv

# Linux: Install python3-venv
sudo apt install python3.11-venv
```

---

## 📦 STEP 5: Install Dependencies

### Upgrade pip First

```bash
# Always upgrade pip first
python -m pip install --upgrade pip

# Verify pip version
pip --version
# Output: pip 24.x.x
```

### Install from requirements.txt

```bash
# Make sure venv is active (see (venv) in prompt)
# If not: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/Mac)

# Install all dependencies
pip install -r requirements.txt

# Expected output:
# Collecting fastapi==0.109.0
# Downloading fastapi-0.109.0-py3-none-any.whl
# ...
# Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

### Manual Installation (if requirements.txt fails)

```bash
# Install dependencies one by one

# Core web framework
pip install fastapi==0.109.0
pip install uvicorn[standard]==0.27.0
pip install pydantic==2.5.3
pip install python-multipart==0.0.6

# Database
pip install sqlalchemy==2.0.25
pip install psycopg2-binary==2.9.9

# Authentication
pip install pyjwt==2.8.0
pip install python-dotenv==1.0.0

# LangChain & AI
pip install langchain==0.1.4
pip install langchain-community==0.0.16

# Utilities
pip install requests==2.31.0
```

### Verify Installation

```bash
# Check installed packages
pip list

# Expected output:
# Package               Version
# --------------------- -------
# fastapi               0.109.0
# uvicorn               0.27.0
# sqlalchemy            2.0.25
# langchain             0.1.4
# ...

# Test imports
python -c "import fastapi, sqlalchemy, langchain; print('✓ All imports OK')"
# Output: ✓ All imports OK
```

### Common Installation Errors

**Error: "Microsoft Visual C++ required"**
```cmd
# Windows: Install Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Or use pre-compiled binary:
pip install psycopg2-binary  # Instead of psycopg2
```

**Error: "Failed building wheel for psycopg2"**
```bash
# Use binary version
pip uninstall psycopg2
pip install psycopg2-binary
```

**Error: "SSL certificate verify failed"**
```bash
# Disable SSL verification (temporary)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## ⚙️ STEP 6: Configure Environment Variables

### Create .env File

```bash
# Create .env file in app folder
# Windows
notepad .env

# Linux/Mac
nano .env
```

### Add Configuration

```env
# filepath: c:\laragon\www\capstone-ai\app\.env

# JWT Secret Key (WAJIB - ganti dengan random string yang sama di Laravel backend)
JWT_SECRET_KEY=kotaBeriman25

# Database Connection (READ ONLY recommended)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/se26

# Chatbot Model
CHATBOT_MODEL=llama3.2
# Alternatives:
# CHATBOT_MODEL=deepseek-r1:1.5b
# CHATBOT_MODEL=llama3.2:1b

# Internal API Key (untuk debugging internal endpoints)
INTERNAL_API_KEY=supersecretkey

# Optional: Ollama API URL (default: http://localhost:11434)
# OLLAMA_BASE_URL=http://localhost:11434
```

### Important Notes:

1. **JWT_SECRET_KEY**: Harus **SAMA PERSIS** dengan `JWT_SECRET` di Laravel backend
2. **DATABASE_URL**: Sesuaikan dengan PostgreSQL Anda:
   ```
   Format: postgresql://username:password@host:port/database
   Contoh: postgresql://postgres:mypassword@localhost:5432/se26
   ```
3. **INTERNAL_API_KEY**: Jangan expose ke frontend! Hanya untuk server-to-server

### Verify Database Connection

```bash
# Test database connection
python -c "from sqlalchemy import create_engine, text; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); result = conn.execute(text('SELECT COUNT(*) FROM usaha_llm')); print(f'✓ Database OK: {result.scalar()} businesses')"

# Expected output:
# ✓ Database OK: 8 businesses
```

---

## 🚀 STEP 7: Run the Application

### Start Ollama Server (Terminal 1)

```bash
# Terminal 1: Start Ollama
ollama serve

# Keep this terminal open
# Output:
# Ollama is running on http://localhost:11434
```

### Start FastAPI Server (Terminal 2)

```bash
# Terminal 2: Navigate to app folder
cd C:\laragon\www\capstone-ai\app

# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start uvicorn server
uvicorn app:app --host 0.0.0.0 --port 5000 --reload

# Expected output:
# ✓ BusinessService connected - 8 businesses in database
# ✓ ChatbotService initialized with model: llama3.2
# ✓ Services initialized successfully
# INFO:     Uvicorn running on http://127.0.0.1:5000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### Uvicorn Command Options

```bash
# Development mode (auto-reload on code changes)
uvicorn app:app --reload

# Specify host and port
uvicorn app:app --host 0.0.0.0 --port 5000

# Production mode (multiple workers)
uvicorn app:app --host 0.0.0.0 --port 5000 --workers 4

# With custom logging
uvicorn app:app --log-level debug

# Full example
uvicorn app:app --host 0.0.0.0 --port 5000 --reload --log-level info
```

### Verify Server Running

**Open new terminal (Terminal 3):**

```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","services":{"business_service":true,"chatbot_service":true}}
```

**Or open browser:**
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

---

## ✅ STEP 8: Test the API

### Test 1: Health Check (No Auth)

```bash
curl http://localhost:5000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "business_service": true,
    "chatbot_service": true
  }
}
```

### Test 2: Get Samples (Requires JWT)

```bash
# Replace YOUR_JWT_TOKEN with actual token
curl -X GET "http://localhost:5000/chatbot/samples" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected:**
```json
{
  "success": true,
  "samples": [
    "Berapa total usaha di database?",
    "Berapa usaha di Balikpapan?",
    "Ada berapa usaha aktif di Balikpapan Timur?"
  ]
}
```

### Test 3: Chat - Count Query

```bash
curl -X POST "http://localhost:5000/chatbot/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Berapa usaha di Balikpapan?\"}"
```

**Expected:**
```json
{
  "success": true,
  "response": "Terdapat 8 usaha di Balikpapan.",
  "message_type": "count",
  "count": 8
}
```

### Test 4: Chat - Business Info

```bash
curl -X POST "http://localhost:5000/chatbot/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Apa itu Sembako Mukhlas?\"}"
```

**Expected:**
```json
{
  "success": true,
  "response": "SEMBAKO MUKHLAS adalah usaha sembako yang berlokasi di Pasar sepinggan...",
  "message_type": "business_info",
  "business_data": {
    "nama_usaha": "SEMBAKO MUKHLAS",
    "kategori": "SEMBAKO",
    "alamat": "Pasar sepinggan",
    "status": "aktif"
  }
}
```

---

## 🔧 Troubleshooting

### Problem 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Make sure venv is active
# Check prompt for (venv) prefix

# If not active:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem 2: "Connection to database failed"

**Solution:**
```bash
# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql

# Test connection manually
psql -U postgres -d se26

# Check .env file
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/se26
#                        ^^^^^^^^ ^^^^^^^^          ^^^^    ^^^^
#                        username password          port    database
```

### Problem 3: "Ollama connection refused"

**Solution:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama
ollama serve

# Check model is installed
ollama list

# If model not found:
ollama pull llama3.2
```

### Problem 4: "Port 5000 already in use"

**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac: Find and kill process
lsof -i :5000
kill -9 <PID>

# Or use different port
uvicorn app:app --port 5001
```

### Problem 5: "JWT token invalid"

**Solution:**
```bash
# Make sure JWT_SECRET_KEY in .env matches Laravel backend
# Check token is not expired
# Verify token format: "Bearer <token>"

# Get new token from Laravel
curl -X POST "http://your-laravel-backend/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Problem 6: "Column 'nama_komersial' does not exist"

**Solution:**
```bash
# Verify database schema
psql -U postgres -d se26 -c "\d usaha_llm"

# Column should be named 'nama_komersial_usaha'
# Check business_service.py uses correct column name
```

### Problem 7: LangChain Deprecation Warning

```
LangChainDeprecationWarning: The class `Ollama` was deprecated in LangChain 0.3.1
```

**Solution:**
```bash
# This is just a warning, app still works
# To fix completely:
pip install langchain-ollama
# Update chatbot_service.py: from langchain_ollama import OllamaLLM
```

---

## 🔄 Start/Stop Commands

### Windows (PowerShell Script)

**Create `start.ps1`:**
```powershell
# filepath: c:\laragon\www\capstone-ai\app\start.ps1

# Activate venv
.\venv\Scripts\Activate.ps1

# Start Ollama in background
Start-Process powershell -ArgumentList "ollama serve" -WindowStyle Minimized

# Wait for Ollama
Start-Sleep -Seconds 3

# Start FastAPI
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

**Run:**
```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

**Create `stop.ps1`:**
```powershell
# filepath: c:\laragon\www\capstone-ai\app\stop.ps1

# Kill uvicorn
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Kill Ollama
Get-Process | Where-Object {$_.ProcessName -eq "ollama"} | Stop-Process -Force

Write-Host "Stopped all services"
```

### Linux/Mac (Bash Script)

**Create `start.sh`:**
```bash
#!/bin/bash
# filepath: /path/to/capstone-ai/app/start.sh

# Activate venv
source venv/bin/activate

# Start Ollama in background
ollama serve > /dev/null 2>&1 &

# Wait for Ollama
sleep 3

# Start FastAPI
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

**Make executable & run:**
```bash
chmod +x start.sh
./start.sh
```

**Create `stop.sh`:**
```bash
#!/bin/bash
# filepath: /path/to/capstone-ai/app/stop.sh

# Kill uvicorn
pkill -f "uvicorn app:app"

# Kill Ollama
pkill -f "ollama serve"

echo "Stopped all services"
```

---

## 📊 Performance Tips

### 1. Use Smaller Model for Development

```bash
# Instead of llama3.2 (2GB), use:
ollama pull llama3.2:1b  # Only 700MB

# Update .env:
CHATBOT_MODEL=llama3.2:1b
```

### 2. Increase Uvicorn Workers (Production)

```bash
# Multiple workers for better performance
uvicorn app:app --workers 4 --host 0.0.0.0 --port 5000
```

### 3. Enable Database Connection Pooling

Edit `business_service.py`:
```python
self.engine = create_engine(
    db_uri,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 📝 Daily Workflow

### Morning Startup

```bash
# 1. Start Ollama (Terminal 1)
ollama serve

# 2. Start FastAPI (Terminal 2)
cd C:\laragon\www\capstone-ai\app
venv\Scripts\activate
uvicorn app:app --reload
```

### During Development

```bash
# Code changes auto-reload (if --reload flag used)
# Check console for errors
# Test with Postman or curl
```

### Before Leaving

```bash
# Stop servers:
# Ctrl+C in each terminal
# Or run stop script
```

---

## 🎯 Next Steps

After setup complete:

1. ✅ Test all endpoints with Postman
2. ✅ Connect frontend (Vue.js)
3. ✅ Monitor logs for errors
4. ✅ Add more test cases
5. ✅ Deploy to production

---

## 📚 References

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Ollama Docs**: https://ollama.com/docs
- **LangChain Docs**: https://python.langchain.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

---

**Setup Complete! 🎉**

Your chatbot API is now running at **http://localhost:5000**

Open http://localhost:5000/docs for interactive API documentation.