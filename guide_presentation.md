# 📚 GUIDE PRESENTATION: Geotags Chatbot Service

## RAG-Based Chatbot untuk Pencarian Informasi Usaha di Balikpapan

---

## 📋 DAFTAR ISI

1. [Gambaran Umum Sistem](#1-gambaran-umum-sistem)
2. [Arsitektur Sistem](#2-arsitektur-sistem)
3. [Komponen Utama](#3-komponen-utama)
4. [Penjelasan Metode per Modul](#4-penjelasan-metode-per-modul)
5. [Penjelasan Variabel Penting](#5-penjelasan-variabel-penting)
6. [Alur Kerja Sistem](#6-alur-kerja-sistem)
7. [API Endpoints](#7-api-endpoints)
8. [Konfigurasi dan Environment](#8-konfigurasi-dan-environment)
9. [Evaluasi Sistem](#9-evaluasi-sistem)

---

## 1. GAMBARAN UMUM SISTEM

### 1.1 Deskripsi

**Geotags Chatbot Service** adalah layanan chatbot berbasis **RAG (Retrieval Augmented Generation)** yang dirancang untuk menjawab pertanyaan tentang data usaha/bisnis di wilayah Balikpapan. Sistem ini menggabungkan:

- **Semantic Search** menggunakan Sentence Transformers
- **Vector Database** menggunakan FAISS
- **Large Language Model** menggunakan Ollama (llama3.2)
- **Async Database** menggunakan PostgreSQL dengan asyncpg

### 1.2 Fitur Utama

| Fitur                     | Deskripsi                                |
| ------------------------- | ---------------------------------------- |
| ✅ **RAG Pipeline**       | Semantic search + LLM generation         |
| ✅ **Async Operations**   | Full async/await untuk performa optimal  |
| ✅ **JWT Authentication** | Kompatibel dengan backend yang sudah ada |
| ✅ **Auto-Sync**          | Sinkronisasi otomatis dengan database    |
| ✅ **Hybrid Queries**     | Kombinasi RAG + database statistics      |
| ✅ **Evaluation Mode**    | Mode evaluasi khusus untuk testing       |

### 1.3 Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│                    TECH STACK                           │
├─────────────────────────────────────────────────────────┤
│  Framework      : FastAPI (Python)                      │
│  Database       : PostgreSQL + asyncpg                  │
│  Vector DB      : FAISS (Facebook AI Similarity Search) │
│  Embeddings     : Sentence-Transformers (all-MiniLM-L6) │
│  LLM            : Ollama (llama3.2)                     │
│  Authentication : JWT (PyJWT)                           │
│  Configuration  : Pydantic Settings                     │
└─────────────────────────────────────────────────────────┘
```

---

## 2. ARSITEKTUR SISTEM

### 2.1 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Frontend/API Consumer)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               FastAPI Server                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   /api/chat     │  │  /api/businesses│  │   /api/health   │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
└───────────┼────────────────────┼────────────────────┼────────────────────────┘
            │                    │                    │
            ▼                    ▼                    │
┌───────────────────────┐ ┌──────────────────────────┐│
│  AUTH MIDDLEWARE      │ │      JWT Verification    ││
│  (get_current_user)   │ │                          ││
└───────────┬───────────┘ └──────────────────────────┘│
            │                                         │
            ▼                                         │
┌───────────────────────────────────────────────────────────────────────────────┐
│                           CHATBOT SERVICE                                      │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐       │
│  │  Query Validation  │→ │  Intent Detection  │→ │  Response Generation│      │
│  │  is_valid_query()  │  │  is_counting_query │  │  generate_response() │      │
│  │                    │  │  is_filtering_query│  │                      │      │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────────┘
            │                        │
            ▼                        ▼
┌────────────────────────┐  ┌────────────────────────┐
│      RAG SERVICE       │  │      DATABASE          │
│  ┌──────────────────┐  │  │  ┌──────────────────┐  │
│  │  Sentence        │  │  │  │  PostgreSQL      │  │
│  │  Transformer     │  │  │  │  (asyncpg)       │  │
│  │  (Embeddings)    │  │  │  │                  │  │
│  └──────────────────┘  │  │  └──────────────────┘  │
│  ┌──────────────────┐  │  │  ┌──────────────────┐  │
│  │  FAISS Index     │  │  │  │  usaha_llm view  │  │
│  │  (Vector Search) │  │  │  │  (Business Data) │  │
│  └──────────────────┘  │  │  └──────────────────┘  │
└────────────────────────┘  └────────────────────────┘
            │
            ▼
┌────────────────────────┐
│    OLLAMA LLM          │
│    (llama3.2)          │
│                        │
│  Natural Language      │
│  Response Generation   │
└────────────────────────┘
```

### 2.2 Struktur Direktori

```
capstone-ai2/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── config.py             # Configuration management (Pydantic Settings)
│   ├── database.py           # Async PostgreSQL operations
│   ├── auth.py               # JWT authentication middleware
│   ├── rag_service.py        # RAG implementation (embeddings + FAISS)
│   ├── chatbot_service.py    # Chatbot logic with Ollama integration
│   └── routes/
│       ├── __init__.py
│       └── chatbot.py        # API endpoint definitions
├── evaluation/               # Evaluation tools and results
│   ├── evaluate_chatbot.py   # Evaluation script
│   ├── generate_responses.py # Response generator for evaluation
│   └── *.json                # Evaluation results
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
└── docker-compose.yml        # Docker Compose configuration
```

---

## 3. KOMPONEN UTAMA

### 3.1 Overview Komponen

| File                 | Class/Module       | Fungsi                                    |
| -------------------- | ------------------ | ----------------------------------------- |
| `main.py`            | `app` (FastAPI)    | Entry point aplikasi, lifespan management |
| `config.py`          | `Settings`         | Manajemen konfigurasi dari environment    |
| `database.py`        | `Database`         | Operasi database async                    |
| `auth.py`            | `get_current_user` | JWT authentication                        |
| `rag_service.py`     | `RAGService`       | Semantic search dengan embeddings         |
| `chatbot_service.py` | `ChatbotService`   | Logika chatbot dan LLM integration        |
| `routes/chatbot.py`  | `router`           | API endpoint definitions                  |

---

## 4. PENJELASAN METODE PER MODUL

### 4.1 Module: `config.py` (Settings)

```python
class Settings(BaseSettings):
    """Manajemen konfigurasi menggunakan Pydantic Settings"""
```

| Metode/Property     | Tipe       | Deskripsi                                     |
| ------------------- | ---------- | --------------------------------------------- |
| `cors_origins_list` | `property` | Mengkonversi string CORS origins menjadi list |

**Penjelasan Detail:**

```python
@property
def cors_origins_list(self) -> List[str]:
    """
    Parse CORS origins from comma-separated string

    Input: "http://localhost:3000,http://localhost:8080"
    Output: ["http://localhost:3000", "http://localhost:8080"]
    """
    return [origin.strip() for origin in self.cors_origins.split(",")]
```

---

### 4.2 Module: `auth.py` (Authentication)

```python
def get_current_user(request: Request) -> Dict[str, Any]:
    """JWT authentication middleware"""
```

| Metode             | Parameter          | Return           | Deskripsi                                         |
| ------------------ | ------------------ | ---------------- | ------------------------------------------------- |
| `get_current_user` | `request: Request` | `Dict[str, Any]` | Memvalidasi JWT token dan mengembalikan user info |

**Alur Kerja:**

```
1. Ambil header "Authorization"
2. Validasi format "Bearer <token>"
3. Decode JWT menggunakan secret key
4. Return {user_id, role} atau raise HTTPException
```

**Exception yang Dihandle:**

- `jwt.ExpiredSignatureError`: Token sudah kadaluarsa
- `jwt.InvalidTokenError`: Token tidak valid

---

### 4.3 Module: `database.py` (Database)

```python
class Database:
    """Async PostgreSQL database manager"""
```

#### Tabel Metode Database

| #   | Metode                             | Parameter                           | Return               | Deskripsi                                        |
| --- | ---------------------------------- | ----------------------------------- | -------------------- | ------------------------------------------------ |
| 1   | `connect()`                        | -                                   | `None`               | Membuat connection pool ke PostgreSQL            |
| 2   | `disconnect()`                     | -                                   | `None`               | Menutup connection pool                          |
| 3   | `get_all_businesses()`             | -                                   | `List[Dict]`         | Mengambil semua data usaha dari view `usaha_llm` |
| 4   | `get_all_businesses_from_csv()`    | `csv_path: str`                     | `List[Dict]`         | Load data dari CSV untuk evaluation mode         |
| 5   | `search_businesses()`              | `query: str, limit: int`            | `List[Dict]`         | Pencarian dengan ILIKE pattern matching          |
| 6   | `get_businesses_by_filter()`       | `filter_field, filter_value, limit` | `List[Dict]`         | Filter usaha berdasarkan field tertentu          |
| 7   | `get_latest_update_time()`         | -                                   | `Optional[datetime]` | Mendapatkan timestamp update terbaru             |
| 8   | `get_max_business_id()`            | -                                   | `Optional[int]`      | Mendapatkan count total usaha                    |
| 9   | `get_businesses_after_timestamp()` | `last_sync_time, limit`             | `List[Dict]`         | Mengambil usaha yang diupdate setelah timestamp  |
| 10  | `get_business_statistics()`        | -                                   | `Dict[str, Any]`     | Statistik komprehensif usaha                     |

#### Detail Metode Penting

**4.3.1 `connect()`**

```python
async def connect(self):
    """
    Create database connection pool

    Pool Configuration:
    - min_size: 2 (minimum connections)
    - max_size: 10 (maximum connections)
    - command_timeout: 60 seconds
    """
    self.pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=2,
        max_size=10,
        command_timeout=60
    )
```

**4.3.2 `get_all_businesses_from_csv()`**

```python
async def get_all_businesses_from_csv(self, csv_path: str) -> List[Dict]:
    """
    Load businesses from CSV for evaluation mode

    Proses:
    1. Baca CSV dengan delimiter ';'
    2. Transform setiap row ke format usaha_llm
    3. Generate UUID untuk setiap usaha
    4. Set default values untuk field yang kosong

    Column Mapping:
    - 'nama tempat' → nama_usaha
    - 'alamat' → alamat
    - 'kategori' → kategori
    """
```

**4.3.3 `get_business_statistics()`**

```python
async def get_business_statistics(self) -> Dict[str, Any]:
    """
    Get comprehensive statistics

    Returns:
    {
        "total": int,                    # Total semua usaha
        "by_category": [{                # Per kategori (top 10)
            "category": str,
            "count": int
        }],
        "by_district": [{                # Per kecamatan
            "district": str,
            "count": int
        }],
        "by_subdistrict": [{             # Per kelurahan (top 10)
            "subdistrict": str,
            "count": int
        }],
        "by_status": {                   # Per status
            "aktif": int,
            "Tidak Aktif": int
        },
        "by_source": {                   # Per sumber data
            "geotags": int,
            "prelist": int
        }
    }
    """
```

---

### 4.4 Module: `rag_service.py` (RAG Service)

```python
class RAGService:
    """RAG service for semantic search over business data"""
```

#### Tabel Metode RAG Service

| #   | Metode                    | Parameter                     | Return       | Deskripsi                              |
| --- | ------------------------- | ----------------------------- | ------------ | -------------------------------------- |
| 1   | `initialize()`            | -                             | `None`       | Load sentence transformer model        |
| 2   | `_create_document_text()` | `business: Dict`              | `str`        | Buat text representasi untuk embedding |
| 3   | `index_documents()`       | `businesses: List[Dict]`      | `None`       | Index semua dokumen ke FAISS           |
| 4   | `search()`                | `query, top_k, min_relevance` | `List[Dict]` | Semantic search                        |
| 5   | `add_documents()`         | `new_businesses: List[Dict]`  | `None`       | Tambah dokumen baru (incremental)      |
| 6   | `sync_if_needed()`        | `db`                          | `bool`       | Auto-sync dengan database              |
| 7   | `format_context()`        | `results: List[Dict]`         | `str`        | Format hasil search untuk LLM          |

#### Detail Metode Penting

**4.4.1 `initialize()`**

```python
async def initialize(self):
    """
    Load the sentence transformer model

    Model: all-MiniLM-L6-v2
    - Lightweight dan cepat
    - 384-dimensional embeddings
    - Multilingual support
    """
    self.model = SentenceTransformer(self.model_name)
```

**4.4.2 `_create_document_text()`**

```python
def _create_document_text(self, business: Dict) -> str:
    """
    Create searchable text from business data

    Format Output:
    "Nama: {nama_usaha} | Nama Komersial: {nama_komersial} |
     Alamat: {alamat} | Kecamatan: {nmkec} | Kabupaten: {nmkab} |
     Kategori: {kategori} | Produk: {produk_utama} | Status: {status}"

    Tujuan: Menggabungkan semua informasi penting menjadi satu text
    yang dapat di-embed untuk semantic search
    """
```

**4.4.3 `index_documents()`**

```python
async def index_documents(self, businesses: List[Dict]):
    """
    Index business documents for semantic search

    Proses:
    1. Simpan dokumen asli di self.documents
    2. Buat text representation untuk setiap dokumen
    3. Generate embeddings menggunakan sentence-transformer
    4. Buat FAISS index (IndexFlatL2)
    5. Tambahkan embeddings ke index
    6. Inisialisasi tracking untuk auto-sync (UUID mapping)

    FAISS Index Type: IndexFlatL2
    - Euclidean distance (L2)
    - Exact search (no approximation)
    - Suitable for < 100k documents
    """
```

**4.4.4 `search()`**

```python
async def search(
    self,
    query: str,
    top_k: int = 5,
    min_relevance: float = 0.2
) -> List[Dict]:
    """
    Semantic search for relevant businesses

    Parameter:
    - query: User query string
    - top_k: Jumlah hasil maksimum (default: 5)
    - min_relevance: Threshold relevance score (0-1, default: 0.2)

    Proses:
    1. Encode query menjadi embedding
    2. Search di FAISS index (3x top_k untuk filtering)
    3. Konversi L2 distance ke similarity score: 1 / (1 + distance)
    4. Filter hasil dengan min_relevance threshold
    5. Return top-k hasil dengan relevance_score

    Relevance Score Formula:
    score = 1 / (1 + L2_distance)
    - Range: 0 to 1
    - Semakin tinggi = semakin relevan
    """
```

**4.4.5 `sync_if_needed()`**

```python
async def sync_if_needed(self, db) -> bool:
    """
    Check database for new data and sync if needed

    Mekanisme:
    1. Rate limiting: Skip jika check terakhir < interval
    2. Get latest update time dari database
    3. Compare dengan last_sync_time
    4. Jika ada data baru, fetch dan add ke index

    Tracking Method: Timestamp-based dengan UUID mapping
    - Tidak menggunakan sequential ID
    - Menggunakan updated_at timestamp
    - Map usaha_id (UUID) ke index position
    """
```

**4.4.6 `format_context()`**

```python
def format_context(self, results: List[Dict]) -> str:
    """
    Format search results into context for LLM

    Output Format:
    "Berikut adalah data usaha yang relevan:

    1. NAMA USAHA
       Nama Komersial: xxx
       Alamat: xxx
       Kategori: xxx
       Produk Utama: xxx
       Status: xxx
       Koordinat: lat, lng

    2. NAMA USAHA 2
       ..."
    """
```

---

### 4.5 Module: `chatbot_service.py` (Chatbot Service)

```python
class ChatbotService:
    """Chatbot service using Ollama for LLM responses"""
```

#### Tabel Metode Chatbot Service

| #   | Metode                 | Parameter                     | Return                  | Deskripsi                    |
| --- | ---------------------- | ----------------------------- | ----------------------- | ---------------------------- |
| 1   | `is_valid_query()`     | `message: str`                | `tuple[bool, str]`      | Validasi query               |
| 2   | `is_counting_query()`  | `message: str`                | `bool`                  | Deteksi query statistik      |
| 3   | `is_filtering_query()` | `message: str`                | `tuple[bool, str, str]` | Deteksi query filter         |
| 4   | `generate_response()`  | `message, context, history`   | `str`                   | Generate response dengan LLM |
| 5   | `process_query()`      | `message, top_k, history, db` | `Dict`                  | Proses query end-to-end      |

#### Detail Metode Penting

**4.5.1 `is_valid_query()`**

```python
def is_valid_query(self, message: str) -> tuple[bool, str]:
    """
    Validate if query is clear enough to process

    Validasi:
    1. Panjang minimum: 3 karakter
    2. Bukan kata generik: 'tes', 'test', 'coba', 'halo', dll

    Returns:
    - (True, "") jika valid
    - (False, "error message") jika tidak valid
    """
```

**4.5.2 `is_counting_query()`**

```python
def is_counting_query(self, message: str) -> bool:
    """
    Detect if query is asking for counts/statistics

    Keywords yang dideteksi:
    - "berapa", "jumlah", "total", "banyak", "ada berapa"
    - "hitung", "count", "statistik", "data"

    Contoh:
    - "Berapa jumlah usaha di Balikpapan?" → True
    - "Cari rumah makan" → False
    """
```

**4.5.3 `is_filtering_query()`**

```python
def is_filtering_query(self, message: str) -> tuple[bool, str, str]:
    """
    Detect if query is asking for filtered list

    Filter Types:
    1. Status: "tidak aktif", "nonaktif", "tutup", "aktif"
    2. Category: (extensible)

    Returns: (is_filtering, filter_type, filter_value)

    Contoh:
    - "Tampilkan usaha tidak aktif" → (True, 'status', 'tidak aktif')
    - "Cari bakso" → (False, '', '')
    """
```

**4.5.4 `generate_response()`**

```python
async def generate_response(
    self,
    message: str,
    context: str,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Generate chatbot response using Ollama

    Proses:
    1. Build messages array dengan system prompt
    2. Tambahkan conversation history (max 6 messages terakhir)
    3. Gabungkan context + user message
    4. Kirim ke Ollama untuk generate response

    System Prompt berisi:
    - Aturan untuk angka/statistik
    - Aturan untuk data tidak ditemukan
    - Aturan untuk pertanyaan tidak jelas
    - Gaya penulisan (langsung, profesional)
    """
```

**4.5.5 `process_query()` - METODE UTAMA**

```python
async def process_query(
    self,
    message: str,
    top_k: int = 5,
    conversation_history: Optional[List[Dict]] = None,
    db = None
) -> Dict[str, Any]:
    """
    Process user query end-to-end: RAG retrieval + LLM generation

    Return Structure:
    {
        "response": str,       # Jawaban chatbot
        "sources": List[Dict], # Sumber data yang digunakan
        "context_used": bool,  # Apakah context digunakan
        "query_type": str      # "invalid" | "filtering" | "counting" | "search"
    }

    Alur Pemrosesan:

    ┌─────────────────────┐
    │  1. Validate Query  │
    │  is_valid_query()   │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐     ┌─────────────────────┐
    │  2. Check Filtering │────▶│ Database Filtering  │
    │  is_filtering_query │     │ get_businesses_by_  │
    └──────────┬──────────┘     │ filter()            │
               │                └─────────────────────┘
    ┌──────────▼──────────┐     ┌─────────────────────┐
    │  3. Check Counting  │────▶│ Hybrid Approach     │
    │  is_counting_query  │     │ Stats + RAG Examples│
    └──────────┬──────────┘     └─────────────────────┘
               │
    ┌──────────▼──────────┐
    │  4. Regular Search  │
    │  rag_service.search │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  5. Generate Resp.  │
    │  generate_response()│
    └─────────────────────┘
    """
```

---

### 4.6 Module: `routes/chatbot.py` (API Endpoints)

#### Tabel Endpoint

| #   | Method | Path                    | Auth   | Deskripsi                           |
| --- | ------ | ----------------------- | ------ | ----------------------------------- |
| 1   | POST   | `/api/chat`             | ✅ JWT | Send message ke chatbot             |
| 2   | GET    | `/api/businesses`       | ✅ JWT | Get all businesses dengan statistik |
| 3   | GET    | `/api/health`           | ❌     | Health check                        |
| 4   | GET    | `/api/admin/sync-stats` | ✅ JWT | Get RAG sync statistics             |

#### Model Request/Response

**ChatRequest:**

```python
class ChatRequest(BaseModel):
    message: str           # User message (1-1000 chars)
    conversation_history: Optional[List[Dict[str, str]]]  # Previous messages
    top_k: int = 5         # Number of docs to retrieve (1-20)
```

**ChatResponse:**

```python
class ChatResponse(BaseModel):
    response: str              # Chatbot answer
    sources: List[Dict]        # Source businesses used
    context_used: bool         # Whether context was used
    user_id: str              # Authenticated user ID
```

**BusinessResponse:**

```python
class BusinessResponse(BaseModel):
    businesses: List[Dict]     # All business data
    total: int                 # Total count
    statistics: BusinessStatistics  # Comprehensive stats
```

---

### 4.7 Module: `main.py` (Application Entry Point)

#### Lifespan Manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    STARTUP:
    1. Connect to database (db.connect())
    2. Initialize RAG service (rag_service.initialize())
    3. Load businesses berdasarkan mode:
       - EVALUATION: get_all_businesses_from_csv()
       - PRODUCTION: get_all_businesses()
    4. Index documents (rag_service.index_documents())

    SHUTDOWN:
    1. Disconnect database (db.disconnect())
    """
```

---

## 5. PENJELASAN VARIABEL PENTING

### 5.1 Variabel di `config.py` (Settings)

| Variabel                    | Tipe   | Default                    | Deskripsi                         |
| --------------------------- | ------ | -------------------------- | --------------------------------- |
| `jwt_secret_key`            | `str`  | -                          | Secret key untuk JWT verification |
| `jwt_algorithm`             | `str`  | `"HS256"`                  | Algoritma JWT                     |
| `database_url`              | `str`  | Required                   | PostgreSQL connection string      |
| `chatbot_model`             | `str`  | `"llama3.2"`               | Nama model Ollama                 |
| `ollama_base_url`           | `str`  | `"http://localhost:11434"` | URL Ollama server                 |
| `rag_sync_interval_seconds` | `int`  | `60`                       | Interval auto-sync (detik)        |
| `evaluation_mode`           | `bool` | `False`                    | Mode evaluasi on/off              |
| `evaluation_csv_path`       | `str`  | `"output.csv"`             | Path CSV untuk evaluasi           |
| `host`                      | `str`  | `"0.0.0.0"`                | Server host                       |
| `port`                      | `int`  | `8000`                     | Server port                       |
| `cors_origins`              | `str`  | `"localhost:3000,..."`     | Allowed CORS origins              |

### 5.2 Variabel di `database.py` (Database)

| Variabel | Tipe                     | Deskripsi                     |
| -------- | ------------------------ | ----------------------------- |
| `pool`   | `Optional[asyncpg.Pool]` | Connection pool ke PostgreSQL |

### 5.3 Variabel di `rag_service.py` (RAGService)

| Variabel                | Tipe                            | Deskripsi                                              |
| ----------------------- | ------------------------------- | ------------------------------------------------------ |
| `model_name`            | `str`                           | Nama model sentence-transformer (`"all-MiniLM-L6-v2"`) |
| `model`                 | `Optional[SentenceTransformer]` | Instance model untuk embedding                         |
| `index`                 | `Optional[faiss.Index]`         | FAISS vector index                                     |
| `documents`             | `List[Dict]`                    | Dokumen asli yang di-index                             |
| `embeddings`            | `Optional[np.ndarray]`          | Matrix embeddings semua dokumen                        |
| `last_check_time`       | `Optional[datetime]`            | Waktu pengecekan sync terakhir                         |
| `last_sync_time`        | `Optional[datetime]`            | Waktu sinkronisasi terakhir                            |
| `usaha_id_to_index`     | `Dict[str, int]`                | Mapping UUID → index position                          |
| `sync_interval_seconds` | `int`                           | Interval cek sync (dari config)                        |
| `sync_stats`            | `Dict`                          | Statistik sinkronisasi                                 |

**sync_stats structure:**

```python
sync_stats = {
    'total_checks': 0,           # Total pengecekan yang dilakukan
    'found_new_data': 0,         # Berapa kali ditemukan data baru
    'last_sync': None,           # Waktu sync terakhir
    'total_documents_added': 0   # Total dokumen yang ditambahkan via sync
}
```

### 5.4 Variabel di `chatbot_service.py` (ChatbotService)

| Variabel        | Tipe            | Deskripsi                                                |
| --------------- | --------------- | -------------------------------------------------------- |
| `model`         | `str`           | Nama model Ollama (dari settings)                        |
| `client`        | `ollama.Client` | Client untuk komunikasi dengan Ollama                    |
| `system_prompt` | `str`           | Prompt sistem yang berisi aturan dan instruksi untuk LLM |

**system_prompt key points:**

```
1. Aturan untuk angka/statistik
   - Gunakan angka TOTAL dari kotak ╔═══╗
   - Jangan gunakan angka kategori sebagai total

2. Aturan untuk data tidak ditemukan
   - Katakan "Tidak ditemukan informasi tentang X"
   - Jangan berikan alternatif yang tidak diminta

3. Aturan untuk pertanyaan tidak jelas
   - Minta klarifikasi
   - Jangan listing semua data

4. Gaya penulisan
   - Langsung ke poin utama
   - Tanpa salam berlebihan
   - Profesional
```

### 5.5 Variabel Global (Singleton Instances)

| File                 | Variabel          | Tipe             | Deskripsi                       |
| -------------------- | ----------------- | ---------------- | ------------------------------- |
| `config.py`          | `settings`        | `Settings`       | Global configuration instance   |
| `database.py`        | `db`              | `Database`       | Global database instance        |
| `rag_service.py`     | `rag_service`     | `RAGService`     | Global RAG service instance     |
| `chatbot_service.py` | `chatbot_service` | `ChatbotService` | Global chatbot service instance |

---

## 6. ALUR KERJA SISTEM

### 6.1 Alur Startup

```
┌───────────────────────────────────────────────────────────────────┐
│                        APPLICATION STARTUP                         │
└───────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌────────────────────┐
│ 1. Database   │    │ 2. RAG Service  │    │ 3. Load Documents  │
│    Connect    │    │    Initialize   │    │                    │
│               │    │                 │    │ if EVAL_MODE:      │
│ asyncpg pool  │    │ Load Sentence   │    │   load from CSV    │
│ min=2, max=10 │    │ Transformer     │    │ else:              │
└───────────────┘    └─────────────────┘    │   load from DB     │
                                            └────────────────────┘
                                                      │
                                                      ▼
                                            ┌────────────────────┐
                                            │ 4. Index Documents │
                                            │                    │
                                            │ - Create texts     │
                                            │ - Generate embeds  │
                                            │ - Build FAISS idx  │
                                            │ - Init UUID map    │
                                            └────────────────────┘
                                                      │
                                                      ▼
                                            ┌────────────────────┐
                                            │  ✅ SERVICE READY  │
                                            └────────────────────┘
```

### 6.2 Alur Chat Request

```
┌───────────────────────────────────────────────────────────────────┐
│                      CHAT REQUEST FLOW                             │
└───────────────────────────────────────────────────────────────────┘

User Request: POST /api/chat
{
  "message": "Cari rumah makan di Balikpapan Selatan",
  "top_k": 5
}
        │
        ▼
┌───────────────────┐
│  1. JWT Auth      │ ── Token Invalid ──▶ 401 Unauthorized
│  get_current_user │
└────────┬──────────┘
         │ Token Valid
         ▼
┌───────────────────┐
│  2. Auto-Sync     │
│  sync_if_needed() │ ── Check interval, sync jika ada data baru
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  3. Validate      │ ── Invalid ──▶ Return error message
│  is_valid_query() │
└────────┬──────────┘
         │ Valid
         ▼
┌────────────────────────────────────────────────────────────┐
│  4. Intent Detection & Routing                              │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ Filtering Query │    │ Counting Query  │                │
│  │ "usaha tidak    │    │ "berapa jumlah  │                │
│  │  aktif"         │    │  usaha?"        │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           │                      │                         │
│           ▼                      ▼                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ DB Filter       │    │ Hybrid Approach │                │
│  │ get_businesses_ │    │ Statistics +    │                │
│  │ by_filter()     │    │ RAG Examples    │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           │                      │                         │
│           └──────────┬───────────┘                         │
│                      │                                      │
│  ┌─────────────────┐ │                                      │
│  │ Regular Search  │◀┘ (default path)                      │
│  │                 │                                        │
│  │ rag_service.    │                                        │
│  │ search()        │                                        │
│  └────────┬────────┘                                        │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────┐
│  5. Format Context│ ── rag_service.format_context()
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  6. LLM Generate  │
│  Ollama llama3.2  │
│                   │
│  System Prompt +  │
│  Context +        │
│  User Message     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  7. Return        │
│  Response         │
│  {                │
│    response,      │
│    sources,       │
│    context_used,  │
│    user_id        │
│  }                │
└───────────────────┘
```

### 6.3 Alur Auto-Sync

```
┌───────────────────────────────────────────────────────────────────┐
│                        AUTO-SYNC FLOW                              │
└───────────────────────────────────────────────────────────────────┘

Triggered: Setiap chat request

        ┌───────────────────┐
        │  Check Interval   │ ── now - last_check < interval ──▶ Skip
        │  (default: 60s)   │
        └────────┬──────────┘
                 │ interval exceeded
                 ▼
        ┌───────────────────┐
        │  Get Latest       │
        │  Update Time      │ ── DB Query: MAX(updated_at)
        │  from Database    │
        └────────┬──────────┘
                 │
                 ▼
        ┌───────────────────┐
        │  Compare with     │ ── latest_db_time <= last_sync_time ──▶ No Update
        │  Last Sync Time   │
        └────────┬──────────┘
                 │ new data detected
                 ▼
        ┌───────────────────┐
        │  Fetch New/       │
        │  Updated Records  │ ── WHERE updated_at > last_sync_time
        │  (limit: 1000)    │
        └────────┬──────────┘
                 │
                 ▼
        ┌───────────────────┐
        │  Add Documents    │
        │  to Index         │
        │                   │
        │  - Generate embeds│
        │  - Add to FAISS   │
        │  - Update mapping │
        └────────┬──────────┘
                 │
                 ▼
        ┌───────────────────┐
        │  Update Stats     │
        │  - last_sync_time │
        │  - sync_stats     │
        └───────────────────┘
```

---

## 7. API ENDPOINTS

### 7.1 POST /api/chat

**Deskripsi:** Kirim pesan ke chatbot dan dapatkan respons

**Request:**

```http
POST /api/chat HTTP/1.1
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
  "response": "Berikut usaha sembako di Balikpapan:\n\n1. SEMBAKO MUKHLAS...",
  "sources": [
    {
      "usaha_id": "2a27f57a-...",
      "nama_usaha": "SEMBAKO MUKHLAS",
      "alamat": "Pasar sepinggan",
      "kategori": "Sembako",
      "relevance_score": 0.89
    }
  ],
  "context_used": true,
  "user_id": "4f683f4a-..."
}
```

### 7.2 GET /api/businesses

**Deskripsi:** Ambil semua data usaha dengan statistik

**Request:**

```http
GET /api/businesses HTTP/1.1
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "businesses": [...],
  "total": 614,
  "statistics": {
    "total": 614,
    "by_category": [
      {"category": "Rumah Makan", "count": 349},
      {"category": "Toko", "count": 120}
    ],
    "by_district": [
      {"district": "BALIKPAPAN SELATAN", "count": 180}
    ],
    "by_subdistrict": [...],
    "by_status": {"aktif": 612, "Tidak Aktif": 2},
    "by_source": {"geotags": 100, "prelist": 514}
  }
}
```

### 7.3 GET /api/health

**Deskripsi:** Health check (tanpa autentikasi)

**Response:**

```json
{
  "status": "healthy",
  "service": "geotags-chatbot",
  "version": "1.0.0"
}
```

### 7.4 GET /api/admin/sync-stats

**Deskripsi:** Statistik auto-sync RAG

**Response:**

```json
{
  "total_checks": 150,
  "found_new_data": 3,
  "last_sync": "2024-12-19T10:30:00",
  "total_documents_added": 45,
  "current_document_count": 614,
  "last_sync_time": "2024-12-19T10:30:00",
  "last_check_time": "2024-12-19T14:15:00",
  "sync_interval_seconds": 60,
  "tracking_method": "timestamp-based (UUID)",
  "tracked_businesses": 614
}
```

---

## 8. KONFIGURASI DAN ENVIRONMENT

### 8.1 File .env

```env
# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Chatbot Configuration
CHATBOT_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434

# RAG Configuration
RAG_SYNC_INTERVAL_SECONDS=60

# Evaluation Mode
EVALUATION_MODE=false
EVALUATION_CSV_PATH=output_for_eval.csv

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 8.2 Database View: usaha_llm

```sql
-- Struktur view usaha_llm
CREATE VIEW usaha_llm AS
SELECT
    source,           -- geotags | prelist
    usaha_id,         -- UUID
    user_id,          -- UUID (owner)
    nama_usaha,       -- Nama usaha
    nama_komersial_usaha,
    alamat,           -- Alamat lengkap
    kdprov, kdkab, kdkec, kddesa,  -- Kode wilayah
    nmprov, nmkab, nmkec, nmdesa,  -- Nama wilayah
    kbli_section, kbli_code, kbli_title,  -- KBLI
    kategori,         -- Kategori usaha
    produk_utama,     -- Produk utama
    status,           -- aktif | Tidak Aktif
    latitude, longitude,  -- Koordinat
    created_at, updated_at  -- Timestamps
FROM ...
```

---

## 9. EVALUASI SISTEM

### 9.1 Mode Evaluasi

Sistem dapat dijalankan dalam mode evaluasi untuk testing:

```env
EVALUATION_MODE=true
EVALUATION_CSV_PATH=output_for_eval.csv
```

### 9.2 Proses Evaluasi

```
1. Generate Responses (generate_responses.py)
   - Jalankan query test terhadap API
   - Simpan response ke JSON

2. Evaluate (evaluate_chatbot.py)
   - Bandingkan response dengan golden truth
   - Hitung metrik: accuracy, relevance
   - Generate report
```

### 9.3 Metrik Evaluasi

| Metrik          | Deskripsi                                |
| --------------- | ---------------------------------------- |
| Accuracy        | Kecocokan dengan jawaban yang diharapkan |
| Relevance Score | Skor relevansi dari RAG search           |
| Response Time   | Waktu respons API                        |

---

## 📝 KESIMPULAN

Geotags Chatbot Service adalah sistem RAG-based yang menggabungkan:

1. **Semantic Search** - Menggunakan sentence-transformers untuk memahami makna query
2. **Vector Database** - FAISS untuk pencarian cepat pada embeddings
3. **LLM Integration** - Ollama llama3.2 untuk generate natural language response
4. **Async Operations** - Full async/await untuk performa optimal
5. **Auto-Sync** - Sinkronisasi otomatis dengan database
6. **Hybrid Queries** - Kombinasi RAG + database untuk query statistik

Sistem ini dirancang untuk membantu pengguna menemukan informasi tentang usaha/bisnis di Balikpapan dengan cara yang natural dan intuitif.

---

_Dokumen ini di-generate pada: 2024-12-19_
_Version: 1.0.0_
