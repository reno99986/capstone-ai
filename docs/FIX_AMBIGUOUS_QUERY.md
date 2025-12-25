# Fix: Ambiguous Query Handling

## Masalah

**User Query:** "tes"

**Response Buruk:**

```
Terdapat beberapa usaha yang tergabung dalam kategori Bengkel Mobil di Balikpapan:

TGO - Teguh Gemilang Otomotif - GT Radial Tirezone
Alamat: Jl. Mulawarman No.161...

Terdapat juga beberapa usaha lain yang tergabung dalam kategori yang tidak terkait dengan bengkel mobil:

TPS 99 DLH
...
Velia Tekno
...
PAYTREN BISNIS
...
```

**Masalah:**

- ❌ Query "tes" terlalu umum dan tidak jelas
- ❌ LLM mencoba "membantu" dengan listing random data
- ❌ Response panjang dan tidak relevan
- ❌ Membingungkan user

## Root Cause

### 1. **No Query Validation**

```python
# SEBELUM
async def process_query(self, message: str, ...):
    # Langsung process tanpa validasi
    is_counting = self.is_counting_query(message)
    ...
```

**Masalah:**

- Tidak ada validasi untuk query yang terlalu pendek
- Tidak ada deteksi untuk generic test words
- Semua query diproses, meski tidak jelas

### 2. **LLM Tries to Be "Helpful"**

Ketika query tidak jelas, RAG mengembalikan hasil random (karena tidak ada yang match), dan LLM mencoba "membantu" dengan listing semua hasil.

## Solusi

### 1. **Add Query Validation**

```python
def is_valid_query(self, message: str) -> tuple[bool, str]:
    """Validate if query is clear enough to process"""
    message = message.strip()

    # Too short
    if len(message) < 3:
        return False, "Pertanyaan terlalu pendek. Silakan berikan pertanyaan yang lebih jelas."

    # Generic test words
    generic_words = ['tes', 'test', 'coba', 'halo', 'hai', 'hello', 'hi']
    if message.lower() in generic_words:
        return False, "Silakan ajukan pertanyaan spesifik tentang usaha di Balikpapan, misalnya:\n- 'Cari rumah makan di Balikpapan Selatan'\n- 'Berapa jumlah usaha aktif?'\n- 'Jelaskan tentang Soto Banjar Azizah'"

    return True, ""
```

### 2. **Early Return for Invalid Queries**

```python
async def process_query(self, message: str, ...):
    # Validate query first
    is_valid, error_msg = self.is_valid_query(message)
    if not is_valid:
        return {
            "response": error_msg,
            "sources": [],
            "context_used": False,
            "query_type": "invalid"
        }

    # Continue with normal processing...
```

### 3. **Update System Prompt**

```python
ATURAN UNTUK PERTANYAAN TIDAK JELAS:
- Jika pertanyaan terlalu umum atau ambigu (misal: "tes", "coba", "halo"), minta klarifikasi
- JANGAN listing semua data yang ada
- JANGAN mencoba menebak maksud user
- Berikan contoh pertanyaan yang jelas
```

## Test Cases

### Test 1: Generic Word "tes"

**Input:** "tes"

**Expected Output:**

```
Silakan ajukan pertanyaan spesifik tentang usaha di Balikpapan, misalnya:
- 'Cari rumah makan di Balikpapan Selatan'
- 'Berapa jumlah usaha aktif?'
- 'Jelaskan tentang Soto Banjar Azizah'
```

**NOT:**

```
Terdapat beberapa usaha yang tergabung dalam kategori Bengkel Mobil...
```

### Test 2: Too Short

**Input:** "a"

**Expected Output:**

```
Pertanyaan terlalu pendek. Silakan berikan pertanyaan yang lebih jelas.
```

### Test 3: Generic Greeting

**Input:** "halo"

**Expected Output:**

```
Silakan ajukan pertanyaan spesifik tentang usaha di Balikpapan, misalnya:
- 'Cari rumah makan di Balikpapan Selatan'
- 'Berapa jumlah usaha aktif?'
- 'Jelaskan tentang Soto Banjar Azizah'
```

### Test 4: Valid Query (Should Work Normally)

**Input:** "Cari rumah makan"

**Expected Output:**

```
Berikut rumah makan di Balikpapan:
1. Soto Banjar Azizah Bilqis - Jl. Serindit No.123...
2. ...
```

## Generic Words List

Words yang akan di-reject:

- `tes`, `test`
- `coba`
- `halo`, `hai`, `hello`, `hi`

**Note:** Bisa ditambah sesuai kebutuhan.

## Benefits

### 1. **Better UX**

- User langsung tahu query-nya tidak jelas
- Diberikan contoh pertanyaan yang baik
- Tidak dibingungkan dengan data random

### 2. **Better Performance**

- Tidak perlu process query yang tidak jelas
- Hemat compute untuk RAG search
- Hemat token LLM

### 3. **Better Quality**

- Tidak ada response "ngaco"
- Fokus pada query yang jelas
- Lebih profesional

## Monitoring

### Check Invalid Query Rate

```python
# Add counter di chatbot_service.py
self.stats = {
    'total_queries': 0,
    'invalid_queries': 0
}

# Di process_query
self.stats['total_queries'] += 1
if not is_valid:
    self.stats['invalid_queries'] += 1
```

### Expected Metrics

| Metric               | Value |
| -------------------- | ----- |
| Invalid Query Rate   | < 5%  |
| Generic Word Queries | ~2-3% |
| Too Short Queries    | ~1-2% |

## Future Improvements

### 1. **Spell Check**

```python
# Detect typos
if is_likely_typo(message):
    return "Apakah Anda maksud: [suggestion]?"
```

### 2. **Intent Classification**

```python
# Classify intent first
intent = classify_intent(message)
if intent == "greeting":
    return "Halo! Ada yang bisa saya bantu tentang usaha di Balikpapan?"
```

### 3. **Conversation Context**

```python
# Remember previous queries
if is_follow_up(message, conversation_history):
    # Handle differently
```

## Conclusion

Dengan **query validation**, chatbot sekarang akan:

- ✅ Reject query yang terlalu pendek atau generic
- ✅ Memberikan feedback yang jelas
- ✅ Suggest contoh pertanyaan yang baik
- ✅ Tidak "ngaco" dengan listing data random

Server sudah auto-reload. Test dengan "tes" sekarang akan dapat response yang proper! 🚀
