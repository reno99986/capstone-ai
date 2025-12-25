# Troubleshooting: LLM Memberikan Angka Total yang Salah

## Masalah

**User melaporkan:**

- Query: "Ada berapa usaha di Balikpapan?"
- LLM Response: "Ada total 349 usaha di Balikpapan"
- Actual Database: 614 usaha

**Root Cause:**
LLM kemungkinan **salah membaca** angka dari kategori (misal: "Rumah Makan: 349") sebagai total keseluruhan, bukan dari bagian "TOTAL USAHA".

## Solusi yang Diterapkan

### 1. **Debug Logging**

Menambahkan logging untuk track angka sebenarnya dari database:

```python
# Line 142-143 di chatbot_service.py
logger.info(f"Database total: {stats['total']} usaha")
logger.info(f"Active: {stats['by_status'].get('aktif', 0)}, Inactive: {stats['by_status'].get('Tidak Aktif', 0)}")
```

**Cara cek:**

```bash
# Lihat log server
# Cari baris seperti:
INFO:app.chatbot_service:Database total: 614 usaha
INFO:app.chatbot_service:Active: 612, Inactive: 2
```

### 2. **Visual Emphasis pada Context**

Menggunakan **box characters** untuk menekankan angka total:

**Sebelum:**

```
TOTAL:
- Total usaha dalam database: 614
```

**Sesudah:**

```
╔════════════════════════════════════════╗
║  TOTAL USAHA DI BALIKPAPAN: 614 USAHA  ║
╚════════════════════════════════════════╝
```

Dan di akhir context:

```
╔═══════════════════════════════════════════════════════════╗
║ PENTING - BACA INI:                                       ║
║ - TOTAL USAHA DI BALIKPAPAN = 614 USAHA                   ║
║ - Angka di atas adalah TOTAL KESELURUHAN                  ║
║ - Jangan gunakan angka kategori sebagai total!            ║
║ - Jika ditanya "berapa usaha", jawab: 614 usaha           ║
╚═══════════════════════════════════════════════════════════╝
```

### 3. **Enhanced System Prompt**

Menambahkan aturan eksplisit untuk penggunaan angka:

```python
ATURAN PENTING UNTUK ANGKA/STATISTIK:
- Jika ada kotak (╔═══╗) dengan angka TOTAL, GUNAKAN ANGKA ITU!
- JANGAN gunakan angka dari kategori sebagai total keseluruhan
- JANGAN menambah, mengurangi, atau mengubah angka dari data
- Jika ditanya "berapa total usaha", lihat bagian "TOTAL USAHA DI BALIKPAPAN"
- Angka kategori (misal: Rumah Makan: 349) adalah SUBSET dari total, BUKAN total keseluruhan
```

## Cara Testing

### Test 1: Query Total Usaha

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ada berapa usaha di Balikpapan?",
    "top_k": 5
  }'
```

**Expected Response:**

```json
{
  "response": "Ada total 614 usaha di Balikpapan...",
  ...
}
```

**Cek Log:**

```
INFO:app.chatbot_service:Detected counting query, using database statistics
INFO:app.chatbot_service:Database total: 614 usaha
INFO:app.chatbot_service:Active: 612, Inactive: 2
```

### Test 2: Query Kategori Spesifik

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Berapa rumah makan di Balikpapan?",
    "top_k": 5
  }'
```

**Expected Response:**

```json
{
  "response": "Terdapat 349 rumah makan di Balikpapan...",
  ...
}
```

### Test 3: Verifikasi Database Langsung

Jika masih ada masalah, cek database langsung:

```sql
-- Total usaha
SELECT COUNT(*) FROM usaha_llm;

-- Per kategori
SELECT kategori, COUNT(*) as count
FROM usaha_llm
WHERE kategori IS NOT NULL AND kategori != ''
GROUP BY kategori
ORDER BY count DESC
LIMIT 10;

-- Per status
SELECT status, COUNT(*) as count
FROM usaha_llm
GROUP BY status;
```

## Debugging Checklist

Jika LLM masih memberikan angka salah:

### ✅ Step 1: Cek Database

