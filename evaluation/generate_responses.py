"""
Generate responses for evaluation using output_for_eval.csv
"""
import pandas as pd
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / '.env')

# Configuration
API_URL = "http://localhost:5000/api/chat"
CSV_FILE = PROJECT_ROOT / "output_for_eval.csv"
OUTPUT_FILE = Path(__file__).parent / "generated_responses_eval.json"

# Load test data
print(f"📂 Loading test data from {CSV_FILE}")
df = pd.read_csv(CSV_FILE, delimiter=';')
print(f"✅ Loaded {len(df)} test cases")

# Prepare test cases
test_cases = []
for idx, row in df.iterrows():
    # Use correct column names from CSV
    nama = row.get('nama tempat', row.get('nama', 'N/A'))
    golden_truth = row.get('golden_truth', '')
    
    # Skip if nama is empty or N/A
    if pd.notna(nama) and str(nama).strip() and str(nama) != 'N/A':
        test_cases.append({
            'id': idx + 1,
            'nama': nama,
            'query': f"Jelaskan tentang {nama}",
            'golden_truth': golden_truth
        })

print(f"📝 Prepared {len(test_cases)} test cases")

# Generate responses
print(f"\n🤖 Generating responses...")
print("="*80)
responses = []

for i, test in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] {test['nama']}")
    print("-"*80)
    
    try:
        # Call chatbot API
        response = requests.post(
            API_URL,
            json={"message": test['query']},
            headers={
                "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdXRob3JpemVkIjp0cnVlLCJleHAiOjE3NjYwMjcxMTUsInJvbGUiOiJhZG1pbiIsInN1YiI6IjRmNjgzZjRhLTFkMmEtNDRkMC1iYjI2LTFiMmJjMDNmNDk0ZCJ9.kCXNb9FB4vq7u5x6Jaaq7IKZmjXDggHlmRforT3pT8E",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            generated = data.get('response', '')
            
            # Display response in terminal
            print(f"📝 Response: {generated}")
            print(f"✅ Success ({len(generated)} chars, {data.get('sources', []).__len__()} sources)")
            
            responses.append({
                'id': test['id'],
                'nama': test['nama'],
                'query': test['query'],
                'golden_truth': test['golden_truth'],
                'generated': generated,
                'sources_count': len(data.get('sources', []))
            })
        else:
            error_msg = f"ERROR: HTTP {response.status_code}"
            print(f"❌ {error_msg}")
            responses.append({
                'id': test['id'],
                'nama': test['nama'],
                'query': test['query'],
                'golden_truth': test['golden_truth'],
                'generated': error_msg,
                'sources_count': 0
            })
    
    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        print(f"❌ {error_msg[:100]}")
        responses.append({
            'id': test['id'],
            'nama': test['nama'],
            'query': test['query'],
            'golden_truth': test['golden_truth'],
            'generated': error_msg,
            'sources_count': 0
        })

# Save responses
print(f"\n💾 Saving {len(responses)} responses to {OUTPUT_FILE}")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(responses, f, ensure_ascii=False, indent=2)

print(f"✅ Done! Generated {len(responses)} responses")
print(f"📄 Output: {OUTPUT_FILE}")
