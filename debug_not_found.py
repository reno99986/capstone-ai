import json
import pandas as pd

# Load generated responses
print("="*60)
print("DIAGNOSIS: Tidak Ditemukan Issue")
print("="*60)

with open('evaluation/generated_responses_eval.json', encoding='utf-8') as f:
    responses = json.load(f)

# Count tidak ditemukan
not_found_keywords = ['tidak ditemukan', 'tidak tersedia', 'tidak ada', 'maaf']
not_found = []

for r in responses:
    gen = r['generated'].lower()
    if any(keyword in gen for keyword in not_found_keywords):
        not_found.append(r)

print(f"\n📊 Statistics:")
print(f"Total responses: {len(responses)}")
print(f"Not found: {len(not_found)} ({len(not_found)/len(responses)*100:.1f}%)")
print(f"Found: {len(responses) - len(not_found)} ({(len(responses)-len(not_found))/len(responses)*100:.1f}%)")

print(f"\n❌ Not Found Examples:")
for i, r in enumerate(not_found[:10], 1):
    print(f"\n{i}. Query: {r['nama']}")
    print(f"   Response: {r['generated'][:150]}...")

# Check CSV
print(f"\n" + "="*60)
print("CSV Data Check")
print("="*60)

df = pd.read_csv('output_for_eval.csv', delimiter=';')
print(f"Businesses in CSV: {len(df)}")
print(f"\nFirst 5 names:")
for i, name in enumerate(df['nama tempat'].head(5), 1):
    print(f"{i}. {name}")

# Check if backend loaded them
print(f"\n" + "="*60)
print("Recommended Actions")
print("="*60)

if len(not_found) > len(responses) * 0.5:
    print("⚠️  CRITICAL: >50% not found!")
    print("\nLikely causes:")
    print("1. Backend NOT in evaluation mode")
    print("   → Check .env: EVALUATION_MODE=true")
    print("   → Restart: python -m uvicorn app.main:app --reload")
    print("   → Check logs for: '🧪 EVALUATION MODE'")
    print()
    print("2. Name mismatch between CSV and queries")
    print("   → Check exact names match")
    print()
    print("3. RAG relevance too strict")
    print("   → Lower min_relevance in rag_service.py")
elif len(not_found) > 0:
    print(f"⚠️  {len(not_found)} businesses not found")
    print("\nPossible causes:")
    print("1. Name variations (typos, abbreviations)")
    print("2. RAG relevance threshold")
    print("3. Embeddings not matching well")
else:
    print("✅ All businesses found!")