```bash
# Gunakan script check_db_stats.py (perlu install asyncpg dulu)
python check_db_stats.py
```

Atau query manual di PostgreSQL:

```sql
SELECT COUNT(*) FROM usaha_llm;
```

### ✅ Step 2: Cek Log Server

Restart server dan cari log:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

Saat ada query counting, cek:

```
INFO:app.chatbot_service:Database total: XXX usaha
```

### ✅ Step 3: Cek Context yang Dikirim ke LLM

Tambahkan temporary logging:

```python
# Di chatbot_service.py, setelah line 188
logger.info(f"Context sent to LLM:\n{stats_context}")
```

Cek apakah angka total benar di context.

### ✅ Step 4: Test dengan Model Lain

Jika Llama 3.2 masih salah, coba model lain:

```bash
# Install model lain
ollama pull llama3.1
ollama pull mistral

# Update .env
CHATBOT_MODEL=llama3.1
```

### ✅ Step 5: Simplify Context

Jika masih gagal, simplify context (hapus detail kategori):

```python
stats_context = f"""
TOTAL USAHA DI BALIKPAPAN: {stats['total']} USAHA

Jika ditanya berapa total usaha, jawab: {stats['total']} usaha.
"""
```

## Expected Behavior After Fix

### Query: "Ada berapa usaha di Balikpapan?"

**Log:**

```
INFO:app.chatbot_service:Detected counting query, using database statistics
INFO:app.chatbot_service:Database total: 614 usaha
INFO:app.chatbot_service:Active: 612, Inactive: 2
INFO:app.chatbot_service:Generating response for: 'Ada berapa usaha di Balikpapan?'
```

**Context yang dikirim:**

```
╔════════════════════════════════════════╗
║  TOTAL USAHA DI BALIKPAPAN: 614 USAHA  ║
╚════════════════════════════════════════╝

DETAIL STATUS:
- Usaha AKTIF: 612 usaha
- Usaha TIDAK AKTIF: 2 usaha
...
╔═══════════════════════════════════════════════════════════╗
║ PENTING - BACA INI:                                       ║
║ - TOTAL USAHA DI BALIKPAPAN = 614 USAHA                   ║
║ - Jika ditanya "berapa usaha", jawab: 614 usaha           ║
╚═══════════════════════════════════════════════════════════╝
```

**Response:**

```
Ada total 614 usaha di Balikpapan, dengan rincian:
- 612 usaha aktif (99.7%)
- 2 usaha tidak aktif (0.3%)

Kategori usaha terbanyak adalah:
1. Rumah Makan: 349 usaha
2. Toko: 123 usaha
...
```

## Kemungkinan Penyebab Lain

### 1. **Database Tidak Sync**

Jika database benar-benar ada 614 tapi LLM bilang 349:

- Cek apakah RAG index sudah sync
- Restart server untuk re-index

### 2. **Query Filter Salah**

Cek query di `database.py` line 164:

```python
total = await conn.fetchval("SELECT COUNT(*) FROM usaha_llm")
```

Pastikan tidak ada WHERE clause yang membatasi.

### 3. **LLM Hallucination**

Jika semua sudah benar tapi LLM tetap salah:

- Ini adalah hallucination
- Solusi: Lebih tegas di system prompt
- Atau gunakan model yang lebih besar/akurat

## Monitoring

Untuk monitor akurasi response:

```python
# Tambahkan di chatbot_service.py
if is_counting:
    # Extract number from LLM response
    import re
    numbers = re.findall(r'\d+', response)
    if numbers:
        llm_number = int(numbers[0])
        actual_number = stats['total']
        if llm_number != actual_number:
            logger.warning(f"LLM number mismatch! LLM: {llm_number}, Actual: {actual_number}")
```

## Kesimpulan

Dengan 3 perbaikan di atas:

1. ✅ Debug logging untuk tracking
2. ✅ Visual emphasis dengan box characters
3. ✅ Enhanced system prompt dengan aturan eksplisit

LLM seharusnya sekarang memberikan angka yang **benar dan konsisten** dengan database.

Jika masih ada masalah, cek log dan ikuti debugging checklist di atas.
