"""
Evaluate chatbot responses using output_for_eval.csv
"""
import json
import pandas as pd
from pathlib import Path
from bert_score import score as bert_score

# Configuration
RESPONSES_FILE = Path(__file__).parent / "generated_responses_eval.json"
OUTPUT_FILE = Path(__file__).parent / "evaluation_results_eval.json"

print("="*60)
print("EVALUATION USING OUTPUT_FOR_EVAL.CSV")
print("="*60)

# Load responses
print(f"\n📂 Loading responses from {RESPONSES_FILE}")
with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
    responses = json.load(f)

print(f"✅ Loaded {len(responses)} responses")

# Prepare data for evaluation
candidates = [r['generated'] for r in responses]
references = [r['golden_truth'] for r in responses]

print(f"\n🧮 Evaluating {len(candidates)} samples...")

# BERTScore
print("\n1️⃣ Calculating BERTScore...")
P, R, F1 = bert_score(
    candidates, 
    references, 
    lang='id',
    model_type='bert-base-multilingual-cased',
    verbose=False
)

# Convert to python floats
precision_scores = P.tolist()
recall_scores = R.tolist()
f1_scores = F1.tolist()

avg_precision = sum(precision_scores) / len(precision_scores)
avg_recall = sum(recall_scores) / len(recall_scores)
avg_f1 = sum(f1_scores) / len(f1_scores)

print(f"   Precision: {avg_precision:.4f}")
print(f"   Recall:    {avg_recall:.4f}")
print(f"   F1:        {avg_f1:.4f}")

# Per-sample results
results = {
    'overall': {
        'total_samples': len(responses),
        'bertscore': {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1': avg_f1
        }
    },
    'per_sample': []
}

for i, resp in enumerate(responses):
    results['per_sample'].append({
        'id': resp['id'],
        'nama': resp['nama'],
        'query': resp['query'],
        'golden_truth': resp['golden_truth'][:200] + '...' if len(resp['golden_truth']) > 200 else resp['golden_truth'],
        'generated': resp['generated'][:200] + '...' if len(resp['generated']) > 200 else resp['generated'],
        'bertscore': {
            'precision': precision_scores[i],
            'recall': recall_scores[i],
            'f1': f1_scores[i]
        },
        'sources_count': resp.get('sources_count', 0)
    })

# Save results
print(f"\n💾 Saving results to {OUTPUT_FILE}")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Summary
print("\n" + "="*60)
print("EVALUATION SUMMARY")
print("="*60)
print(f"\n📊 BERTScore:")
print(f"   Precision: {avg_precision:.4f}")
print(f"   Recall:    {avg_recall:.4f}")
print(f"   F1:        {avg_f1:.4f}")

print(f"\n💡 Interpretation:")
if avg_f1 > 0.85:
    print("   ✅ Excellent semantic similarity")
elif avg_f1 > 0.75:
    print("   ✅ Good semantic similarity")
elif avg_f1 > 0.65:
    print("   ⚠️  Acceptable, room for improvement")
else:
    print("   ❌ Poor semantic similarity, needs work")

print(f"\n📄 Results saved to: {OUTPUT_FILE}")
print("="*60)
