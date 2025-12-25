# Geotags Chatbot Service

RAG-based chatbot service untuk aplikasi Geotags yang dapat menjawab pertanyaan tentang data usaha menggunakan PostgreSQL dan Ollama LLM.

## 🚀 Fitur

- ✅ **Async Operations** - Full async/await untuk performa optimal
- ✅ **RAG (Retrieval Augmented Generation)** - Semantic search menggunakan sentence-transformers + FAISS
- ✅ **JWT Authentication** - Kompatibel dengan backend service yang sudah ada
- ✅ **Ollama Integration** - Menggunakan LLM lokal (llama3.2)
- ✅ **PostgreSQL** - Async connection dengan asyncpg
- ✅ **FastAPI** - Modern, cepat, dan auto-generated docs

## 📋 Requirements

- Python 3.11+
- PostgreSQL database dengan view `usaha_llm`
- Ollama dengan model `llama3.2`

## 🛠️ Installation

### Windows

1. **Clone atau download project ini**

2. **Jalankan setup script:**
   ```bash
   setup.bat
   ```
   Script ini akan:
   - Membuat virtual environment
   - Install semua dependencies
   - Membuat file `.env` dari template

3. **Edit file `.env`:**
   ```env
   JWT_SECRET_KEY=your_secret_key_here
   DATABASE_URL=postgresql://user:password@host:port/database
   CHATBOT_MODEL=llama3.2
   OLLAMA_BASE_URL=http://localhost:11434
   ```

4. **Install dan setup Ollama:**
   - Download dari: https://ollama.ai
   - Install dan jalankan: `ollama serve`
   - Pull model: `ollama pull llama3.2`

5. **Jalankan server:**
   ```bash
   run.bat
   ```

### Linux/Mac

1. **Setup virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env dengan konfigurasi Anda
   ```

4. **Run server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🐳 Docker Deployment

```bash
# Build dan run dengan Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📚 API Documentation

Setelah server berjalan, akses dokumentasi interaktif di:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### 1. Chat dengan Chatbot
```http
POST /api/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Cari usaha sembako di Balikpapan",
  "top_k": 5,
  "conversation_history": [
    {"role": "user", "content": "Halo"},
    {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu?"}
  ]
}
```

**Response:**
```json
{
  "response": "Berikut adalah usaha sembako di Balikpapan:\n\n1. SEMBAKO MUKHLAS...",
  "sources": [
    {
      "usaha_id": "2a27f57a-...",
      "nama_usaha": "SEMBAKO MUKHLAS",
      "alamat": "Pasar sepinggan",
      "relevance_score": 0.89
    }
  ],
  "context_used": true,
  "user_id": "4f683f4a-..."
}
```

#### 2. Get All Businesses
```http
GET /api/businesses
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "businesses": [...],
  "total": 150
}
```

#### 3. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "geotags-chatbot",
  "version": "1.0.0"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key untuk JWT verification | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CHATBOT_MODEL` | Ollama model name | `llama3.2` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:8080` |

### Database View Structure

Service ini menggunakan view `usaha_llm` dengan kolom:
- `source`, `usaha_id`, `user_id`
- `nama_usaha`, `nama_komersial_usaha`
- `alamat`, `kdprov`, `kdkab`, `kdkec`, `kddesa`
- `nmprov`, `nmkab`, `nmkec`, `nmdesa`
- `kbli_section`, `kbli_code`, `kbli_title`
- `kategori`, `produk_utama`, `status`
- `latitude`, `longitude`
- `created_at`, `updated_at`

## 🧪 Testing

### Manual Testing dengan curl

```bash
# Get JWT token dari backend service Anda terlebih dahulu
TOKEN="your_jwt_token_here"

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cari warung kopi di Balikpapan",
    "top_k": 3
  }'

# Test get businesses
curl -X GET http://localhost:8000/api/businesses \
  -H "Authorization: Bearer $TOKEN"

# Test health check
curl http://localhost:8000/api/health
```

### Testing dengan Python

```python
import requests

# Your JWT token
token = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {token}"}

# Chat request
response = requests.post(
    "http://localhost:8000/api/chat",
    headers=headers,
    json={
        "message": "Ada usaha bakso di mana?",
        "top_k": 5
    }
)

print(response.json())
```

## 🏗️ Project Structure

```
capstone-ai2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Async PostgreSQL connection
│   ├── auth.py              # JWT authentication
│   ├── rag_service.py       # RAG implementation
│   ├── chatbot_service.py   # Chatbot logic with Ollama
│   └── routes/
│       ├── __init__.py
│       └── chatbot.py       # API endpoints
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore
├── setup.bat               # Windows setup script
├── run.bat                 # Windows run script
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔍 How It Works

1. **Startup:**
   - Connect to PostgreSQL database
   - Load all businesses from `usaha_llm` view
   - Initialize sentence-transformer model
   - Generate embeddings for all businesses
   - Create FAISS vector index

2. **Query Processing:**
   - User sends message via `/api/chat`
   - JWT token verified
   - Message embedded using sentence-transformer
   - FAISS searches for top-k most similar businesses
   - Relevant businesses formatted as context
   - Context + query sent to Ollama LLM
   - LLM generates natural language response
   - Response returned to user

3. **Async Operations:**
   - All database queries are async (asyncpg)
   - All API endpoints are async
   - Multiple users can query simultaneously
   - No blocking operations

## 🚨 Troubleshooting

### Error: "Database pool not initialized"
- Pastikan DATABASE_URL benar
- Check koneksi ke PostgreSQL
- Pastikan view `usaha_llm` exists

### Error: "Ollama connection failed"
- Pastikan Ollama service running: `ollama serve`
- Check OLLAMA_BASE_URL di .env
- Pastikan model sudah di-pull: `ollama pull llama3.2`

### Error: "Token tidak valid"
- Pastikan JWT_SECRET_KEY sama dengan backend service
- Check format token: `Bearer <token>`
- Pastikan token belum expired

### Slow response
- Pertama kali load model akan lambat (download embeddings)
- Ollama inference bisa 2-5 detik tergantung hardware
- Consider menggunakan GPU untuk Ollama

## 📝 License

MIT License

## 👥 Support

Untuk pertanyaan atau issues, silakan buat issue di repository ini.
