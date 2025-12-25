# 📊 Evaluation

Evaluation system untuk mengukur performa chatbot.

## 🚀 Quick Start

```bash
cd evaluation

# 1. Generate responses
python generate_responses.py

# 2. Evaluate
python evaluate_chatbot.py
```

**Results:** `evaluation_results.json`

## 📋 Prerequisites

1. **Backend in evaluation mode:**

   ```bash
   # .env
   EVALUATION_MODE=true
   EVALUATION_CSV_PATH=output_for_eval.csv

   # Start
   python -m uvicorn app.main:app --reload
   ```

2. **Dependencies:**
   ```bash
   pip install bert-score pandas requests
   ```

## 📊 Metrics

- **BERTScore F1:** Semantic similarity (0-1)
  - Target: > 0.85
  - Minimum: > 0.75

## 📁 Files

- `generate_responses.py` - Generate chatbot responses
- `evaluate_chatbot.py` - Calculate BERTScore
- `generated_responses.json` - Generated responses
- `evaluation_results.json` - Final results
- `EVALUATION_GUIDE.md` - Complete documentation

## 🎯 Targets

| Metric        | Target | Minimum |
| ------------- | ------ | ------- |
| F1 Score      | > 0.85 | > 0.75  |
| Response Time | < 3s   | < 5s    |

**For complete guide:** See `EVALUATION_GUIDE.md`
