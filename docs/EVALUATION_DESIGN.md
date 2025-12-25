# Rancangan Evaluasi LLM dengan BERTScore dan QuESTEval

## Daftar Isi

1. [Overview](#overview)
2. [Metrik Evaluasi](#metrik-evaluasi)
3. [Arsitektur Sistem Evaluasi](#arsitektur-sistem-evaluasi)
4. [Dataset Preparation](#dataset-preparation)
5. [Implementasi](#implementasi)
6. [Workflow Evaluasi](#workflow-evaluasi)
7. [Interpretasi Hasil](#interpretasi-hasil)

---

## Overview

### Tujuan Evaluasi

Mengukur kualitas response chatbot RAG untuk pertanyaan tentang usaha di Balikpapan menggunakan:

1. **BERTScore**: Mengukur semantic similarity antara response dan reference
2. **QuESTEval**: Mengukur question answering quality (apakah pertanyaan terjawab dengan benar)

### Mengapa Kedua Metrik Ini?

| Metrik        | Mengukur                   | Kelebihan                                                                         | Keterbatasan                                                      |
| ------------- | -------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **BERTScore** | Semantic similarity        | - Tidak perlu exact match<br>- Capture meaning<br>- Robust terhadap paraphrase    | - Tidak cek faktual accuracy<br>- Bisa tinggi meski jawaban salah |
| **QuESTEval** | Question answering quality | - Cek apakah pertanyaan terjawab<br>- Measure relevance<br>- Detect hallucination | - Lebih lambat<br>- Perlu model tambahan                          |

**Kombinasi keduanya** memberikan evaluasi yang komprehensif:

- BERTScore → Kualitas bahasa
- QuESTEval → Kualitas jawaban

---

## Metrik Evaluasi

### 1. BERTScore

#### Apa itu BERTScore?

**BERTScore** menggunakan BERT embeddings untuk mengukur similarity antara generated text dan reference text.

#### Formula

```
BERTScore = F1(Precision, Recall)

Precision = (1/|x|) Σ max cos_sim(x_i, y_j)
Recall    = (1/|y|) Σ max cos_sim(y_j, x_i)
F1        = 2 × (P × R) / (P + R)
```

Dimana:

- `x` = generated tokens
- `y` = reference tokens
- `cos_sim` = cosine similarity antara BERT embeddings

#### Cara Kerja

```
Generated: "Ada 614 usaha di Balikpapan"
Reference: "Terdapat 614 bisnis di kota Balikpapan"

1. Tokenize & Embed:
   Generated tokens → BERT → embeddings
   Reference tokens → BERT → embeddings

2. Match tokens:
   "Ada" ↔ "Terdapat"     → cos_sim = 0.85
   "614" ↔ "614"          → cos_sim = 1.00
   "usaha" ↔ "bisnis"     → cos_sim = 0.92
   "Balikpapan" ↔ "Balikpapan" → cos_sim = 1.00

3. Calculate:
   Precision = avg(max similarities for generated)
   Recall    = avg(max similarities for reference)
   F1        = harmonic mean
```

#### Interpretasi Score

| Score Range | Interpretasi                               |
| ----------- | ------------------------------------------ |
| 0.9 - 1.0   | Excellent - Hampir identik secara semantik |
| 0.8 - 0.9   | Good - Makna sangat mirip                  |
| 0.7 - 0.8   | Fair - Makna cukup mirip                   |
| < 0.7       | Poor - Makna berbeda signifikan            |

### 2. QuESTEval

#### Apa itu QuESTEval?

**QuESTEval** (Question Answering-based Summarization Evaluation) mengukur apakah generated text menjawab pertanyaan dengan benar.

#### Cara Kerja

```
Question: "Berapa usaha di Balikpapan?"
Generated Answer: "Ada 614 usaha di Balikpapan"
Reference Answer: "Terdapat 614 usaha"

1. Question Generation (dari reference):
   - "Berapa jumlah usaha?"
   - "Di mana lokasinya?"

2. Question Answering (pada generated):
   QA Model menjawab questions menggunakan generated text
   - Q: "Berapa jumlah usaha?" → A: "614"
   - Q: "Di mana lokasinya?" → A: "Balikpapan"

3. Compare Answers:
   Compare QA answers dengan reference
   - "614" vs "614" → Match ✓
   - "Balikpapan" vs "Balikpapan" → Match ✓

4. Score:
   QuESTEval = % questions answered correctly
```

#### Interpretasi Score

| Score Range | Interpretasi                            |
| ----------- | --------------------------------------- |
| 0.8 - 1.0   | Excellent - Semua informasi penting ada |
| 0.6 - 0.8   | Good - Sebagian besar informasi ada     |
| 0.4 - 0.6   | Fair - Beberapa informasi hilang        |
| < 0.4       | Poor - Banyak informasi hilang/salah    |

---

## Arsitektur Sistem Evaluasi

```
┌─────────────────────────────────────────────────────────────┐
│                   Evaluation Pipeline                       │
└─────────────────────────────────────────────────────────────┘

1. DATASET PREPARATION
   ┌──────────────────────────────────────────────┐
   │ Test Dataset (JSON)                          │
   │ ┌──────────────────────────────────────────┐ │
   │ │ {                                        │ │
   │ │   "question": "Berapa usaha?",           │ │
   │ │   "reference": "Ada 614 usaha",          │ │
   │ │   "context": [...],                      │ │
   │ │   "metadata": {...}                      │ │
   │ │ }                                        │ │
   │ └──────────────────────────────────────────┘ │
   └──────────────────────────────────────────────┘
                    ↓
2. GENERATE RESPONSES
   ┌──────────────────────────────────────────────┐
   │ For each test case:                          │
   │ - Send question to chatbot                   │
   │ - Get generated response                     │
   │ - Store in results                           │
   └──────────────────────────────────────────────┘
                    ↓
3. EVALUATE WITH BERTSCORE
   ┌──────────────────────────────────────────────┐
   │ BERTScore Evaluation                         │
   │ - Load BERT model                            │
   │ - Calculate P, R, F1 for each pair           │
   │ - Aggregate scores                           │
   └──────────────────────────────────────────────┘
                    ↓
4. EVALUATE WITH QUESTEVAL
   ┌──────────────────────────────────────────────┐
   │ QuESTEval Evaluation                         │
   │ - Generate questions from reference          │
   │ - Answer questions using generated text      │
   │ - Compare answers                            │
   │ - Calculate score                            │
   └──────────────────────────────────────────────┘
                    ↓
5. AGGREGATE & REPORT
   ┌──────────────────────────────────────────────┐
   │ Results Dashboard                            │
   │ - Overall scores                             │
   │ - Per-category breakdown                     │
   │ - Error analysis                             │
   │ - Visualizations                             │
   └──────────────────────────────────────────────┘
```

---

## Dataset Preparation

### 1. Test Dataset Structure

```json
{
  "test_cases": [
    {
      "id": "TC001",
      "category": "counting",
      "question": "Berapa jumlah usaha di Balikpapan?",
      "reference_answer": "Terdapat 614 usaha di Balikpapan, dengan 612 usaha aktif dan 2 usaha tidak aktif.",
      "context": {
        "total": 614,
        "active": 612,
        "inactive": 2
      },
      "expected_info": ["total_count", "active_count", "status_breakdown"]
    },
    {
      "id": "TC002",
      "category": "search",
      "question": "Cari rumah makan di Balikpapan Selatan",
      "reference_answer": "Berikut beberapa rumah makan di Balikpapan Selatan: 1. Soto Banjar Azizah Bilqis di Jl. Serindit No.123, Gunung Bahagia. 2. Warung Sate Maduratna di Jl. Mulawarman No.207, Sepinggan.",
      "context": {
        "businesses": [
          {
            "nama": "Soto Banjar Azizah Bilqis",
            "alamat": "Jl. Serindit No.123",
            "kecamatan": "BALIKPAPAN SELATAN"
          }
        ]
      },
      "expected_info": ["business_names", "addresses", "locations"]
    },
    {
      "id": "TC003",
      "category": "statistics",
      "question": "Kategori usaha apa yang paling banyak?",
      "reference_answer": "Kategori usaha terbanyak adalah Rumah Makan dengan 349 usaha, diikuti oleh Toko dengan 123 usaha.",
      "context": {
        "top_categories": [
          { "category": "Rumah Makan", "count": 349 },
          { "category": "Toko", "count": 123 }
        ]
      },
      "expected_info": ["top_category", "category_count"]
    }
  ]
}
```

### 2. Dataset Categories

Buat test cases untuk berbagai jenis query:

| Category          | Jumlah  | Contoh Query                                       |
| ----------------- | ------- | -------------------------------------------------- |
| **Counting**      | 20      | "Berapa usaha?", "Jumlah rumah makan?"             |
| **Search**        | 30      | "Cari toko di...", "Alamat restoran..."            |
| **Statistics**    | 20      | "Kategori terbanyak?", "Distribusi per kecamatan?" |
| **Specific Info** | 20      | "Jam buka?", "Nomor telepon?"                      |
| **Follow-up**     | 10      | "Yang di Balikpapan Selatan saja"                  |
| **Total**         | **100** |                                                    |

### 3. Reference Answer Creation

**Manual Annotation:**

```python
# Untuk setiap test case, buat reference answer yang:
# 1. Akurat (sesuai data database)
# 2. Lengkap (semua info penting ada)
# 3. Natural (bahasa yang baik)

reference = {
    "answer": "Ada 614 usaha di Balikpapan...",
    "key_facts": [
        {"type": "number", "value": 614, "label": "total"},
        {"type": "number", "value": 612, "label": "active"},
        {"type": "location", "value": "Balikpapan"}
    ]
}
```

---

## Implementasi

### 1. Setup Environment

```bash
# Install dependencies
pip install bert-score questeval transformers torch

# Atau tambahkan ke requirements.txt
echo "bert-score>=0.3.13" >> requirements.txt
echo "questeval>=0.2.4" >> requirements.txt
echo "transformers>=4.30.0" >> requirements.txt
echo "torch>=2.0.0" >> requirements.txt
```

### 2. Evaluation Script Structure

```
evaluation/
├── __init__.py
├── dataset/
│   ├── test_cases.json          # Test dataset
│   └── create_dataset.py        # Script untuk buat dataset
├── metrics/
│   ├── __init__.py
│   ├── bertscore_eval.py        # BERTScore implementation
│   └── questeval_eval.py        # QuESTEval implementation
├── evaluator.py                 # Main evaluation orchestrator
├── generate_responses.py        # Generate responses dari chatbot
├── analyze_results.py           # Analyze & visualize results
└── config.py                    # Configuration
```

### 3. BERTScore Implementation

```python
# evaluation/metrics/bertscore_eval.py

from bert_score import score
import logging

logger = logging.getLogger(__name__)

class BERTScoreEvaluator:
    """Evaluate responses using BERTScore"""

    def __init__(self, model_type="bert-base-multilingual-cased", lang="id"):
        """
        Initialize BERTScore evaluator

        Args:
            model_type: BERT model to use for embeddings
            lang: Language code (id for Indonesian)
        """
        self.model_type = model_type
        self.lang = lang

    def evaluate(self, candidates, references):
        """
        Calculate BERTScore for candidate-reference pairs

        Args:
            candidates: List of generated responses
            references: List of reference answers

        Returns:
            Dictionary with precision, recall, F1 scores
        """
        logger.info(f"Evaluating {len(candidates)} responses with BERTScore")

        # Calculate BERTScore
        P, R, F1 = score(
            candidates,
            references,
            model_type=self.model_type,
            lang=self.lang,
            verbose=True
        )

        results = {
            "precision": P.mean().item(),
            "recall": R.mean().item(),
            "f1": F1.mean().item(),
            "per_sample": [
                {
                    "precision": p.item(),
                    "recall": r.item(),
                    "f1": f.item()
                }
                for p, r, f in zip(P, R, F1)
            ]
        }

        logger.info(f"BERTScore F1: {results['f1']:.4f}")
        return results

    def evaluate_single(self, candidate, reference):
        """Evaluate single candidate-reference pair"""
        P, R, F1 = score(
            [candidate],
            [reference],
            model_type=self.model_type,
            lang=self.lang
        )

        return {
            "precision": P.item(),
            "recall": R.item(),
            "f1": F1.item()
        }
```

### 4. QuESTEval Implementation

```python
# evaluation/metrics/questeval_eval.py

from questeval.questeval_metric import QuestEval
import logging

logger = logging.getLogger(__name__)

class QuESTEvalEvaluator:
    """Evaluate responses using QuESTEval"""

    def __init__(self, language="en", use_cache=True):
        """
        Initialize QuESTEval evaluator

        Args:
            language: Language for evaluation (en/fr/multilingual)
            use_cache: Whether to cache model
        """
        logger.info("Loading QuESTEval model...")
        self.questeval = QuestEval(
            language=language,
            use_cache=use_cache
        )
        logger.info("QuESTEval model loaded")

    def evaluate(self, candidates, references, questions=None):
        """
        Calculate QuESTEval scores

        Args:
            candidates: List of generated responses
            references: List of reference answers
            questions: Optional list of source questions

        Returns:
            Dictionary with QuESTEval scores
        """
        logger.info(f"Evaluating {len(candidates)} responses with QuESTEval")

        scores = []
        for i, (cand, ref) in enumerate(zip(candidates, references)):
            try:
                # Calculate score for this pair
                score = self.questeval.corpus_questeval(
                    hypothesis=[cand],
                    sources=[ref]
                )
                scores.append(score['corpus_score'])

                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(candidates)}")

            except Exception as e:
                logger.error(f"Error evaluating sample {i}: {e}")
                scores.append(0.0)

        results = {
            "mean_score": sum(scores) / len(scores) if scores else 0.0,
            "per_sample": scores
        }

        logger.info(f"QuESTEval Mean Score: {results['mean_score']:.4f}")
        return results

    def evaluate_single(self, candidate, reference, question=None):
        """Evaluate single candidate-reference pair"""
        score = self.questeval.corpus_questeval(
            hypothesis=[candidate],
            sources=[reference]
        )
        return score['corpus_score']
```

### 5. Main Evaluator

```python
# evaluation/evaluator.py

import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from .metrics.bertscore_eval import BERTScoreEvaluator
from .metrics.questeval_eval import QuESTEvalEvaluator

logger = logging.getLogger(__name__)

class ChatbotEvaluator:
    """Main evaluator orchestrating all metrics"""

    def __init__(self, config=None):
        """
        Initialize evaluator with all metrics

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize metrics
        logger.info("Initializing evaluation metrics...")
        self.bertscore = BERTScoreEvaluator(
            model_type=self.config.get('bertscore_model', 'bert-base-multilingual-cased'),
            lang=self.config.get('language', 'id')
        )

        self.questeval = QuESTEvalEvaluator(
            language=self.config.get('questeval_lang', 'en')
        )

        logger.info("All metrics initialized")

    def evaluate_dataset(
        self,
        test_cases: List[Dict[str, Any]],
        generated_responses: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate entire dataset

        Args:
            test_cases: List of test case dictionaries
            generated_responses: List of generated responses

        Returns:
            Comprehensive evaluation results
        """
        logger.info(f"Evaluating {len(test_cases)} test cases")

        # Extract references and questions
        references = [tc['reference_answer'] for tc in test_cases]
        questions = [tc['question'] for tc in test_cases]

        # Evaluate with BERTScore
        logger.info("Running BERTScore evaluation...")
        bertscore_results = self.bertscore.evaluate(
            generated_responses,
            references
        )

        # Evaluate with QuESTEval
        logger.info("Running QuESTEval evaluation...")
        questeval_results = self.questeval.evaluate(
            generated_responses,
            references,
            questions
        )

        # Combine results
        results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "num_samples": len(test_cases),
                "config": self.config
            },
            "overall_scores": {
                "bertscore": {
                    "precision": bertscore_results['precision'],
                    "recall": bertscore_results['recall'],
                    "f1": bertscore_results['f1']
                },
                "questeval": {
                    "mean_score": questeval_results['mean_score']
                }
            },
            "per_sample_results": []
        }

        # Combine per-sample results
        for i, tc in enumerate(test_cases):
            sample_result = {
                "id": tc['id'],
                "category": tc['category'],
                "question": tc['question'],
                "reference": tc['reference_answer'],
                "generated": generated_responses[i],
                "scores": {
                    "bertscore": bertscore_results['per_sample'][i],
                    "questeval": questeval_results['per_sample'][i]
                }
            }
            results['per_sample_results'].append(sample_result)

        # Category-wise analysis
        results['category_scores'] = self._analyze_by_category(
            results['per_sample_results']
        )

        logger.info("Evaluation complete")
        return results

    def _analyze_by_category(self, per_sample_results):
        """Analyze scores by category"""
        categories = {}

        for result in per_sample_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {
                    'bertscore_f1': [],
                    'questeval': []
                }

            categories[cat]['bertscore_f1'].append(
                result['scores']['bertscore']['f1']
            )
            categories[cat]['questeval'].append(
                result['scores']['questeval']
            )

        # Calculate means
        category_scores = {}
        for cat, scores in categories.items():
            category_scores[cat] = {
                'bertscore_f1': sum(scores['bertscore_f1']) / len(scores['bertscore_f1']),
                'questeval': sum(scores['questeval']) / len(scores['questeval']),
                'num_samples': len(scores['bertscore_f1'])
            }

        return category_scores

    def save_results(self, results, output_path):
        """Save evaluation results to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {output_path}")
```

### 6. Response Generation Script

```python
# evaluation/generate_responses.py

import asyncio
import json
import logging
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chatbot_service import chatbot_service
from app.database import db
from app.rag_service import rag_service

logger = logging.getLogger(__name__)

async def generate_responses(test_cases: List[Dict[str, Any]]) -> List[str]:
    """
    Generate responses for all test cases

    Args:
        test_cases: List of test case dictionaries

    Returns:
        List of generated responses
    """
    logger.info(f"Generating responses for {len(test_cases)} test cases")

    # Initialize services
    await db.connect()
    await rag_service.initialize()

    # Index documents
    businesses = await db.get_all_businesses()
    await rag_service.index_documents(businesses)

    responses = []

    for i, tc in enumerate(test_cases):
        try:
            logger.info(f"Processing {i+1}/{len(test_cases)}: {tc['question']}")

            # Generate response
            result = await chatbot_service.process_query(
                message=tc['question'],
                top_k=5,
                db=db
            )

            responses.append(result['response'])

        except Exception as e:
            logger.error(f"Error generating response for TC {tc['id']}: {e}")
            responses.append("")

    await db.disconnect()

    logger.info("Response generation complete")
    return responses

async def main():
    """Main function"""
    # Load test cases
    with open('evaluation/dataset/test_cases.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        test_cases = data['test_cases']

    # Generate responses
    responses = await generate_responses(test_cases)

    # Save responses
    output = {
        "test_cases": test_cases,
        "generated_responses": responses
    }

    with open('evaluation/generated_responses.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info("Responses saved to evaluation/generated_responses.json")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
```

### 7. Main Evaluation Runner

```python
# evaluation/run_evaluation.py

import json
import logging
from evaluator import ChatbotEvaluator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Run complete evaluation pipeline"""

    # Load generated responses
    logger.info("Loading generated responses...")
    with open('evaluation/generated_responses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        test_cases = data['test_cases']
        generated_responses = data['generated_responses']

    # Initialize evaluator
    config = {
        'bertscore_model': 'bert-base-multilingual-cased',
        'language': 'id',
        'questeval_lang': 'en'
    }

    evaluator = ChatbotEvaluator(config=config)

    # Run evaluation
    logger.info("Starting evaluation...")
    results = evaluator.evaluate_dataset(test_cases, generated_responses)

    # Save results
    evaluator.save_results(results, 'evaluation/results.json')

    # Print summary
    print("\n" + "="*60)
    print("EVALUATION RESULTS SUMMARY")
    print("="*60)
    print(f"\nOverall Scores:")
    print(f"  BERTScore F1:     {results['overall_scores']['bertscore']['f1']:.4f}")
    print(f"  BERTScore P:      {results['overall_scores']['bertscore']['precision']:.4f}")
    print(f"  BERTScore R:      {results['overall_scores']['bertscore']['recall']:.4f}")
    print(f"  QuESTEval Score:  {results['overall_scores']['questeval']['mean_score']:.4f}")

    print(f"\nScores by Category:")
    for cat, scores in results['category_scores'].items():
        print(f"  {cat}:")
        print(f"    BERTScore F1:  {scores['bertscore_f1']:.4f}")
        print(f"    QuESTEval:     {scores['questeval']:.4f}")
        print(f"    Samples:       {scores['num_samples']}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()
```

---

## Workflow Evaluasi

### Step-by-Step Process

```bash
# 1. Prepare dataset
cd evaluation/dataset
python create_dataset.py

# 2. Generate responses
cd ..
python generate_responses.py

# 3. Run evaluation
python run_evaluation.py

# 4. Analyze results
python analyze_results.py
```

### Expected Output

```
EVALUATION RESULTS SUMMARY
============================================================

Overall Scores:
  BERTScore F1:     0.8756
  BERTScore P:      0.8821
  BERTScore R:      0.8693
  QuESTEval Score:  0.7234

Scores by Category:
  counting:
    BERTScore F1:  0.9123
    QuESTEval:     0.8456
    Samples:       20

  search:
    BERTScore F1:  0.8567
    QuESTEval:     0.7012
    Samples:       30

  statistics:
    BERTScore F1:  0.8901
    QuESTEval:     0.7589
    Samples:       20

============================================================
```

---

## Interpretasi Hasil

### 1. BERTScore Interpretation

| Scenario             | BERTScore F1 | Interpretasi                  | Action    |
| -------------------- | ------------ | ----------------------------- | --------- |
| High F1 (>0.85)      | 0.90         | Response semantically similar | ✅ Good   |
| Medium F1 (0.7-0.85) | 0.78         | Some semantic differences     | ⚠️ Review |
| Low F1 (<0.7)        | 0.65         | Significant differences       | ❌ Fix    |

**Contoh:**

```
Question: "Berapa usaha di Balikpapan?"
Reference: "Ada 614 usaha di Balikpapan"
Generated: "Terdapat 614 bisnis di kota Balikpapan"
BERTScore F1: 0.92 → Excellent (paraphrase yang baik)

Generated: "Saya tidak tahu pasti"
BERTScore F1: 0.45 → Poor (tidak menjawab)
```

### 2. QuESTEval Interpretation

| Scenario         | QuESTEval | Interpretasi           | Action    |
| ---------------- | --------- | ---------------------- | --------- |
| High (>0.8)      | 0.85      | All key info present   | ✅ Good   |
| Medium (0.6-0.8) | 0.72      | Some info missing      | ⚠️ Review |
| Low (<0.6)       | 0.45      | Key info missing/wrong | ❌ Fix    |

**Contoh:**

```
Question: "Berapa usaha aktif di Balikpapan?"
Reference: "Ada 612 usaha aktif dari total 614 usaha"

Generated: "Ada 612 usaha aktif"
QuESTEval: 0.75 → Good (angka benar, tapi kurang context)

Generated: "Ada banyak usaha aktif"
QuESTEval: 0.30 → Poor (tidak ada angka spesifik)
```

### 3. Combined Analysis

**Ideal Case (High Both):**

```
BERTScore: 0.90, QuESTEval: 0.85
→ Response is semantically similar AND answers correctly
→ ✅ Excellent quality
```

**High BERTScore, Low QuESTEval:**

```
BERTScore: 0.88, QuESTEval: 0.45
→ Response uses similar words but wrong information
→ ❌ Hallucination detected
```

**Low BERTScore, High QuESTEval:**

```
BERTScore: 0.65, QuESTEval: 0.82
→ Response has correct info but different phrasing
→ ⚠️ Consider improving naturalness
```

---

## Recommendations

### 1. Baseline Thresholds

Set minimum acceptable scores:

```python
THRESHOLDS = {
    "bertscore_f1": 0.75,      # Minimum semantic similarity
    "questeval": 0.65,          # Minimum QA quality
    "combined": 0.70            # Average of both
}
```

### 2. Continuous Evaluation

```python
# Add to CI/CD pipeline
def test_chatbot_quality():
    results = run_evaluation()

    assert results['overall_scores']['bertscore']['f1'] >= 0.75
    assert results['overall_scores']['questeval']['mean_score'] >= 0.65

    # Check no category is too low
    for cat, scores in results['category_scores'].items():
        assert scores['bertscore_f1'] >= 0.70
        assert scores['questeval'] >= 0.60
```

### 3. Error Analysis

Identify problematic cases:

```python
# Find low-scoring samples
low_scores = [
    sample for sample in results['per_sample_results']
    if sample['scores']['bertscore']['f1'] < 0.70
    or sample['scores']['questeval'] < 0.60
]

# Analyze patterns
for sample in low_scores:
    print(f"ID: {sample['id']}")
    print(f"Category: {sample['category']}")
    print(f"Question: {sample['question']}")
    print(f"Generated: {sample['generated']}")
    print(f"Scores: BERTScore={sample['scores']['bertscore']['f1']:.2f}, "
          f"QuESTEval={sample['scores']['questeval']:.2f}")
    print()
```

---

## Kesimpulan

Dengan implementasi evaluasi menggunakan **BERTScore** dan **QuESTEval**, Anda akan mendapatkan:

1. ✅ **Objective Metrics** - Tidak perlu manual evaluation
2. ✅ **Comprehensive Coverage** - Semantic similarity + QA quality
3. ✅ **Reproducible** - Consistent evaluation across runs
4. ✅ **Actionable Insights** - Identify specific weaknesses
5. ✅ **Continuous Monitoring** - Track improvements over time

**Next Steps:**

1. Create test dataset (100 cases)
2. Implement evaluation scripts
3. Run baseline evaluation
4. Analyze results
5. Iterate and improve chatbot
6. Re-evaluate and compare
