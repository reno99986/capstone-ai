# 🎯 Chatbot Evaluation Guide

Complete guide untuk mengevaluasi performa chatbot menggunakan dataset `output_for_eval.csv`.

---

## 📋 **Quick Start**

### **Prerequisites:**

1. **Backend running in evaluation mode:**

   ```bash
   # Edit .env
   EVALUATION_MODE=true
   EVALUATION_CSV_PATH=output_for_eval.csv

   # Start backend
   python -m uvicorn app.main:app --reload

   # Expected logs:
   # 🧪 EVALUATION MODE: Loading from CSV
   # Loaded 50 businesses from CSV
   ```

2. **Dependencies installed:**
   ```bash
   pip install bert-score pandas requests
   ```

### **Run Evaluation (2 Steps):**

```bash
cd evaluation

# Step 1: Generate responses
python generate_responses.py

# Step 2: Evaluate
python evaluate_chatbot.py
```

**Done!** Results in `evaluation_results.json`

---

## 📊 **What Gets Evaluated**

### **Test Dataset: output_for_eval.csv**

- **50 test cases** dari businesses di Balikpapan
- Setiap row punya:
  - `nama tempat`: Nama business
  - `alamat`: Alamat lengkap
  - `kategori`: Jenis usaha
  - `golden_truth`: Reference answer (generated dari data)

### **Evaluation Metric: BERTScore**

Mengukur semantic similarity antara:

- **Generated**: Response dari chatbot
- **Golden truth**: Reference answer

**Metrics:**

- **Precision**: Seberapa akurat generated response
- **Recall**: Seberapa lengkap generated response
- **F1 Score**: Balance antara precision & recall

---

## 🚀 **Step-by-Step Guide**

### **Step 1: Generate Responses**

```bash
cd evaluation
python generate_responses.py
```

**What it does:**

1. Reads `output_for_eval.csv` (50 businesses)
2. For each business:
   - Query: `"Jelaskan tentang {nama}"`
   - Calls: `POST http://localhost:5000/api/chat`
   - Saves response
3. Outputs: `generated_responses.json`

**Expected output:**

```
📂 Loading test data from output_for_eval.csv
✅ Loaded 50 test cases
📝 Prepared 50 test cases

🤖 Generating responses...
[1/50] RKC SEAFOOD... ✅ (87 chars)
[2/50] Radja Tenda... ✅ (61 chars)
...
[50/50] DrW Skincare... ✅ (81 chars)

✅ Done! Generated 50 responses
```

**Time:** ~2-5 minutes (depends on LLM speed)

### **Step 2: Evaluate**

```bash
python evaluate_chatbot.py
```

**What it does:**

1. Loads `generated_responses.json`
2. Compares with `golden_truth` from CSV
3. Calculates BERTScore (P, R, F1)
4. Saves to `evaluation_results.json`

**Expected output:**

```
============================================================
EVALUATION USING OUTPUT_FOR_EVAL.CSV
============================================================

📂 Loading responses...
✅ Loaded 50 responses

🧮 Evaluating 50 samples...

1️⃣ Calculating BERTScore...
   Precision: 0.8123
   Recall:    0.7845
   F1:        0.7981

============================================================
EVALUATION SUMMARY
============================================================

📊 BERTScore:
   Precision: 0.8123
   Recall:    0.7845
   F1:        0.7981

💡 Interpretation:
   ✅ Good semantic similarity

📄 Results saved to: evaluation_results.json
```

**Time:** ~5-10 minutes

---

## 📈 **Understanding Results**

### **BERTScore Thresholds**

| F1 Score    | Quality    | Action                |
| ----------- | ---------- | --------------------- |
| > 0.85      | Excellent  | ✅ Production ready   |
| 0.75 - 0.85 | Good       | ⚠️ Minor improvements |
| 0.65 - 0.75 | Acceptable | ⚠️ Needs tuning       |
| < 0.65      | Poor       | ❌ Major issues       |

### **Example Results**

**Good Performance (F1 = 0.81):**

```json
{
  "query": "Jelaskan tentang RKC SEAFOOD",
  "golden_truth": "RKC SEAFOOD adalah usaha restoran yang berlokasi di Jl. Sultan Adam...",
  "generated": "RKC SEAFOOD merupakan restoran seafood di Balikpapan...",
  "bertscore": {
    "precision": 0.85,
    "recall": 0.82,
    "f1": 0.83
  }
}
```

**Poor Performance (F1 = 0.52):**

