# 📊 Evaluation Results - Chatbot LLM Performance

**Date:** 2025-12-17  
**Model:** llama3.2 (via Ollama)  
**Embedding:** all-MiniLM-L6-v2  
**Test Cases:** 50 samples  
**Dataset:** ref_true_mistake - added_ref.csv.csv

---

## 🎯 **Overall Performance**

### **BERTScore Metrics**

| Metric        | Score  | Status        |
| ------------- | ------ | ------------- |
| **Precision** | 0.7992 | ⚠️ Good       |
| **Recall**    | 0.7129 | ⚠️ Acceptable |
| **F1 Score**  | 0.7533 | ⚠️ Acceptable |

**Scale:** 0.0 - 1.0 (higher is better)

### **Discrimination Analysis**

| Metric                  | Score   | Status          |
| ----------------------- | ------- | --------------- |
| **F1 with Reference**   | 0.7533  | ⚠️ Acceptable   |
| **F1 with Incorrect**   | 0.7893  | ❌ **HIGHER!**  |
| **Difference**          | -0.0360 | ❌ **NEGATIVE** |
| **Discrimination Rate** | 0.0%    | ❌ **CRITICAL** |

---

## ⚠️ **Critical Finding: Discrimination Failure**

### **Problem Identified:**

The chatbot **prefers INCORRECT descriptions** over correct ones!

```
F1 with Reference (Correct):    0.7533
F1 with Incorrect (Wrong):       0.7893  ← HIGHER!
Difference:                      -0.0360  ← NEGATIVE!
```

**What this means:**

- ❌ Model generates responses MORE similar to **incorrect** descriptions
- ❌ Model generates responses LESS similar to **correct** descriptions
- ❌ **0% discrimination rate** - failed ALL 50 test cases
- ❌ Model cannot distinguish correct from incorrect information

### **Root Causes (Hypothesis):**

1. **RAG Retrieval Issues:**

   - May be retrieving irrelevant documents
   - Top-k results not matching query intent
   - Relevance threshold too low

2. **Prompt Engineering:**

   - System prompt may not emphasize factual accuracy
   - Lacks explicit instructions to avoid misinformation
   - No examples of correct vs incorrect responses

3. **Context Quality:**

   - Retrieved context may be incomplete
   - Missing key business attributes
   - Noisy or contradictory information

4. **LLM Behavior:**
   - Model may be hallucinating
   - Creative responses instead of factual
   - Temperature too high (if applicable)

---

## 📈 **BERTScore Analysis**

### **Semantic Similarity: Acceptable**

**F1 Score: 0.7533**

| Range         | Interpretation    | Your Score    |
| ------------- | ----------------- | ------------- |
| 0.9 - 1.0     | Excellent         |               |
| 0.8 - 0.9     | Good              |               |
| **0.7 - 0.8** | **Acceptable**    | **✅ 0.7533** |
| 0.6 - 0.7     | Needs Improvement |               |
| < 0.6         | Poor              |               |

**Interpretation:**

- ✅ Moderate semantic alignment with reference answers
- ✅ Responses are somewhat relevant
- ⚠️ Room for improvement in accuracy
- ⚠️ May include unnecessary information

### **Precision vs Recall**

```
Precision (0.7992) > Recall (0.7129)
   ↓                    ↓
How much of           How much of
generated is          reference is
in reference          in generated
```

**What this tells us:**

