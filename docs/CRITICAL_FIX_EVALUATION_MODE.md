# 🚨 CRITICAL FIX: Backend Not in Evaluation Mode

## Problem
48/50 businesses returning "tidak ditemukan" - Backend is loading from **database** (9 businesses) instead of **CSV** (50 businesses).

## Root Cause
Backend **NOT** in evaluation mode. Check:
1. `.env` file not configured
2. Backend not restarted after `.env` change
3. Config not loading properly

## Fix Steps

### Step 1: Configure .env

Add these lines to `.env`:

```bash
# Evaluation Mode
EVALUATION_MODE=true
EVALUATION_CSV_PATH=output_for_eval.csv
```

**CRITICAL:** Make sure there are NO spaces around `=`

### Step 2: Restart Backend

```bash
# Stop current server (Ctrl+C if running)
# Then restart:
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

### Step 3: Verify Logs

Backend startup should show:

```
🧪 EVALUATION MODE: Loading from CSV
Loaded 50 businesses from CSV: output_for_eval.csv
Successfully indexed 50 documents
Tracking initialized with 50 UUIDs
```

**NOT** this:

```
🚀 PRODUCTION MODE: Loading from database
Loaded 9 businesses from database
```

### Step 4: Test

```bash
cd evaluation
python generate_responses.py
```

Should now find businesses!

## Verification Checklist

- [ ] `.env` has `EVALUATION_MODE=true`
- [ ] `.env` has `EVALUATION_CSV_PATH=output_for_eval.csv`
- [ ] Backend restarted
- [ ] Logs show "🧪 EVALUATION MODE"
- [ ] Logs show "Loaded 50 businesses from CSV"
- [ ] Test query finds businesses

## Alternative Issue

If still not working after fix:

1. **Check CSV path:**
   ```python
   # In .env
   EVALUATION_CSV_PATH=output_for_eval.csv  # ✅ Correct (root dir)
   # NOT: evaluation/output_for_eval.csv   # ❌ Wrong
   ```

2. **Check file exists:**
   ```bash
   ls output_for_eval.csv
   ```

3. **Manual test:**
   ```bash
   curl -X POST http://localhost:5000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Jelaskan tentang RKC SEAFOOD"}'
   ```

## Expected Result

After fix, all 50 businesses should be found:

```
[1/50] RKC SEAFOOD
📝 Response: RKC SEAFOOD adalah usaha restoran...
✅ Success

[2/50] Radja Tenda
📝 Response: Radja Tenda adalah usaha...
✅ Success
```

**NOT:**
```
📝 Response: Tidak ditemukan informasi... ❌
```
