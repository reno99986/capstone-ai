# Hybrid Query System - Counting & Statistics

## 🎯 Problem Solved

**Before**: 
```
User: "Berapa jumlah usaha di Balikpapan?"
top_k: 5
Actual: 100 usaha

❌ LLM hanya lihat 5 usaha → "Ada 5 usaha" (SALAH!)
```

**After**:
```
User: "Berapa jumlah usaha di Balikpapan?"

✅ System detects counting query
✅ Gets ALL businesses from database
✅ Provides accurate statistics to LLM
✅ LLM answers: "Ada 100 usaha" (BENAR!)
```

## 🔍 How It Works

### 1. Intent Detection

System automatically detects counting queries using keywords:

```python
Keywords: ["berapa", "jumlah", "total", "banyak", "ada berapa", 
           "hitung", "count", "statistik", "data"]
```

### 2. Query Types

#### **Counting Query** (Hybrid Approach)
Triggered by keywords like "berapa", "jumlah", "total"

**Process:**
1. Detect counting intent
2. Get ALL businesses from database (not limited by top_k)
3. Calculate accurate statistics
4. Get relevant examples via RAG (limited to 5)
5. Combine stats + examples as context
6. LLM generates response with accurate numbers

**Example:**
```json
{
  "message": "Berapa jumlah usaha aktif di Balikpapan?",
  "top_k": 5
}
```

**Context sent to LLM:**
```
STATISTIK DATABASE (AKURAT):
- Total usaha dalam database: 9
- Usaha aktif: 8
- Usaha tidak aktif: 1

CONTOH USAHA YANG RELEVAN:
1. SEMBAKO MUKHLAS
   Kategori: SEMBAKO
   Status: aktif
...

PENTING: Gunakan angka statistik di atas untuk menjawab.
```

#### **Search Query** (RAG Only)
Regular queries without counting keywords

**Process:**
1. Embed query
2. FAISS search for top_k most relevant
3. Format as context
4. LLM generates response

**Example:**
```json
{
  "message": "Cari warung kopi di Balikpapan Kota",
  "top_k": 5
}
```

## 📊 Examples

### Counting Queries ✅

```bash
# Total count
"Berapa jumlah usaha di database?"
→ Gets ALL businesses, returns accurate total

# Filtered count
"Berapa banyak usaha aktif?"
→ Counts all active businesses

# Category count
"Ada berapa SPBU?"
→ Searches for SPBU, provides count

# Location count
"Jumlah usaha di Balikpapan Utara?"
→ Counts businesses in that district
```

### Search Queries ✅

```bash
# Specific search
"Cari warung kopi"
→ RAG finds top 5 coffee shops

# Location search
"Usaha di Sepinggan"
→ RAG finds businesses in Sepinggan

# Category search
"Toko sembako terdekat"
→ RAG finds grocery stores
```

## 🔧 Configuration

### Adjust Counting Keywords

Edit `app/chatbot_service.py`:

```python
def is_counting_query(self, message: str) -> bool:
    counting_keywords = [
        "berapa", "jumlah", "total", "banyak",
        # Add more keywords here
        "statistik", "laporan", "ringkasan"
    ]
    return any(keyword in message.lower() for keyword in counting_keywords)
```

### Adjust Example Count

For counting queries, you can change how many examples are shown:

```python
# In process_query method
results = await rag_service.search(message, top_k=min(top_k, 5))
#                                                        ↑
#                                          Change this number
```

## 📈 Response Format

### Counting Query Response

```json
{
  "response": "Total ada 9 usaha dalam database. Dari jumlah tersebut, 8 usaha aktif dan 1 tidak aktif.",
  "sources": [
    // Top 5 businesses as examples
  ],
  "context_used": true,
  "query_type": "counting"  // ← Indicates hybrid approach used
}
```

### Search Query Response

```json
{
  "response": "Berikut warung kopi di Balikpapan:\n1. Warung KPK...",
  "sources": [
    // Top K most relevant businesses
  ],
  "context_used": true,
  "query_type": "search"  // ← Indicates RAG-only approach
}
```

## 💡 Best Practices

### For Counting Questions

```json
// ✅ Good - Will use hybrid approach
{
  "message": "Berapa jumlah usaha?",
  "top_k": 5  // Doesn't matter for counting, all data is used
}

// ✅ Good - Specific count
{
  "message": "Ada berapa SPBU di Balikpapan?",
  "top_k": 3
}
```

### For Search Questions

```json
// ✅ Good - Will use RAG
{
  "message": "Cari warung kopi",
  "top_k": 5  // Returns 5 most relevant
}

// ✅ Good - More results
{
  "message": "Usaha apa saja di Balikpapan Utara?",
  "top_k": 10  // Returns 10 most relevant
}
```

## 🧪 Testing

### Test Counting Query

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Berapa total usaha dalam database?",
    "top_k": 5
  }'
```

**Expected**: Accurate count of ALL businesses

### Test Search Query

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cari warung kopi",
    "top_k": 5
  }'
```

**Expected**: Top 5 most relevant coffee shops

## 🔍 Debugging

Check logs to see which approach is used:

```
# Counting query detected
2025-12-11 07:00:00 - app.chatbot_service - INFO - Detected counting query, using hybrid approach

# Regular search
2025-12-11 07:00:00 - app.chatbot_service - INFO - Generating response for: 'Cari warung kopi'
```

## ⚠️ Limitations

1. **Keyword-based detection**: May miss counting queries without keywords
2. **Database load**: Counting queries fetch ALL data (slower for large datasets)
3. **Language**: Currently optimized for Indonesian keywords

## 🚀 Future Improvements

1. **ML-based intent classification** instead of keywords
2. **Caching** for statistics to avoid repeated database queries
3. **Aggregation queries** for complex statistics
4. **Multi-language support** for English counting queries
