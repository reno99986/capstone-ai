"""
Diagnose RAG matching issue - why only 2/50 found
"""
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

# Load CSV
df = pd.read_csv('output_for_eval.csv', delimiter=';')
print(f"📊 CSV has {len(df)} businesses")
print(f"\n✅ Found by RAG:")
print("- Perumahan bpd")
print("- Pesona Alam Residence")

print(f"\n❌ Not found: {len(df) - 2} businesses")
print(f"\nFirst 10 names from CSV:")
for i, name in enumerate(df['nama tempat'].head(10), 1):
    print(f"{i}. {name}")

# Load embedding model (same as backend)
print(f"\n🔬 Testing embeddings...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test query vs name similarity
test_cases = [
    ("RKC SEAFOOD / RUMAH KEPITING CUMI BPD", "Jelaskan tentang RKC SEAFOOD / RUMAH KEPITING CUMI BPD"),
    ("Perumahan bpd", "Jelaskan tentang Perumahan bpd"),
    ("Radja Tenda", "Jelaskan tentang Radja Tenda"),
]

print(f"\n📏 Query-to-Name Similarities:")
for name, query in test_cases:
    # Embed both
    name_emb = model.encode([name])[0]
    query_emb = model.encode([query])[0]
    
    # Cosine similarity
    similarity = np.dot(name_emb, query_emb) / (np.linalg.norm(name_emb) * np.linalg.norm(query_emb))
    
    print(f"\nName: {name}")
    print(f"Query: {query}")
    print(f"Similarity: {similarity:.4f}")
    
    if similarity < 0.3:
        print("  ⚠️  Below default threshold (0.3)")
    elif similarity < 0.5:
        print("  ⚠️  Low similarity")
    else:
        print("  ✅ Good similarity")

# Check what backend indexed
print(f"\n💡 Recommendations:")
print("1. Lower min_relevance threshold in RAG search")
print("2. Check if CSV data format matches expectations")
print("3. Verify name matching (exact vs fuzzy)")
