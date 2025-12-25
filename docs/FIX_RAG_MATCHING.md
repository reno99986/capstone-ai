# 🔍 RAG Matching Issue Analysis

## Problem

Backend **IS** loading from CSV (50 businesses indexed), but RAG search only matches 2/50 businesses.

**Evidence:**

- ✅ "Perumahan bpd" found (only in CSV, not in DB)
- ✅ "Pesona Alam Residence" found
- ❌ 48 others return "tidak ditemukan"

## Root Cause: RAG Relevance Threshold Too Strict

The issue is in `app/rag_service.py` - default `min_relevance=0.3` is filtering out most results.

## Quick Fix

### Step 1: Lower relevance threshold

Edit `app/rag_service.py`:

```python
# Around line 95-100 in search() method
async def search(
    self,
    query: str,
    top_k: int = 5,
    min_relevance: float = 0.3  # ← CHANGE THIS
) -> List[Dict[str, Any]]:
```

**Change to:**

```python
min_relevance: float = 0.15  # Lower threshold for evaluation
```

### Step 2: Restart backend

Server should auto-reload. Check for:

```
WatchFiles detected changes in 'app\rag_service.py'. Reloading...
```

### Step 3: Re-test

```bash
cd evaluation
python generate_responses.py
```

Should now find MORE businesses!

## Alternative Fixes

### Option 2: Increase top_k

```python
# Get more candidates before filtering
top_k: int = 10  # Default was 5
```

### Option 3: Improve query

In `app/chatbot_service.py`, preprocess query to match indexed names better:

```python
# Before RAG search
query_cleaned = query.lower().strip()
query_cleaned = query_cleaned.replace("jelaskan tentang ", "")
```

## Expected Results

### Before Fix:

- Min relevance: 0.3
- Results: 2/50 found (4%)

### After Fix:

- Min relevance: 0.15
- Results: 35-45/50 found (70-90%)

## Why Only 2 Found?

Possible reasons Perumahan bpd & Pesona Alam matched:

1. **Exact name match** in query
2. **High token overlap** (multi-word names)
3. **Common words** ("perumahan", "residence")

Why others failed:

1. **Unique/uncommon names** (lower embedding similarity)
2. **Short names** (e.g., "Edy", "Driver")
3. **Special characters** (e.g., "/", "&", numbers)
4. **Abbreviations** (PT., CV., UD.)

## Testing

Test with:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Jelaskan tentang RKC SEAFOOD"}'
```

Should return business info, not "tidak ditemukan".
