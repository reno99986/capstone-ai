# Dokumentasi Lengkap: LLM, Embedding, dan RAG

## Daftar Isi

1. [Pengantar](#pengantar)
2. [Teori Dasar](#teori-dasar)
   - [Large Language Models (LLM)](#large-language-models-llm)
   - [Text Embeddings](#text-embeddings)
   - [Retrieval-Augmented Generation (RAG)](#retrieval-augmented-generation-rag)
3. [Arsitektur Sistem](#arsitektur-sistem)
4. [Implementasi Detail](#implementasi-detail)
5. [Model yang Digunakan](#model-yang-digunakan)
6. [Alur Kerja](#alur-kerja)
7. [Optimasi dan Best Practices](#optimasi-dan-best-practices)

---

## Pengantar

Sistem chatbot Geotags menggunakan arsitektur **RAG (Retrieval-Augmented Generation)** yang menggabungkan:

- **Embedding Model** untuk mengubah teks menjadi vektor
- **Vector Database (FAISS)** untuk pencarian semantik
- **Large Language Model (LLM)** untuk menghasilkan respons natural

Arsitektur ini memungkinkan chatbot memberikan jawaban yang **akurat**, **kontekstual**, dan **grounded** pada data aktual.

---

## Teori Dasar

### Large Language Models (LLM)

#### Apa itu LLM?

**Large Language Model** adalah model neural network yang dilatih pada dataset teks yang sangat besar untuk memahami dan menghasilkan bahasa natural.

#### Arsitektur Transformer

LLM modern menggunakan arsitektur **Transformer** yang terdiri dari:

```
Input Text
    ↓
Tokenization (text → token IDs)
    ↓
Embedding Layer (token IDs → vectors)
    ↓
┌─────────────────────────────────┐
│  Transformer Blocks (N layers)  │
│  ┌───────────────────────────┐  │
│  │  Multi-Head Attention     │  │
│  │  ↓                        │  │
│  │  Add & Normalize          │  │
│  │  ↓                        │  │
│  │  Feed Forward Network     │  │
│  │  ↓                        │  │
│  │  Add & Normalize          │  │
│  └───────────────────────────┘  │
│  (Repeat N times)               │
└─────────────────────────────────┘
    ↓
Output Layer (logits)
    ↓
Softmax (probabilities)
    ↓
Generated Text
```

#### Komponen Utama Transformer

**1. Self-Attention Mechanism**

Attention memungkinkan model "memperhatikan" bagian relevan dari input:

```
Attention(Q, K, V) = softmax(QK^T / √d_k) × V
```

Dimana:

- **Q (Query)**: Apa yang dicari
- **K (Key)**: Apa yang tersedia
- **V (Value)**: Informasi aktual
- **d_k**: Dimensi key (untuk scaling)

**Contoh:**

```
Input: "Cari rumah makan di Balikpapan"

Self-Attention akan menghubungkan:
- "rumah makan" ← "Balikpapan" (lokasi)
- "Cari" ← "rumah makan" (objek pencarian)
```

**2. Multi-Head Attention**

Menjalankan attention paralel dengan "kepala" berbeda:

```
MultiHead(Q, K, V) = Concat(head₁, ..., headₕ) × W^O

head_i = Attention(QW^Q_i, KW^K_i, VW^V_i)
```

Setiap head belajar pola yang berbeda:

- Head 1: Hubungan subjek-predikat
- Head 2: Hubungan lokasi
- Head 3: Hubungan kategori
- dll.

**3. Positional Encoding**

Karena Transformer tidak memiliki urutan bawaan, ditambahkan positional encoding:

```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

#### Model yang Digunakan: Llama 3.2

**Spesifikasi:**

- **Arsitektur**: Transformer Decoder-only
- **Parameter**: ~3B (3 miliar parameter)
- **Context Length**: 8192 tokens
- **Training Data**: Triliunan token dari berbagai sumber
- **Bahasa**: Multilingual (termasuk Indonesia)

**Keunggulan Llama 3.2:**

- Open-source dan dapat di-host lokal
- Performa tinggi untuk ukuran model yang relatif kecil
- Mendukung instruction following
- Efisien untuk inference

---

### Text Embeddings

#### Apa itu Embedding?

**Embedding** adalah representasi vektor numerik dari teks yang menangkap makna semantik.

```
Text: "Rumah makan di Balikpapan"
         ↓
Embedding: [0.23, -0.45, 0.67, ..., 0.12]  (384 dimensi)
```

#### Mengapa Embedding Penting?

1. **Semantic Similarity**: Teks dengan makna mirip memiliki vektor yang dekat
2. **Dimensionality Reduction**: Dari vocabulary tak terbatas → vektor fixed-size
3. **Numerical Operations**: Memungkinkan operasi matematika pada teks

#### Cara Kerja Embedding

**1. Tokenization**

```
Input: "Rumah makan enak"
  ↓
Tokens: ["Rumah", "makan", "enak"]
  ↓
Token IDs: [1234, 5678, 9012]
```

**2. Embedding Lookup**

```
Token ID 1234 → [0.1, 0.2, 0.3, ..., 0.4]  (384 dim)
Token ID 5678 → [0.5, 0.6, 0.7, ..., 0.8]
Token ID 9012 → [0.9, 1.0, 1.1, ..., 1.2]
```

**3. Pooling (Sentence-level)**

Menggabungkan token embeddings menjadi satu vektor kalimat:

```
Mean Pooling:
sentence_embedding = mean([token_emb₁, token_emb₂, ..., token_embₙ])

CLS Pooling:
sentence_embedding = token_emb[CLS]  (token khusus di awal)
```

#### Model yang Digunakan: all-MiniLM-L6-v2

**Spesifikasi:**

- **Arsitektur**: BERT-based (Bidirectional Transformer)
- **Parameter**: 22.7 juta
- **Embedding Dimension**: 384
- **Max Sequence Length**: 256 tokens
- **Training**: Contrastive learning pada 1 miliar pasangan kalimat

**Keunggulan:**

- **Lightweight**: Cepat untuk inference
- **High Quality**: Performa mendekati model besar
- **Multilingual**: Mendukung 50+ bahasa termasuk Indonesia
- **Normalized**: Output vektor sudah di-normalize (cosine similarity ready)

**Training Objective:**

Model dilatih dengan **Contrastive Learning**:

```
Loss = -log(exp(sim(anchor, positive) / τ) /
        Σ exp(sim(anchor, negative_i) / τ))
```

Dimana:

- **anchor**: Kalimat asli
- **positive**: Kalimat dengan makna sama (paraphrase)
- **negative**: Kalimat dengan makna berbeda
- **τ (tau)**: Temperature parameter
- **sim**: Cosine similarity

**Contoh Training:**

```
Anchor:    "Rumah makan di Balikpapan"
Positive:  "Restoran di kota Balikpapan"  → sim = 0.85
Negative:  "Hotel di Jakarta"             → sim = 0.23
```

Model belajar membuat anchor-positive dekat, anchor-negative jauh.

---

### Retrieval-Augmented Generation (RAG)

#### Apa itu RAG?

**RAG** adalah teknik yang menggabungkan **retrieval** (pencarian) dengan **generation** (pembuatan teks) untuk menghasilkan respons yang grounded pada data faktual.

#### Mengapa RAG?

**Masalah LLM Standalone:**

1. **Hallucination**: LLM bisa "mengarang" fakta yang tidak benar
2. **Outdated Knowledge**: Training data bisa sudah lama
3. **No Domain-Specific Data**: Tidak tahu data internal perusahaan
4. **No Source Attribution**: Tidak bisa cite sumber

**Solusi RAG:**

```
User Query → Retrieve Relevant Docs → Augment Prompt → Generate Response
```

#### Arsitektur RAG

```
┌─────────────────────────────────────────────────────────┐
│                    RAG Pipeline                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. INDEXING (Offline)                                  │
│     Documents → Chunks → Embeddings → Vector DB         │
│                                                          │
│  2. RETRIEVAL (Online)                                  │
│     Query → Embedding → Similarity Search → Top-K Docs  │
│                                                          │
│  3. AUGMENTATION (Online)                               │
│     Query + Retrieved Docs → Augmented Prompt           │
│                                                          │
│  4. GENERATION (Online)                                 │
│     Augmented Prompt → LLM → Response                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Komponen RAG

**1. Document Indexing**

```python
# Pseudocode
for document in documents:
    # Chunking (jika perlu)
    chunks = split_document(document, chunk_size=512)

    # Generate embeddings
    for chunk in chunks:
        embedding = embedding_model.encode(chunk)
        vector_db.add(embedding, metadata=chunk)
```

**2. Similarity Search**

Menggunakan **Cosine Similarity**:

```
cosine_sim(A, B) = (A · B) / (||A|| × ||B||)
```

Dimana:

- **A · B**: Dot product
- **||A||**: Magnitude (panjang vektor)

**Range**: -1 (berlawanan) hingga 1 (identik)

**Contoh:**

```
Query: "Rumah makan di Balikpapan"
Query Embedding: [0.2, 0.5, 0.3, ...]

Document 1: "Soto Banjar Azizah di Balikpapan Selatan"
Doc1 Embedding: [0.3, 0.4, 0.4, ...]
Similarity: 0.92 ✓ (Very relevant)

Document 2: "Hotel di Jakarta Pusat"
Doc2 Embedding: [-0.1, 0.1, -0.2, ...]
Similarity: 0.15 ✗ (Not relevant)
```

**3. Vector Database (FAISS)**

**FAISS** (Facebook AI Similarity Search) adalah library untuk efficient similarity search.

**Index Types:**

```
IndexFlatL2: Brute-force L2 distance
- Pros: 100% accurate
- Cons: Slow for large datasets (O(N))
- Use: <10K documents

IndexIVFFlat: Inverted File Index
- Pros: Faster (O(√N))
- Cons: Approximate
- Use: 10K-1M documents

IndexHNSW: Hierarchical Navigable Small World
- Pros: Very fast, high recall
- Cons: More memory
- Use: >1M documents
```

Sistem ini menggunakan **IndexFlatL2** karena dataset <10K.

**4. Prompt Augmentation**

```
Original Query: "Cari rumah makan di Balikpapan"

Retrieved Context:
- Soto Banjar Azizah Bilqis, Jl. Serindit No.123
- Warung Sate Maduratna, Jl. Mulawarman No.207
- BALE FOOD (lalap selatan), Gunung Bahagia

Augmented Prompt:
"""
Konteks data usaha:
1. Soto Banjar Azizah Bilqis
   Alamat: Jl. Serindit No.123, RT.02, Gn. Bahagia
   Kategori: Rumah Makan

2. Warung Sate Maduratna "Pak Sholeh"
   Alamat: Jl. Mulawarman No.207, Sepinggan
   Kategori: Restoran Sate

Pertanyaan pengguna: Cari rumah makan di Balikpapan

Berikan jawaban yang informatif berdasarkan data di atas.
"""
```

#### RAG vs Fine-Tuning

| Aspek           | RAG                  | Fine-Tuning         |
| --------------- | -------------------- | ------------------- |
| **Data Update** | Real-time            | Perlu re-train      |
| **Cost**        | Rendah               | Tinggi (GPU, waktu) |
| **Accuracy**    | Tinggi (grounded)    | Bisa hallucinate    |
| **Flexibility** | Tinggi               | Rendah              |
| **Latency**     | Sedikit lebih tinggi | Rendah              |
| **Use Case**    | Dynamic data         | Static knowledge    |

---

## Arsitektur Sistem

### Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Geotags Chatbot System                    │
└──────────────────────────────────────────────────────────────┘

┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Client    │─────▶│   FastAPI    │─────▶│   PostgreSQL    │
│  (Frontend) │      │   Backend    │      │    Database     │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            ├─────────────────────────────────┐
                            │                                 │
                     ┌──────▼──────┐                  ┌───────▼──────┐
                     │ RAG Service │                  │ LLM Service  │
                     │             │                  │   (Ollama)   │
                     │ - Embedding │                  │              │
                     │ - FAISS     │                  │ - Llama 3.2  │
                     │ - Search    │                  │ - Generation │
                     └─────────────┘                  └──────────────┘
```

### Data Flow

```
1. STARTUP (Indexing)
   PostgreSQL → Get All Businesses → RAG Service
                                          ↓
                                    Embedding Model
                                          ↓
                                    Generate Embeddings
                                          ↓
                                    FAISS Index

2. CHAT REQUEST
   User Query → FastAPI → Auto-Sync Check → RAG Service
                                                  ↓
                                          Query Embedding
                                                  ↓
                                          FAISS Search
                                                  ↓
                                          Top-K Results
                                                  ↓
                              LLM Service ← Format Context
                                   ↓
                              Generate Response
                                   ↓
                              Return to User
```

---

## Implementasi Detail

### 1. Embedding Service

**File:** `app/rag_service.py`

#### Inisialisasi

```python
class RAGService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
```

**Model Loading:**

```python
async def initialize(self):
    logger.info(f"Loading model: {self.model_name}")
    self.model = SentenceTransformer(self.model_name)
    # Model di-download dari HuggingFace (jika belum ada)
    # Disimpan di: ~/.cache/torch/sentence_transformers/
```

#### Document Preparation

```python
def _create_document_text(self, business: Dict[str, Any]) -> str:
    """
    Mengubah structured data menjadi text untuk embedding
    """
    parts = []

    # Business names
    if business.get("nama_usaha"):
        parts.append(f"Nama: {business['nama_usaha']}")

    # Location
    if business.get("alamat"):
        parts.append(f"Alamat: {business['alamat']}")
    if business.get("nmkec"):
        parts.append(f"Kecamatan: {business['nmkec']}")

    # Business info
    if business.get("kategori"):
        parts.append(f"Kategori: {business['kategori']}")

    return " | ".join(parts)
```

**Contoh Output:**

```
Input (JSON):
{
  "nama_usaha": "Soto Banjar Azizah Bilqis",
  "alamat": "Jl. Serindit No.123",
  "nmkec": "BALIKPAPAN SELATAN",
  "kategori": "Rumah Makan"
}

Output (Text):
"Nama: Soto Banjar Azizah Bilqis | Alamat: Jl. Serindit No.123 | Kecamatan: BALIKPAPAN SELATAN | Kategori: Rumah Makan"
```

#### Indexing

```python
async def index_documents(self, businesses: List[Dict[str, Any]]):
    # 1. Prepare texts
    texts = [self._create_document_text(biz) for biz in businesses]

    # 2. Generate embeddings (batch processing)
    self.embeddings = self.model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        batch_size=32  # Process 32 at a time
    )
    # Shape: (N, 384) dimana N = jumlah dokumen

    # 3. Create FAISS index
    dimension = self.embeddings.shape[1]  # 384
    self.index = faiss.IndexFlatL2(dimension)

    # 4. Add embeddings to index
    self.index.add(self.embeddings)
    # FAISS internally: normalize vectors, build index structure
```

**Proses Encoding:**

```
Text → Tokenizer → Token IDs → BERT Model → Token Embeddings → Pooling → Sentence Embedding

"Soto Banjar..."
      ↓
[101, 2342, 5643, ..., 102]  (Token IDs)
      ↓
[[0.1, 0.2, ...],            (Token embeddings)
 [0.3, 0.4, ...],
 ...]
      ↓
[0.25, 0.35, ..., 0.42]      (Mean pooling → sentence embedding)
```

#### Similarity Search

```python
async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    # 1. Encode query
    query_embedding = self.model.encode([query], convert_to_numpy=True)
    # Shape: (1, 384)

    # 2. Search in FAISS
    distances, indices = self.index.search(query_embedding, top_k)
    # distances: L2 distances (lower = more similar)
    # indices: Index positions of top-k results

    # 3. Convert to results
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        result = self.documents[idx].copy()
        # Convert L2 distance to similarity score (0-1)
        result["relevance_score"] = float(1 / (1 + distance))
        results.append(result)

    return results
```

**FAISS Search Internals:**

```
Query Vector: [0.2, 0.5, 0.3, ..., 0.1]
                    ↓
        Calculate L2 Distance to ALL vectors
                    ↓
L2(q, v) = √(Σ(q_i - v_i)²)

Vector 1: distance = 0.12 → score = 1/(1+0.12) = 0.89
Vector 2: distance = 0.45 → score = 1/(1+0.45) = 0.69
Vector 3: distance = 1.23 → score = 1/(1+1.23) = 0.45
...
                    ↓
        Sort by distance (ascending)
                    ↓
        Return top-K
```

#### Incremental Indexing

```python
async def add_documents(self, new_businesses: List[Dict[str, Any]]):
    # 1. Generate embeddings for new docs only
    texts = [self._create_document_text(biz) for biz in new_businesses]
    new_embeddings = self.model.encode(texts, convert_to_numpy=True)

    # 2. Add to FAISS index (O(n) operation)
    self.index.add(new_embeddings)

    # 3. Update tracking
    self.documents.extend(new_businesses)
    self.embeddings = np.vstack([self.embeddings, new_embeddings])
```

**Efficiency:**

- Full re-index 10K docs: ~30-60 seconds
- Incremental add 10 docs: ~0.05 seconds
- **~1000x faster!**

---

### 2. LLM Service

**File:** `app/chatbot_service.py`

#### Inisialisasi

```python
class ChatbotService:
    def __init__(self):
        self.model = settings.chatbot_model  # "llama3.2"
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.system_prompt = """..."""  # Instruction untuk LLM
```

#### System Prompt Engineering

```python
system_prompt = """
Anda adalah asisten chatbot untuk aplikasi Geotags yang membantu
pengguna mencari informasi tentang usaha/bisnis.

Tugas Anda:
1. Menjawab pertanyaan tentang usaha berdasarkan data yang diberikan
2. Memberikan informasi yang akurat dan relevan
3. Jika data tidak tersedia, katakan dengan jelas
4. Gunakan bahasa Indonesia yang sopan dan profesional
5. Fokus pada informasi yang paling relevan dengan pertanyaan
6. Untuk pertanyaan statistik/jumlah, gunakan data statistik yang diberikan

Format jawaban:
- Langsung ke poin utama
- Sertakan detail penting seperti alamat, kategori, dan produk
- Jangan menambahkan informasi yang tidak ada dalam data
- Jangan Berhalusinasi
- Jangan Memberikan data kalau tidak jelas pertanyaannya
"""
```

**Mengapa System Prompt Penting?**

- Mengatur "personality" dan behavior LLM
- Mencegah hallucination
- Memastikan format output konsisten
- Memberikan context tentang domain

#### Response Generation

```python
async def generate_response(
    self,
    message: str,
    context: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    # Build messages
    messages = [
        {"role": "system", "content": self.system_prompt}
    ]

    # Add conversation history (last 3 exchanges)
    if conversation_history:
        messages.extend(conversation_history[-6:])

    # Add current query with context
    user_message = f"""
Konteks data usaha:
{context}

Pertanyaan pengguna: {message}

Berikan jawaban yang informatif berdasarkan data di atas.
"""

    messages.append({"role": "user", "content": user_message})

    # Generate response
    response = self.client.chat(
        model=self.model,
        messages=messages
    )

    return response['message']['content']
```

**Ollama Chat API:**

```
POST http://localhost:11434/api/chat

Request:
{
  "model": "llama3.2",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stream": false
}

Response:
{
  "message": {
    "role": "assistant",
    "content": "Berikut adalah rumah makan di Balikpapan..."
  },
  "done": true
}
```

#### Hybrid Query Processing

```python
async def process_query(
    self,
    message: str,
    top_k: int = 5,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    db = None
) -> Dict[str, Any]:

    # Detect counting query
    is_counting = self.is_counting_query(message)

    if is_counting and db:
        # HYBRID APPROACH: Statistics + Examples
        all_businesses = await db.get_all_businesses()

        # Get examples via RAG
        results = await rag_service.search(message, top_k=5)
        example_context = rag_service.format_context(results)

        # Build hybrid context
        context = f"""
STATISTIK DATABASE (AKURAT):
- Total usaha: {len(all_businesses)}
- Usaha aktif: {count_active}
- Usaha tidak aktif: {count_inactive}

CONTOH USAHA:
{example_context}

PENTING: Gunakan angka statistik di atas untuk menjawab.
"""
    else:
        # REGULAR APPROACH: RAG only
        results = await rag_service.search(message, top_k=top_k)
        context = rag_service.format_context(results)

    # Generate response
    response = await self.generate_response(message, context, conversation_history)

    return {
        "response": response,
        "sources": results,
        "context_used": True
    }
```

**Mengapa Hybrid?**

Untuk counting queries ("berapa jumlah..."):

- **RAG alone**: Hanya lihat top-K docs → tidak akurat
- **Database stats**: Akurat tapi tidak ada contoh
- **Hybrid**: Stats akurat + contoh relevan = best of both worlds

---

## Model yang Digunakan

### 1. Embedding Model: all-MiniLM-L6-v2

**Metadata:**

```yaml
Name: sentence-transformers/all-MiniLM-L6-v2
Type: Sentence Embedding
Base Model: MiniLM (Microsoft)
Parameters: 22.7M
Embedding Dimension: 384
Max Sequence Length: 256 tokens
Training Data: 1B+ sentence pairs
Languages: 50+ (including Indonesian)
License: Apache 2.0
```

**Architecture:**

```
Input: "Rumah makan di Balikpapan"
  ↓
Tokenizer (WordPiece)
  ↓
[CLS] Rumah makan di Balikpapan [SEP]
  ↓
Token IDs: [101, 2342, 5643, 1234, 5678, 102]
  ↓
┌─────────────────────────────────────┐
│  BERT Encoder (6 layers)            │
│  ┌───────────────────────────────┐  │
│  │ Layer 1: Self-Attention       │  │
│  │ Layer 2: Self-Attention       │  │
│  │ Layer 3: Self-Attention       │  │
│  │ Layer 4: Self-Attention       │  │
│  │ Layer 5: Self-Attention       │  │
│  │ Layer 6: Self-Attention       │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
  ↓
Token Embeddings: [[...], [...], [...], ...]
  ↓
Mean Pooling
  ↓
Sentence Embedding: [0.23, -0.45, 0.67, ..., 0.12] (384-dim)
  ↓
L2 Normalization
  ↓
Final Embedding (unit vector)
```

**Performance Benchmarks:**

| Dataset       | Accuracy |
| ------------- | -------- |
| STS Benchmark | 82.41%   |
| SICK-R        | 78.42%   |
| STS12-16      | 76.53%   |

**Inference Speed:**

- CPU (Intel i7): ~50 sentences/second
- GPU (RTX 3060): ~500 sentences/second

### 2. LLM: Llama 3.2

**Metadata:**

```yaml
Name: llama3.2
Developer: Meta AI
Parameters: ~3B
Architecture: Transformer Decoder
Context Length: 8192 tokens
Vocabulary Size: 128K tokens
Training Data: 15T+ tokens
Languages: Multilingual (100+ languages)
License: Llama 3 Community License
```

**Architecture Details:**

```
┌────────────────────────────────────────────┐
│         Llama 3.2 Architecture             │
├────────────────────────────────────────────┤
│                                            │
│  Input Tokens                              │
│    ↓                                       │
│  Token Embedding (128K vocab → 3072 dim)   │
│    ↓                                       │
│  Rotary Position Embedding (RoPE)          │
│    ↓                                       │
│  ┌──────────────────────────────────────┐ │
│  │  Transformer Decoder Blocks (28x)    │ │
│  │  ┌────────────────────────────────┐  │ │
│  │  │ RMSNorm                        │  │ │
│  │  │ Multi-Head Attention (32 heads)│  │ │
│  │  │ RMSNorm                        │  │ │
│  │  │ SwiGLU Feed Forward (11008)    │  │ │
│  │  └────────────────────────────────┘  │ │
│  └──────────────────────────────────────┘ │
│    ↓                                       │
│  RMSNorm                                   │
│    ↓                                       │
│  Output Layer (3072 → 128K logits)         │
│    ↓                                       │
│  Softmax                                   │
│    ↓                                       │
│  Next Token Prediction                     │
│                                            │
└────────────────────────────────────────────┘
```

**Key Features:**

1. **Grouped-Query Attention (GQA)**

   - Reduces memory usage
   - Faster inference
   - 32 query heads, 8 key-value heads

2. **RoPE (Rotary Position Embedding)**

   - Better handling of long sequences
   - Relative position encoding

3. **SwiGLU Activation**

   ```
   SwiGLU(x) = Swish(xW) ⊙ (xV)
   Swish(x) = x · sigmoid(x)
   ```

4. **RMSNorm (Root Mean Square Normalization)**
   ```
   RMSNorm(x) = x / RMS(x) × γ
   RMS(x) = √(mean(x²))
   ```

**Training Process:**

```
Pre-training:
- 15T tokens from web, books, code
- Next token prediction objective
- Batch size: 4M tokens
- Learning rate: 3e-4 with cosine decay

Instruction Tuning:
- Supervised fine-tuning on instruction datasets
- Reinforcement Learning from Human Feedback (RLHF)
- Safety alignment

Result: Model that follows instructions well
```

**Inference with Ollama:**

Ollama provides:

- Model quantization (4-bit, 8-bit)
- Efficient memory management
- Easy API interface
- Local deployment

```bash
# Download model
ollama pull llama3.2

# Run inference
ollama run llama3.2 "Halo, apa kabar?"
```

---

## Alur Kerja

### 1. Startup Flow

```
┌─────────────────────────────────────────────────────────┐
│                   Application Startup                   │
└─────────────────────────────────────────────────────────┘

1. Load Configuration
   ├─ Database URL
   ├─ Ollama URL
   ├─ Model names
   └─ CORS settings

2. Connect to Database
   └─ Create connection pool (2-10 connections)

3. Initialize RAG Service
   ├─ Load embedding model (all-MiniLM-L6-v2)
   │  ├─ Download from HuggingFace (if not cached)
   │  └─ Load to memory (~90MB)
   └─ Initialize FAISS index

4. Index Business Documents
   ├─ Fetch all businesses from database
   │  └─ Query: SELECT * FROM usaha_llm
   ├─ Create text representations
   │  └─ Format: "Nama: ... | Alamat: ... | Kategori: ..."
   ├─ Generate embeddings (batch processing)
   │  ├─ Batch size: 32
   │  └─ Progress bar shown
   ├─ Build FAISS index
   │  ├─ Index type: IndexFlatL2
   │  └─ Dimension: 384
   └─ Store in memory

5. Start FastAPI Server
   └─ Listen on 0.0.0.0:5000

✓ Ready to serve requests!
```

**Time Breakdown (10K documents):**

- Model loading: ~5 seconds
- Database fetch: ~2 seconds
- Embedding generation: ~30 seconds
- Index building: ~1 second
- **Total: ~38 seconds**

### 2. Chat Request Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Chat Request Flow                    │
└─────────────────────────────────────────────────────────┘

User: "Cari rumah makan di Balikpapan"
  ↓
┌─────────────────────────────────────────────────────────┐
│ 1. API Endpoint (/api/chat)                             │
├─────────────────────────────────────────────────────────┤
│ - Authenticate user (JWT)                               │
│ - Validate request                                      │
│ - Extract message                                       │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Auto-Sync Check                                      │
├─────────────────────────────────────────────────────────┤
│ - Check if > 60s since last check                      │
│ - If yes:                                               │
│   ├─ Query: SELECT MAX(id) FROM usaha_llm              │
│   ├─ Compare with last_known_max_id                    │
│   └─ If new data: incremental index                    │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Query Classification                                 │
├─────────────────────────────────────────────────────────┤
│ - Detect if counting query                              │
│   Keywords: "berapa", "jumlah", "total", "banyak"       │
│ - Route to appropriate handler                          │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 4. RAG Retrieval                                        │
├─────────────────────────────────────────────────────────┤
│ A. Encode Query                                         │
│    "Cari rumah makan di Balikpapan"                     │
│         ↓                                               │
│    [0.23, -0.45, 0.67, ..., 0.12] (384-dim)            │
│                                                          │
│ B. FAISS Search                                         │
│    - Calculate L2 distance to all vectors               │
│    - Sort by distance                                   │
│    - Return top-5 results                               │
│                                                          │
│ C. Results:                                             │
│    1. Soto Banjar Azizah (score: 0.92)                 │
│    2. Warung Sate Maduratna (score: 0.88)              │
│    3. BALE FOOD (score: 0.85)                          │
│    4. Resto Koe (score: 0.82)                          │
│    5. Depot Terumbu Sultra (score: 0.79)               │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Context Formatting                                   │
├─────────────────────────────────────────────────────────┤
│ Format retrieved docs into readable context:            │
│                                                          │
│ "Berikut adalah data usaha yang relevan:                │
│                                                          │
│ 1. Soto Banjar Azizah Bilqis                           │
│    Nama Komersial: Soto Banjar Azizah Bilqis           │
│    Alamat: Jl. Serindit No.123, RT.02, Gn. Bahagia     │
│    Kategori: Rumah Makan                                │
│    Status: aktif                                        │
│                                                          │
│ 2. Warung Sate Maduratna "Pak Sholeh"                  │
│    Alamat: Jl. Mulawarman No.207, Sepinggan            │
│    Kategori: Restoran Sate                              │
│    Status: aktif                                        │
│ ..."                                                     │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Prompt Construction                                  │
├─────────────────────────────────────────────────────────┤
│ messages = [                                            │
│   {                                                      │
│     "role": "system",                                   │
│     "content": "Anda adalah asisten chatbot..."        │
│   },                                                     │
│   {                                                      │
│     "role": "user",                                     │
│     "content": "Konteks data usaha:\n{context}\n\n     │
│                 Pertanyaan: {query}\n\n                 │
│                 Berikan jawaban informatif..."          │
│   }                                                      │
│ ]                                                        │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 7. LLM Generation (Ollama)                              │
├─────────────────────────────────────────────────────────┤
│ POST http://localhost:11434/api/chat                    │
│                                                          │
│ Llama 3.2 Processing:                                   │
│ 1. Tokenize input                                       │
│ 2. Forward pass through 28 transformer layers           │
│ 3. Generate tokens autoregressively                     │
│ 4. Stop at [EOS] token or max length                    │
│                                                          │
│ Output:                                                  │
│ "Berikut adalah beberapa rumah makan di Balikpapan:     │
│                                                          │
│ 1. **Soto Banjar Azizah Bilqis**                       │
│    - Alamat: Jl. Serindit No.123, RT.02, Gunung        │
│      Bahagia, Balikpapan Selatan                        │
│    - Kategori: Rumah Makan                              │
│    - Status: Aktif                                      │
│                                                          │
│ 2. **Warung Sate Maduratna "Pak Sholeh"**              │
│    - Alamat: Jl. Mulawarman No.207, Sepinggan          │
│    - Kategori: Restoran Sate                            │
│    - Status: Aktif                                      │
│ ..."                                                     │
└─────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────┐
│ 8. Response Packaging                                   │
├─────────────────────────────────────────────────────────┤
│ {                                                        │
│   "response": "Berikut adalah beberapa rumah makan...", │
│   "sources": [                                          │
│     {                                                    │
│       "nama_usaha": "Soto Banjar Azizah Bilqis",       │
│       "alamat": "Jl. Serindit No.123",                 │
│       "relevance_score": 0.92                           │
│     },                                                   │
│     ...                                                  │
│   ],                                                     │
│   "context_used": true,                                 │
│   "user_id": "user123"                                  │
│ }                                                        │
└─────────────────────────────────────────────────────────┘
  ↓
Return to Client

Total Time: ~2-3 seconds
- Auto-sync: 0-50ms (if needed)
- RAG retrieval: 50-100ms
- LLM generation: 1.5-2.5s
- Overhead: 50-100ms
```

### 3. Auto-Sync Flow

```
┌─────────────────────────────────────────────────────────┐
│              Auto-Sync Flow (Every 60s)                 │
└─────────────────────────────────────────────────────────┘

Chat Request Received
  ↓
Check: (now - last_check_time) > 60s?
  ├─ No → Skip sync, proceed to chat
  └─ Yes → Continue sync
      ↓
Query: SELECT MAX(id) FROM usaha_llm
  ↓
max_id = 1523
last_known_max_id = 1520
  ↓
New data detected! (1523 > 1520)
  ↓
Query: SELECT * FROM usaha_llm WHERE id > 1520 ORDER BY id
  ↓
Retrieved 3 new businesses:
- ID 1521: "Cafe Baru"
- ID 1522: "Toko Elektronik"
- ID 1523: "Salon Cantik"
  ↓
Generate embeddings for 3 docs
  ├─ Text 1 → Embedding 1 [0.1, 0.2, ...]
  ├─ Text 2 → Embedding 2 [0.3, 0.4, ...]
  └─ Text 3 → Embedding 3 [0.5, 0.6, ...]
  ↓
FAISS: index.add(new_embeddings)
  ↓
Update tracking:
- documents.extend(new_businesses)
- embeddings = vstack([old, new])
- last_known_max_id = 1523
- last_check_time = now
  ↓
Log: "Auto-synced 3 new documents"
  ↓
Proceed to chat processing

Time: ~50-100ms for 3 docs
```

---

## Optimasi dan Best Practices

### 1. Embedding Optimization

#### Batch Processing

```python
# ❌ BAD: One at a time
for text in texts:
    embedding = model.encode(text)  # Slow!

# ✅ GOOD: Batch processing
embeddings = model.encode(
    texts,
    batch_size=32,  # Process 32 at once
    show_progress_bar=True
)
# ~10x faster!
```

#### GPU Acceleration

```python
# Use GPU if available
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

# Speedup: 10-20x on GPU
```

#### Caching

```python
# Cache embeddings to avoid re-computation
import pickle

# Save
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# Load
with open('embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)
```

### 2. FAISS Optimization

#### Index Selection

```python
# For <10K docs: IndexFlatL2 (exact search)
index = faiss.IndexFlatL2(dimension)

# For 10K-1M docs: IndexIVFFlat (approximate)
quantizer = faiss.IndexFlatL2(dimension)
index = faiss.IndexIVFFlat(quantizer, dimension, nlist=100)
index.train(embeddings)  # Required for IVF

# For >1M docs: IndexHNSW (very fast)
index = faiss.IndexHNSWFlat(dimension, 32)
```

#### GPU Acceleration

```python
# Move index to GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)

# Speedup: 5-10x on GPU
```

### 3. LLM Optimization

#### Prompt Engineering

```python
# ❌ BAD: Vague prompt
"Answer the question based on the data"

# ✅ GOOD: Specific instructions
"""
Berdasarkan data usaha berikut:
{context}

Pertanyaan: {query}

Instruksi:
1. Jawab hanya berdasarkan data yang diberikan
2. Jika tidak ada data relevan, katakan "Tidak ada data"
3. Sertakan alamat lengkap
4. Format: bullet points
"""
```

#### Context Window Management

```python
# Limit context to avoid exceeding token limit
MAX_CONTEXT_TOKENS = 2000

def truncate_context(context, max_tokens):
    tokens = tokenizer.encode(context)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        context = tokenizer.decode(tokens)
    return context
```

#### Streaming Responses

```python
# Stream tokens as they're generated
response = client.chat(
    model=model,
    messages=messages,
    stream=True  # Enable streaming
)

for chunk in response:
    print(chunk['message']['content'], end='')
```

### 4. System-Level Optimization

#### Connection Pooling

```python
# Database connection pool
pool = await asyncpg.create_pool(
    database_url,
    min_size=2,
    max_size=10,
    command_timeout=60
)
```

#### Async Processing

```python
# ✅ GOOD: Async for I/O operations
async def process_query(query):
    # These run concurrently
    results, stats = await asyncio.gather(
        rag_service.search(query),
        db.get_statistics()
    )
```

#### Caching Strategies

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache statistics for 5 minutes
@lru_cache(maxsize=1)
def get_cached_stats():
    return db.get_statistics(), datetime.now()

def get_stats():
    stats, timestamp = get_cached_stats()
    if datetime.now() - timestamp > timedelta(minutes=5):
        get_cached_stats.cache_clear()
        return get_cached_stats()
    return stats
```

### 5. Monitoring and Logging

```python
import logging
import time

logger = logging.getLogger(__name__)

async def search_with_logging(query, top_k):
    start = time.time()

    logger.info(f"Search query: '{query}', top_k={top_k}")

    results = await rag_service.search(query, top_k)

    elapsed = time.time() - start
    logger.info(f"Search completed in {elapsed:.3f}s, found {len(results)} results")

    return results
```

### 6. Error Handling

```python
async def safe_generate_response(message, context):
    try:
        response = await chatbot_service.generate_response(message, context)
        return response
    except ollama.ResponseError as e:
        logger.error(f"Ollama error: {e}")
        return "Maaf, LLM sedang tidak tersedia. Silakan coba lagi."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return "Terjadi kesalahan sistem. Silakan hubungi admin."
```

---

## Performance Metrics

### Latency Breakdown

```
Total Response Time: ~2-3 seconds

├─ Auto-sync check: 0-50ms (if needed)
├─ Query embedding: 20-30ms
├─ FAISS search: 10-20ms (10K docs)
├─ Context formatting: 5-10ms
├─ LLM generation: 1.5-2.5s (depends on response length)
└─ Overhead: 50-100ms
```

### Throughput

```
Concurrent Requests:
- 1 user: ~0.5 QPS (queries per second)
- 10 users: ~3-4 QPS
- 100 users: ~15-20 QPS (with proper scaling)

Bottleneck: LLM generation (CPU-bound)
```

### Resource Usage

```
Memory:
- Embedding model: ~90MB
- FAISS index (10K docs): ~15MB
- LLM (Llama 3.2): ~2GB
- Total: ~2.1GB

CPU:
- Idle: 5-10%
- During embedding: 80-100%
- During LLM generation: 60-80%

Disk:
- Models: ~2.5GB
- Database: varies
```

---

## Kesimpulan

Sistem chatbot Geotags menggunakan arsitektur RAG yang menggabungkan:

1. **Embedding Model (all-MiniLM-L6-v2)**

   - Mengubah teks menjadi vektor 384-dimensi
   - Menangkap makna semantik
   - Memungkinkan similarity search

2. **Vector Database (FAISS)**

   - Menyimpan dan mencari embeddings
   - Efficient similarity search
   - Incremental updates

3. **LLM (Llama 3.2)**
   - Menghasilkan respons natural
   - Grounded pada data faktual
   - Mencegah hallucination

**Keunggulan:**

- ✅ Akurat (grounded on data)
- ✅ Real-time updates
- ✅ Scalable
- ✅ Cost-effective (local deployment)
- ✅ Privacy-preserving (no external API)

**Trade-offs:**

- ⚠️ Latency ~2-3s (vs <1s for API-based)
- ⚠️ Resource intensive (2GB+ RAM)
- ⚠️ Requires GPU for optimal performance

Sistem ini memberikan balance optimal antara akurasi, kecepatan, dan cost untuk use case chatbot informasi usaha.