- ✅ Generated content is relatively accurate (precision)
- ⚠️ Missing some key information (recall)
- 💡 Model may be conservative (doesn't include all reference info)

---

## 🔍 **Detailed Analysis**

### **Test Configuration**

```json
{
  "model": "llama3.2",
  "embedding_model": "all-MiniLM-L6-v2",
  "test_samples": 50,
  "evaluation_metrics": [
    "BERTScore (bert-base-multilingual-cased)",
    "Discrimination Analysis"
  ],
  "dataset": "ref_true_mistake - added_ref.csv.csv"
}
```

### **Execution Time**

- **BERTScore:** ~7 seconds (11.34 sentences/sec)
- **Discrimination:** ~12 seconds
- **Total:** ~19 seconds

### **QuESTEval**

- **Status:** ❌ Not installed (skipped)
- **Reason:** Dependency conflicts with spacy
- **Impact:** Minimal (BERTScore is sufficient)

---

## 🚨 **Recommendations**

### **Priority 1: Fix Discrimination Failure** 🔥

#### **1. Improve System Prompt**

Current issue: Model may not prioritize factual accuracy.

**Suggested changes:**

```python
# Add to system_prompt:
"""
CRITICAL RULES FOR ACCURACY:
1. ONLY use information from CONTEXT provided
2. DO NOT add information not in context
3. DO NOT make assumptions or guess
4. If information missing, say "Tidak tersedia dalam data"
5. VERIFY business name, category, and details match context

INCORRECT EXAMPLE (DON'T DO THIS):
User: "Jelaskan tentang Restoran ABC"
Context: "Restoran ABC - Cafe & Coffee Shop"
❌ BAD: "Restoran ABC adalah toko elektronik..."
✅ GOOD: "Restoran ABC adalah cafe dan coffee shop..."
"""
```

#### **2. Improve RAG Retrieval**

```python
# In chatbot_service.py
results = await rag_service.search(
    query,
    top_k=10,           # Increase from 5
    min_relevance=0.4   # Increase threshold from 0.3
)
```

#### **3. Add Fact Verification Step**

```python
# Verify generated response matches retrieved context
def verify_facts(generated, context):
    # Check if key facts in generated exist in context
    # Reject if hallucination detected
    pass
```

### **Priority 2: Improve BERTScore (0.75 → 0.85)**

#### **1. Enhance Context Formatting**

```python
# Make context clearer and more structured
def format_context(results):
    formatted = []
    for biz in results:
        formatted.append(f"""
NAMA: {biz['nama_usaha']}
KATEGORI: {biz['kategori']}
PRODUK: {biz['produk_utama']}
ALAMAT: {biz['alamat']}
STATUS: {biz['status']}
        """)
    return "\n---\n".join(formatted)
```

#### **2. Fine-tune Response Format**

```python
# In system_prompt
"""
RESPONSE FORMAT:
1. Start with business name
2. State category and main product
3. Provide address
4. Keep it concise (2-3 sentences)
5. No marketing language
"""
```

### **Priority 3: Testing & Validation**

#### **1. Create Better Test Cases**

- Ensure `deskripsi_keliru` is subtly wrong (not obviously false)
- Add edge cases
- Test different query types

#### **2. Implement Continuous Monitoring**

```bash
# Run evaluation after each change
cd evaluation
python generate_responses.py
python evaluate_chatbot.py

# Track progress
git add evaluation_results.json
git commit -m "Eval: F1=0.XX, Disc=XX%"
```

---

## 📝 **Next Steps**

### **Immediate Actions (Today):**

1. ✅ ~~Run evaluation~~ (DONE)
2. ⚠️ **Fix system prompt** (add accuracy rules)
3. ⚠️ **Increase RAG relevance threshold**
4. ⚠️ **Re-run evaluation**

### **Short-term (This Week):**

1. Improve context formatting
2. Add fact verification
3. Create better test cases
4. Target: Discrimination > 85%, BERTScore > 0.80

### **Long-term (Next 2 Weeks):**

1. Implement automated testing pipeline
2. Add A/B testing for prompts
3. Monitor production performance
4. Continuous improvement cycle

---

## 📊 **Comparison with Targets**

| Metric         | Target | Current | Gap     | Status          |
| -------------- | ------ | ------- | ------- | --------------- |
| BERTScore F1   | > 0.85 | 0.7533  | -0.0967 | ⚠️ Below target |
| Discrimination | > 90%  | 0%      | -90%    | ❌ **CRITICAL** |
| Response Time  | < 5s   | ~3s     | ✅ OK   | ✅ Pass         |

---

## 🎓 **Lessons Learned**

1. **Discrimination is MORE important than BERTScore**

   - Even with 0.75 F1, 0% discrimination is unacceptable
   - Model must distinguish correct from incorrect

2. **RAG alone is not enough**

   - Need explicit accuracy instructions in prompt
   - Need verification step

3. **Testing is crucial**

   - Revealed critical issue with discrimination
   - Would not have found without evaluation

4. **Metrics matter**
   - BERTScore alone would have hidden the problem
   - Discrimination analysis caught the issue

---

## 📂 **Files Generated**

- ✅ `generated_responses.json` - 50 chatbot responses
- ✅ `evaluation_results.json` - Detailed metrics
- ✅ `eval_result.md` - This report

---

## 🔗 **References**

- **BERTScore Paper:** https://arxiv.org/abs/1904.09675
- **Evaluation Guide:** `evaluation/eval_guide.md`
- **Implementation:** `evaluation/evaluate_chatbot.py`

---

**Generated:** 2025-12-17 10:09:00  
**Status:** ⚠️ NEEDS IMMEDIATE ATTENTION - Discrimination Failure  
**Next Evaluation:** After fixing system prompt and RAG settings