```json
{
  "query": "Jelaskan tentang Toko ABC",
  "golden_truth": "Toko ABC adalah usaha retail yang berlokasi di...",
  "generated": "Maaf, saya tidak menemukan informasi tentang Toko ABC.",
  "bertscore": {
    "f1": 0.52  ← LOW!
  }
}
```

---

## 🔧 **Improving Performance**

### **If Low Precision (<0.75):**

Generated response contains irrelevant information.

**Fix:**

1. Improve system prompt (remove marketing language)
2. Increase RAG relevance threshold
3. Add fact verification

### **If Low Recall (<0.75):**

Generated response missing key information.

**Fix:**

1. Increase RAG `top_k` (retrieve more context)
2. Improve context formatting
3. Update prompt to include all key details

### **If Both Low:**

Major issues with RAG or LLM.

**Fix:**

1. Check RAG is indexing correctly
2. Verify LLM is running
3. Test with manual queries
4. Review system prompt

---

## 📁 **File Structure**

```
capstone-ai2/
├── output_for_eval.csv                    # Test dataset (50 businesses)
├── evaluation/
│   ├── generate_responses.py              # Step 1: Generate
│   ├── evaluate_chatbot.py                # Step 2: Evaluate
│   ├── generated_responses.json           # Output from step 1
│   ├── evaluation_results.json            # Output from step 2 (FINAL)
│   └── EVALUATION_GUIDE.md                # This file
```

---

## 🔄 **Iteration Workflow**

### **1. Baseline Evaluation**

```bash
cd evaluation
python generate_responses.py
python evaluate_chatbot.py
# Note: F1 = 0.75
```

### **2. Make Improvements**

```python
# Example: Improve system prompt
# In app/chatbot_service.py

system_prompt = """
STRICT RULES:
- ONLY use context provided
- NO guessing or assumptions
- Include: nama, kategori, alamat
- Be concise (2-3 sentences)
"""
```

### **3. Re-evaluate**

```bash
# Restart backend (auto-reload)
cd evaluation
python generate_responses.py
python evaluate_chatbot.py
# Check: F1 = 0.82 ← Improved!
```

### **4. Track Progress**

```bash
# Save versions
cp evaluation_results.json results_v1_baseline.json
# After improvements
cp evaluation_results.json results_v2_improved.json
```

---

## 🎯 **Production Targets**

Before deploying to production:

| Metric            | Target      | Minimum |
| ----------------- | ----------- | ------- |
| **BERTScore F1**  | > 0.85      | > 0.75  |
| **Response Time** | < 3s        | < 5s    |
| **Relevance**     | All queries | 90%+    |

---

## 💡 **Tips & Best Practices**

1. **Run evaluation after every change:**

   - Prompt updates
   - RAG settings
   - Model changes

2. **Check individual samples:**

   ```python
   import json
   with open('evaluation_results.json') as f:
       data = json.load(f)

   # Find low-scoring samples
   low = [s for s in data['per_sample'] if s['bertscore']['f1'] < 0.6]
   for sample in low:
       print(sample['query'], sample['bertscore']['f1'])
   ```

3. **Compare versions:**

   ```bash
   # Use git to track
   git add evaluation_results.json
   git commit -m "Eval: F1=0.82 after prompt tuning"
   ```

4. **Update test data:**
   - Add new business types
   - Include edge cases
   - Test different query styles

---

## ⚠️ **Troubleshooting**

### **"Connection refused"**

Backend not running or wrong port.

```bash
# Check
curl http://localhost:5000/api/chat

# Fix
python -m uvicorn app.main:app --reload
```

### **"0 test cases prepared"**

CSV column name mismatch.

```bash
# Check
python -c "import pandas as pd; df=pd.read_csv('output_for_eval.csv',delimiter=';'); print(df.columns)"

# Should include: 'nama tempat', 'golden_truth'
```

### **"bert-score not found"**

```bash
pip install bert-score
```

### **Very low scores across all samples**

- Check LLM is running: `curl http://localhost:11434/api/tags`
- Verify backend in eval mode: Check logs for "🧪 EVALUATION MODE"
- Test one query manually

---

## 📚 **Additional Resources**

- **BERTScore Paper:** https://arxiv.org/abs/1904.09675
- **System Prompt:** `app/chatbot_service.py`
- **RAG Settings:** `app/rag_service.py`
- **Dual-Mode Guide:** `evaluation/eval_guide.md`

---

**Last Updated:** 2025-12-17  
**Version:** 2.0 (Default Method)  
**Dataset:** output_for_eval.csv (50 samples)  
**Metric:** BERTScore F1
