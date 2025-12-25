# Fix: Error "column id does not exist" & "cannot access local variable rag_service"

## ❌ **Errors Fixed:**

### **Error 1: `column "id" does not exist`**

```
ERROR - Error fetching max business ID: column "id" does not exist
ERROR - Error in auto-sync: column "id" does not exist
```

**Root Cause:**

- View `usaha_llm` menggunakan `usaha_id` (UUID), bukan `id` (integer)
- Auto-sync code mencari kolom `id` yang tidak ada

**Fix:**

```python
# BEFORE (❌ Error)
max_id = await conn.fetchval("SELECT MAX(id) FROM usaha_llm")

# AFTER (✅ Fixed)
# Use COUNT instead since usaha_id is UUID (not sequential)
result = await conn.fetchval("SELECT COUNT(*) FROM usaha_llm")
```

**Note:** Auto-sync sekarang **disabled** untuk UUID-based table. Untuk enable kembali, perlu implement timestamp-based tracking dengan `updated_at`.

### **Error 2: `cannot access local variable 'rag_service'`**

```
ERROR - Error processing query: cannot access local variable 'rag_service' where it is not associated with a value
```

**Root Cause:**

- Import `rag_service` di dalam conditional block
- Jika error terjadi sebelum block tersebut, variable tidak terdefinisi

**Fix:**

```python
# BEFORE (❌ Error)
async def process_query(...):
    try:
        # ... validation ...

        if is_filtering:
            from app.rag_service import rag_service  # ← Import di sini
            context = rag_service.format_context(...)

# AFTER (✅ Fixed)
async def process_query(...):
    try:
        # Import at the top to avoid scope issues
        from app.rag_service import rag_service  # ← Import di awal

        # ... validation ...

        if is_filtering:
            context = rag_service.format_context(...)
```

## ✅ **Changes Made:**

### **1. `app/database.py`**

**`get_max_business_id()`:**

- Changed from `SELECT MAX(id)` to `SELECT COUNT(*)`
- Returns count instead of max ID
- Handles UUID-based table properly

**`get_businesses_after_id()`:**

- Disabled auto-sync for UUID table
- Returns empty list
- Logs info message

### **2. `app/chatbot_service.py`**

**`process_query()`:**

- Moved `rag_service` import to top of function
- Prevents variable scope issues
- Ensures import happens before any conditional blocks

## 🔄 **Auto-Sync Status:**

**Current:** ❌ **Disabled** for `usaha_llm` (UUID-based)

**Why?**

- `usaha_id` is UUID, not sequential integer
- Can't use `WHERE id > last_id` logic
- Need different approach

**To Re-enable:**
Implement timestamp-based tracking:

```python
async def get_businesses_after_timestamp(
    self,
    last_updated: datetime,
    limit: int = 1000
) -> List[Dict]:
    query = """
        SELECT * FROM usaha_llm
        WHERE updated_at > $1
        ORDER BY updated_at
        LIMIT $2
    """
    rows = await conn.fetch(query, last_updated, limit)
    return [dict(row) for row in rows]
```

## 🎯 **Impact:**

**Before:**

- ❌ Auto-sync error on every request
- ❌ `rag_service` scope error on filtering queries
- ❌ Logs filled with errors

**After:**

- ✅ No more "column id does not exist" errors
- ✅ No more `rag_service` scope errors
- ✅ Clean logs
- ⚠️ Auto-sync disabled (manual re-index needed if data changes)

## 📝 **Manual Re-index:**

If data changes, restart server to re-index:

```bash
# Server will auto-index on startup
python -m uvicorn app.main:app --reload
```

Or implement timestamp-based auto-sync (recommended for production).
