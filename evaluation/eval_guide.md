# 📊 Evaluation Guide - Chatbot LLM Testing

Complete guide untuk menjalankan evaluation chatbot dengan dual-mode system.

## 🎯 **Overview**

System mendukung **2 mode operasi**:

| Mode           | Data Source | Use Case              |
| -------------- | ----------- | --------------------- |
| **Production** | Database    | Production deployment |
| **Evaluation** | CSV File    | Testing & evaluation  |

## 🔧 **Setup: Dual-Mode Configuration**

### **1. Environment Variables**

Edit `.env`:

```bash
# PRODUCTION MODE (default)
EVALUATION_MODE=false

# EVALUATION MODE (for testing)
EVALUATION_MODE=true
EVALUATION_CSV_PATH=output.csv
```

### **2. CSV File**

Ensure `output.csv` exists in project root with format:

```csv
id;nama;url;alamat;telepon;latitude;longitude;kategori;...
1;Soto Banjar Azizah;...;Jl. Serindit No.123;...;-1.123;116.456;Restoran;...
```

**Required columns:**

- `nama` → Business name
- `alamat` → Address
- `kategori` → Category
- `produk_utama` → Main product
- `latitude`, `longitude` → Coordinates

## 🚀 **Evaluation Workflow**

### **Step 1: Enable Evaluation Mode**

```bash
# Edit .env
EVALUATION_MODE=true
EVALUATION_CSV_PATH=output.csv
```

### **Step 2: Start Backend**

```bash
cd c:\laragon\www\capstone-ai2
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

**Expected logs:**

```
🧪 EVALUATION MODE: Loading from CSV
Loaded 1000 businesses from CSV: output.csv
Successfully indexed 1000 documents
Tracking initialized with 1000 UUIDs
Service started successfully!
```

### **Step 3: Generate Responses**

```bash
cd evaluation
python generate_responses.py
```

**What it does:**

1. Reads `ref_true_mistake - added_ref.csv.csv` (50 test cases)
2. For each test case:
   - Query: `"Jelaskan tentang {nama_tempat}"`
   - Calls: `POST /api/chat`
   - Saves response
3. Outputs: `generated_responses.json`

**Example test case:**

```csv
nama_tempat,kategori,deskripsi_referensi,deskripsi_keliru
RKC SEAFOOD,Restoran,RKC SEAFOOD adalah restoran...,RKC SEAFOOD adalah toko...
```

### **Step 4: Run Evaluation**

```bash
python evaluate_chatbot.py
```

**What it does:**

1. Loads `generated_responses.json`
2. Loads reference answers from CSV
3. Computes metrics:
   - **BERTScore F1**: Semantic similarity (0-1)
   - **Discrimination Rate**: Correct vs incorrect distinction (%)
4. Outputs: `evaluation_results.json`

**Example results:**

```json
{
  "overall": {
    "bertscore_precision": 0.87,
    "bertscore_recall": 0.85,
    "bertscore_f1": 0.86,
    "discrimination_rate": 94.0,
    "total_samples": 50
  },
  "per_sample": [
    {
      "query": "Jelaskan tentang RKC SEAFOOD",
      "generated": "RKC SEAFOOD adalah restoran seafood...",
      "reference": "RKC SEAFOOD adalah restoran...",
      "bertscore_f1": 0.89,
      "discrimination": {
        "correct_score": 0.85,
        "incorrect_score": 0.22,
        "margin": 0.63
      }
    }
  ]
}
```

### **Step 5: Analyze Results**

```bash
# View summary
cat evaluation_results.json | grep "overall" -A 10

# Or open in editor
code evaluation_results.json
```

**Key metrics:**

- **BERTScore F1 > 0.8**: Good semantic alignment
- **Discrimination > 90%**: Excellent correct/incorrect distinction
- **Low margin (<0.2)**: May need prompt engineering

### **Step 6: Switch Back to Production**

```bash
# Edit .env
EVALUATION_MODE=false

# Restart server (auto-reload)
# Logs: 🚀 PRODUCTION MODE: Loading from database
```

## 📊 **Metrics Explained**

### **1. BERTScore**

Measures semantic similarity using BERT embeddings.

```python
BERTScore = Similarity(Generated, Reference)
```

- **Precision**: How much of generated is in reference
- **Recall**: How much of reference is in generated
- **F1**: Harmonic mean (balanced metric)

**Scale:** 0.0 - 1.0 (higher is better)

**Thresholds:**

- `> 0.9`: Excellent
- `0.8 - 0.9`: Good
- `0.7 - 0.8`: Acceptable
- `< 0.7`: Needs improvement

### **2. Discrimination Analysis**

Tests model's ability to distinguish correct from incorrect descriptions.

```python
correct_score = Similarity(Generated, deskripsi_referensi)
incorrect_score = Similarity(Generated, deskripsi_keliru)

