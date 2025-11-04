import pandas as pd
import requests
from bert_score import score
from tqdm import tqdm

# 1. Load dataset hasil generate dan referensi
df = pd.read_csv("cleaned_data.csv")

# 2. Menyiapkan kolom referensi dan prediksi
# diasumsikan sudah ada kolom `deskripsi_prediksi` dari Ollama dan `deskripsi_referensi` manual
references = df["deskripsi_referensi"].fillna("").tolist()
candidates = df["deskripsi_prediksi"].fillna("").tolist()

# 3. Hitung skor BERTScore
P, R, F1 = score(candidates, references, lang="id", model_type="indobenchmark/indobert-base-p2")

# 4. Tambahkan ke dataframe
df["BERT_P"] = P.tolist()
df["BERT_R"] = R.tolist()
df["BERT_F1"] = F1.tolist()

# 5. Simpan hasil evaluasi
df.to_csv("bertscore_result.csv", index=False)
print("Evaluasi selesai → bertsore_result.csv")
print("Rata-rata F1:", F1.mean().item())
