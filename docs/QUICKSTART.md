# 🚀 Quick Start Guide

## Setup Selesai! ✓

Virtual environment dan dependencies sudah terinstall. Sekarang ikuti langkah berikut:

## 1. Konfigurasi Database

Edit file `.env` (copy dari `.env.example` jika belum ada):

```bash
# Copy .env.example ke .env
copy .env.example .env
```

Kemudian edit `.env` dan ganti `DATABASE_URL` dengan connection string PostgreSQL Anda:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

**Contoh:**
```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/geotags
```

## 2. Install dan Setup Ollama

### Download Ollama
- Windows: https://ollama.ai/download/windows
- Atau gunakan: `winget install Ollama.Ollama`

### Jalankan Ollama
```bash
ollama serve
```

### Pull Model llama3.2
```bash
ollama pull llama3.2
```

## 3. Test Setup

Jalankan test script untuk memverifikasi konfigurasi:

```bash
.\venv\Scripts\python.exe test_setup.py
```

Jika semua test passed ✓, lanjut ke step 4.

## 4. Jalankan Server

```bash
run.bat
```

Atau manual:
```bash
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Server akan berjalan di: **http://localhost:8000**

## 5. Test API

### Swagger UI (Interactive Docs)
Buka browser: **http://localhost:8000/docs**

### Test dengan curl

```bash
# Health check (no auth required)
curl http://localhost:8000/api/health

# Chat (requires JWT token)
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Cari warung kopi di Balikpapan\"}"
```

### Test dengan Python

```python
import requests

token = "YOUR_JWT_TOKEN_HERE"
headers = {"Authorization": f"Bearer {token}"}

response = requests.post(
    "http://localhost:8000/api/chat",
    headers=headers,
    json={"message": "Cari usaha sembako di Balikpapan"}
)

print(response.json())
```

## Troubleshooting

### Error: "Database pool not initialized"
- Check DATABASE_URL di file `.env`
- Pastikan PostgreSQL running
- Pastikan view `usaha_llm` exists

### Error: "Ollama connection failed"
- Pastikan Ollama running: `ollama serve`
- Check OLLAMA_BASE_URL di `.env`
- Test: `ollama list` (harus ada llama3.2)

### Error: "Token tidak valid"
- Pastikan JWT_SECRET_KEY sama dengan backend
- Check format: `Bearer <token>`
- Pastikan token belum expired

## File Structure

```
capstone-ai2/
├── app/                    # Main application
│   ├── main.py            # FastAPI app
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection
│   ├── auth.py            # JWT auth
│   ├── rag_service.py     # RAG implementation
│   ├── chatbot_service.py # Chatbot logic
│   └── routes/
│       └── chatbot.py     # API endpoints
├── venv/                  # Virtual environment
├── .env                   # Your configuration (EDIT THIS!)
├── .env.example          # Template
├── requirements.txt      # Dependencies
├── test_setup.py         # Test script
├── setup.bat             # Setup script
├── run.bat               # Run server
└── README.md             # Full documentation
```

## Next Steps

1. ✅ Setup complete
2. ⚠️ Edit `.env` dengan database credentials Anda
3. ⚠️ Install dan jalankan Ollama
4. ⚠️ Run `test_setup.py` untuk verify
5. ⚠️ Start server dengan `run.bat`
6. ✅ Test API di http://localhost:8000/docs

## Support

Lihat `README.md` untuk dokumentasi lengkap.
