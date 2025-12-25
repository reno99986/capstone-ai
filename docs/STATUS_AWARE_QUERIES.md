# Status-Aware Query Handling

## 🎯 Problem Fixed

**Before:**
```
User: "Bagaimana dengan usaha yang tidak aktif?"
AI: "Pertanyaan tentang usaha yang tidak aktif tidak tersedia dalam data..."
```

**After:**
```
User: "Bagaimana dengan usaha yang tidak aktif?"
AI: "Ada 1 usaha tidak aktif:
     BENING WATER TECHNOLOGIES
     Status: Tidak Aktif
     ..."
```

## 🔧 How It Works

### Status Detection Keywords

**Inactive Keywords:**
- "tidak aktif"
- "nonaktif"  
- "inactive"
- "tutup"

**Active Keywords:**
- "aktif"
- "active"
- "buka"
- "beroperasi"

### Query Routing

```python
if "tidak aktif" in query:
    # Show only inactive businesses
    examples = filter(status != 'aktif')
    
elif "aktif" in query:
    # Show only active businesses
    examples = filter(status == 'aktif')
    
else:
    # Use RAG for general queries
    examples = rag_search(query)
```

## 📊 Examples

### Query 1: Inactive Businesses
```json
{
  "message": "Bagaimana dengan usaha yang tidak aktif?",
  "top_k": 5
}
```

**Response:**
```
STATISTIK DATABASE:
- Total: 9 usaha
- Aktif: 8 usaha
- Tidak aktif: 1 usaha

CONTOH USAHA:
1. BENING WATER TECHNOLOGIES
   Status: Tidak Aktif
   Kategori: PERALATAN AIR
   ...
```

### Query 2: Active Businesses
```json
{
  "message": "Berapa usaha yang masih aktif?",
  "top_k": 5
}
```

**Response:**
```
STATISTIK DATABASE:
- Total: 9 usaha
- Aktif: 8 usaha
- Tidak aktif: 1 usaha

CONTOH USAHA:
1. SEMBAKO MUKHLAS
   Status: aktif
2. BAKSO OPPA
   Status: aktif
...
```

### Query 3: General (No Status Filter)
```json
{
  "message": "Berapa total usaha?",
  "top_k": 5
}
```

**Response:**
Uses RAG to find most relevant examples (mixed status)

## ✅ Benefits

1. **Accurate Examples** - Shows businesses matching the query intent
2. **Better Context** - LLM sees relevant data for better responses
3. **No Hallucination** - Real data from database, not assumptions
4. **Smart Filtering** - Automatic based on keywords

## 🧪 Testing

Test with these queries:

```bash
# Inactive businesses
"Bagaimana dengan usaha yang tidak aktif?"
"Ada berapa usaha yang tutup?"
"Usaha nonaktif apa saja?"

# Active businesses  
"Berapa usaha yang masih aktif?"
"Usaha yang buka apa saja?"
"Berapa yang masih beroperasi?"

# General
"Berapa total usaha?"
"Ada apa saja di Balikpapan?"
```

All should now show appropriate examples!