margin = correct_score - incorrect_score
discrimination = (margin > 0) ? "Correct" : "Failed"
```

**Discrimination Rate:** % of samples where model prefers correct description

**Thresholds:**

- `> 95%`: Excellent
- `90-95%`: Good
- `80-90%`: Acceptable
- `< 80%`: Needs tuning

## 🔄 **Iteration & Debugging**

### **If Low BERTScore:**

1. **Check prompt engineering:**

   ```python
   # In app/chatbot_service.py
   system_prompt = "..."  # Tune this
   ```

2. **Check RAG results:**

   ```python
   # Increase top_k or adjust min_relevance
   results = rag_service.search(query, top_k=10, min_relevance=0.25)
   ```

3. **Check reference quality:**
   - Are references well-written?
   - Consistent format?

### **If Low Discrimination:**

1. **Improve incorrect descriptions:**

   - Make them more subtly wrong
   - Not obviously false

2. **Tune LLM temperature:**

   ```python
   # Lower temperature for more factual responses
   ollama.generate(model="llama3.2", temperature=0.1)
   ```

3. **Add negative examples to prompt:**
   ```
   DON'T DO THIS:
   - "RKC SEAFOOD adalah toko elektronik" (wrong category)
   ```

## 📁 **File Structure**

```
capstone-ai2/
├── .env                           # Config (EVALUATION_MODE)
├── output.csv                     # Data for evaluation mode
├── evaluation/
│   ├── ref_true_mistake - added_ref.csv.csv  # Test cases
│   ├── generate_responses.py      # Step 1: Generate responses
│   ├── evaluate_chatbot.py        # Step 2: Evaluate
│   ├── generated_responses.json   # Output of step 1
│   ├── evaluation_results.json    # Output of step 2
│   ├── README.md                  # Quick reference
│   └── eval_guide.md              # This file
└── app/
    ├── config.py                  # evaluation_mode settings
    ├── database.py                # CSV loader
    └── main.py                    # Dual-mode startup
```

## 🎯 **Quick Reference**

### **Start Evaluation:**

```bash
# 1. Enable evaluation mode
echo "EVALUATION_MODE=true" >> .env

# 2. Start backend
python -m uvicorn app.main:app --reload

# 3. Generate & evaluate
cd evaluation
python generate_responses.py
python evaluate_chatbot.py
```

### **Back to Production:**

```bash
# 1. Disable evaluation mode
echo "EVALUATION_MODE=false" >> .env

# 2. Restart (auto-reload)
```

## ⚠️ **Important Notes**

1. **Database Connection:**

   - Still required even in evaluation mode
   - Used for authentication & stats

2. **Auto-Sync:**

   - Disabled in evaluation mode
   - CSV data is static

3. **Performance:**

   - 1000 businesses: ~30s indexing
   - 50 test queries: ~2-5 minutes
   - Evaluation: ~5-10 minutes

4. **Data Consistency:**
   - CSV format matches `usaha_llm` view
   - Same API behavior both modes

## 🐛 **Troubleshooting**

### **"CSV not found"**

```bash
# Check path
ls output.csv

# Update .env
EVALUATION_CSV_PATH=evaluation/output.csv
```

### **"No matching businesses"**

```bash
# Check test cases match CSV data
# nama_tempat in CSV must match businesses in output.csv
```

### **"Low scores across all samples"**

```bash
# Check LLM is running
curl http://localhost:11434/api/tags

# Check prompt
cat app/chatbot_service.py | grep "system_prompt" -A 50
```

## 📈 **Best Practices**

1. **Use production-like data:**

   - Real business names
   - Realistic descriptions
   - Actual addresses

2. **Diverse test cases:**

   - Different categories
   - Various query types
   - Edge cases

3. **Consistent references:**

   - Same style
   - Same detail level
   - Factual accuracy

4. **Regular evaluation:**

   - After prompt changes
   - After model updates
   - Before deployment

5. **Version control results:**
   ```bash
   git add evaluation_results_v1.json
   git commit -m "Evaluation results after prompt tuning"
   ```

## 🎓 **Metrics Targets**

For production deployment:

| Metric           | Target        | Minimum          |
| ---------------- | ------------- | ---------------- |
| BERTScore F1     | > 0.85        | > 0.75           |
| Discrimination   | > 93%         | > 85%            |
| Response Time    | < 5s          | < 10s            |
| No relevant data | Clear message | No hallucination |

---

**Last Updated:** 2025-12-17  
**Version:** 1.0  
**Mode:** Dual-Mode (Production + Evaluation)
