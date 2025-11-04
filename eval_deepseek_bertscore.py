#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone evaluator: Ollama generation + BERTScore (Bahasa Indonesia)
- Reads a CSV
- Optionally reverse-geocodes lat/lon to a compact narrative
- Generates descriptions via Ollama
- Computes BERTScore against reference texts
- Writes an output CSV with predictions and scores

Required CSV columns:
- nama_tempat (str)
- kategori (str)
- latitude (float/str)
- longitude (float/str)
- deskripsi_referensi (str, the gold/reference to evaluate against)

Optional columns:
- lokasi_naratif (str). If provided and --no-geocode is used, script will not call Nominatim.
- deskripsi_prediksi (str). If provided and --reuse-preds is set, reuse instead of regenerating.

Usage example:
python eval_ollama_bertscore.py --csv-in cleaned_data.csv --csv-out bertscores.csv --model-name llama3.2
"""

import os
import time
import argparse
from typing import List, Dict, Any

import pandas as pd
import requests
from tqdm import tqdm

# Optional torch for device hint; bert_score auto-handles CPU if no CUDA
try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

from bert_score import score as bertscore
import ollama

# NEW: Import untuk visualisasi
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ------------------ Prompt scaffolding (deterministic style) ------------------

SYSTEM_MSG = (
    "Kamu menulis deskripsi usaha ringkas dalam Bahasa Indonesia, nada netral, faktual. "
    "Gunakan HANYA data yang diberikan. Dilarang menambahkan klaim, opini, atau asumsi. "
    "JANGAN sebut koordinat. Maks 2 kalimat. Kalimat pertama WAJIB diawali dengan nama usaha persis seperti input."
)

FEW_SHOTS = [
    {
        "role": "user",
        "content": "nama=WARUNG BAKSO PAK JOYO | kategori=Restoran | lokasi=Jalan Mawar, Lowokwaru, Malang, Jawa Timur"
    },
    {
        "role": "assistant",
        "content": "WARUNG BAKSO PAK JOYO adalah restoran yang menyajikan bakso di Jalan Mawar, Lowokwaru, Malang, Jawa Timur. Tempat ini cocok untuk santap cepat di kawasan sekitar."
    },
    {
        "role": "user",
        "content": "nama=TOKO MEGA JAYA | kategori=Toko Furnitur | lokasi=Jalan Sudirman, Pekanbaru, Riau"
    },
    {
        "role": "assistant",
        "content": "TOKO MEGA JAYA adalah toko furnitur di Jalan Sudirman, Pekanbaru, Riau. Tersedia ragam perabot rumah tangga untuk kebutuhan harian."
    },
]

def build_user_content(nama: str, kategori: str, lokasi_naratif: str) -> str:
    return f"nama={nama} | kategori={kategori} | lokasi={lokasi_naratif}"

# ------------------ Geocoding helpers ------------------

def create_map_link(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps?q={lat},{lon}"

def reverse_geocode(lat: float, lon: float, user_agent_email: str, timeout: float = 10.0) -> Dict[str, Any]:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": str(lat),
        "lon": str(lon),
        "zoom": 14,
        "addressdetails": 1,
        "accept-language": "id"
    }
    headers = {"User-Agent": f"capstone-geotagging/1.0 (mailto:{user_agent_email})"}
    r = requests.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    addr = data.get("address", {})
    parts = [
        addr.get("neighbourhood") or addr.get("suburb") or addr.get("village"),
        addr.get("city_district") or addr.get("town") or addr.get("city"),
        addr.get("county"),
        addr.get("state"),
    ]
    lokasi = ", ".join([p for p in parts if p])
    jalan = addr.get("road")
    return {
        "ringkas": lokasi,
        "jalan": jalan,
        "full": data.get("display_name", ""),
        "raw_data": data
    }

def build_lokasi_naratif(geo: Dict[str, Any]) -> str:
    if geo.get("jalan") and geo.get("ringkas"):
        return f"{geo['jalan']}, {geo['ringkas']}"
    if geo.get("ringkas"):
        return geo["ringkas"]
    return geo.get("full", "").strip()

# ------------------ Ollama call ------------------

def call_ollama(model_name: str, nama: str, kategori: str, lokasi_naratif: str,
                temperature: float, top_p: float, repeat_penalty: float) -> str:
    messages = [{"role": "system", "content": SYSTEM_MSG}]
    messages.extend(FEW_SHOTS)
    messages.append({"role": "user", "content": build_user_content(nama, kategori, lokasi_naratif)})
    resp = ollama.chat(
        model=model_name,
        messages=messages,
        options={
            "temperature": float(temperature),
            "top_p": float(top_p),
            "repeat_penalty": float(repeat_penalty),
        },
    )
    return resp["message"]["content"].strip()

# ------------------ Main pipeline ------------------

def normalize_float(x: Any) -> float:
    s = str(x).strip().replace(",", ".")
    return float(s)

def generate_predictions(df: pd.DataFrame, args) -> List[str]:
    preds: List[str] = []
    email = args.user_agent_email or "admin@example.com"
    for _, r in tqdm(df.iterrows(), total=len(df), desc="Generate"):
        nama = str(r["nama_tempat"]).strip()
        kategori = str(r["kategori"]).strip()

        # lokasi_naratif source
        if "lokasi_naratif" in df.columns and isinstance(r.get("lokasi_naratif", ""), str) and r.get("lokasi_naratif", "").strip():
            lokasi_naratif = str(r["lokasi_naratif"]).strip()
        else:
            if args.no_geocode:
                # deterministic fallback if geocode disabled
                lat = normalize_float(r["latitude"])
                lon = normalize_float(r["longitude"])
                lokasi_naratif = f"sekitar koordinat {lat:.6f}, {lon:.6f}"
            else:
                # geocode
                try:
                    lat = normalize_float(r["latitude"])
                    lon = normalize_float(r["longitude"])
                    geo = reverse_geocode(lat, lon, user_agent_email=email, timeout=args.geocode_timeout)
                    lokasi_naratif = build_lokasi_naratif(geo)
                    time.sleep(args.sleep)  # politeness
                except Exception:
                    lokasi_naratif = f"sekitar koordinat {normalize_float(r['latitude']):.6f}, {normalize_float(r['longitude']):.6f}"

        # LLM gen
        text = ""
        for attempt in range(args.retries):
            try:
                text = call_ollama(
                    model_name=args.model_name,
                    nama=nama,
                    kategori=kategori,
                    lokasi_naratif=lokasi_naratif,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    repeat_penalty=args.repeat_penalty,
                )
                break
            except Exception as e:
                if attempt + 1 >= args.retries:
                    text = f"{nama} adalah {kategori.lower()} yang berlokasi di {lokasi_naratif}."
                else:
                    time.sleep(1.2 * (attempt + 1))
        preds.append(text)
        if args.sleep_llm > 0:
            time.sleep(args.sleep_llm)
    return preds

# ------------------ Visualization functions ------------------

def create_visualizations(df: pd.DataFrame, output_prefix: str):
    """
    Generate 5 visualization charts for BERTScore evaluation results
    """
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # 1. Distribution Plot - Histogram untuk P, R, F1
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ['BERT_P', 'BERT_R', 'BERT_F1']
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    titles = ['Precision Distribution', 'Recall Distribution', 'F1 Distribution']
    
    for ax, metric, color, title in zip(axes, metrics, colors, titles):
        ax.hist(df[metric], bins=20, color=color, alpha=0.7, edgecolor='black')
        ax.axvline(df[metric].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df[metric].mean():.4f}')
        ax.axvline(df[metric].median(), color='orange', linestyle=':', linewidth=2, label=f'Median: {df[metric].median():.4f}')
        ax.set_xlabel('Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_prefix}_distribution.png")
    
    # 2. Box Plot - Perbandingan P, R, F1
    fig, ax = plt.subplots(figsize=(10, 6))
    data_to_plot = [df['BERT_P'], df['BERT_R'], df['BERT_F1']]
    bp = ax.boxplot(data_to_plot, labels=['Precision', 'Recall', 'F1'], 
                     patch_artist=True, notch=True, showmeans=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('BERTScore Metrics Comparison (DeepSeek-R1)', fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    plt.savefig(f"{output_prefix}_boxplot.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_prefix}_boxplot.png")
    
    # 3. Progression Chart - Score per sample
    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(df))
    ax.plot(x, df['BERT_P'], marker='o', label='Precision', alpha=0.7, linewidth=2, markersize=4)
    ax.plot(x, df['BERT_R'], marker='s', label='Recall', alpha=0.7, linewidth=2, markersize=4)
    ax.plot(x, df['BERT_F1'], marker='^', label='F1', alpha=0.7, linewidth=2, markersize=4)
    ax.axhline(df['BERT_F1'].mean(), color='red', linestyle='--', alpha=0.5, label=f'Mean F1: {df["BERT_F1"].mean():.4f}')
    
    ax.set_xlabel('Sample Index', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('BERTScore Progression Across Samples (DeepSeek-R1)', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.savefig(f"{output_prefix}_progression.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_prefix}_progression.png")
    
    # 4. Category Heatmap - Performance per kategori
    if 'kategori' in df.columns:
        category_stats = df.groupby('kategori')[['BERT_P', 'BERT_R', 'BERT_F1']].mean()
        
        if len(category_stats) > 0:
            fig, ax = plt.subplots(figsize=(10, max(6, len(category_stats) * 0.5)))
            sns.heatmap(category_stats, annot=True, fmt='.3f', cmap='RdYlGn', 
                       cbar_kws={'label': 'Score'}, linewidths=0.5, ax=ax)
            ax.set_title('Average BERTScore by Category (DeepSeek-R1)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Metrics', fontsize=12)
            ax.set_ylabel('Category', fontsize=12)
            plt.tight_layout()
            plt.savefig(f"{output_prefix}_heatmap.png", dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ Saved: {output_prefix}_heatmap.png")
    
    # 5. Summary Bar Chart dengan Error Bars
    fig, ax = plt.subplots(figsize=(10, 6))
    means = [df['BERT_P'].mean(), df['BERT_R'].mean(), df['BERT_F1'].mean()]
    stds = [df['BERT_P'].std(), df['BERT_R'].std(), df['BERT_F1'].std()]
    labels = ['Precision', 'Recall', 'F1']
    
    bars = ax.bar(labels, means, yerr=stds, capsize=10, 
                   color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar, mean, std in zip(bars, means, stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std,
                f'{mean:.4f}\n±{std:.4f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('BERTScore Summary Statistics (DeepSeek-R1)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_summary.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_prefix}_summary.png")

def main():
    p = argparse.ArgumentParser(description="Standalone evaluator: Ollama generation + BERTScore")
    p.add_argument("--csv-in", required=True, help="Path to input CSV")
    p.add_argument("--csv-out", default="bertscore_result.csv", help="Path to output CSV")
    p.add_argument("--model-name", default=os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b"), help="Ollama model name")
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--top-p", type=float, default=0.9)
    p.add_argument("--repeat-penalty", type=float, default=1.1)
    p.add_argument("--user-agent-email", default=os.environ.get("USER_AGENT_EMAIL", "admin@example.com"))
    p.add_argument("--sleep", type=float, default=0.3, help="Sleep between geocode calls (politeness)")
    p.add_argument("--sleep-llm", type=float, default=0.0, help="Optional sleep between LLM calls")
    p.add_argument("--geocode-timeout", type=float, default=10.0)
    p.add_argument("--no-geocode", action="store_true", help="Skip reverse geocoding; require lokasi_naratif or fallback to 'sekitar koordinat'")
    p.add_argument("--reuse-preds", action="store_true", help="Reuse existing deskripsi_prediksi column if present")
    p.add_argument("--recalc-bertscore", action="store_true", help="Recalculate BERTScore even if BERT_* columns exist")
    p.add_argument("--bert-model", default=os.environ.get("BERT_MODEL", "xlm-roberta-base"))
    p.add_argument("--bert-lang", default=os.environ.get("BERT_LANG", "id"))
    p.add_argument("--max-rows", type=int, default=None, help="Optional limit for quick testing")
    p.add_argument("--retries", type=int, default=3, help="Retries for LLM calls")
    p.add_argument("--no-viz", action="store_true", help="Skip visualization generation")
    args = p.parse_args()

    df = pd.read_csv(args.csv_in)

    required = ["nama_tempat", "kategori", "latitude", "longitude", "deskripsi_referensi"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV missing required columns: {missing}")

    if args.max_rows is not None:
        df = df.head(args.max_rows)

    # Prepare references
    references = df["deskripsi_referensi"].fillna("").astype(str).tolist()

    # Prepare predictions
    if args.reuse_preds and "deskripsi_prediksi" in df.columns and df["deskripsi_prediksi"].astype(str).str.strip().ne("").any():
        preds = df["deskripsi_prediksi"].fillna("").astype(str).tolist()
    else:
        preds = generate_predictions(df, args)
        df["deskripsi_prediksi"] = preds

    # Compute BERTScore
    device_str = "cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
    
    # Use lang parameter only for auto model selection
    P, R, F1 = bertscore(preds, references, lang=args.bert_lang, device=device_str)

    df["BERT_P"] = P.tolist()
    df["BERT_R"] = R.tolist()
    df["BERT_F1"] = F1.tolist()

    df.to_csv(args.csv_out, index=False)

    # Print summary statistics
    print("\n" + "="*60)
    print("BERTSCORE EVALUATION RESULTS (DeepSeek-R1)")
    print("="*60)
    print(f"Device: {device_str}")
    print(f"Model: {args.model_name}")
    print(f"Total Samples: {len(df)}")
    print(f"\n--- Metrics Summary ---")
    print(f"Precision  - Mean: {float(P.mean()):.4f} | Std: {float(P.std()):.4f}")
    print(f"Recall     - Mean: {float(R.mean()):.4f} | Std: {float(R.std()):.4f}")
    print(f"F1         - Mean: {float(F1.mean()):.4f} | Std: {float(F1.std()):.4f}")
    print(f"\n--- F1 Score Distribution ---")
    print(f"Min: {float(F1.min()):.4f}")
    print(f"25%: {float(np.percentile(F1.numpy(), 25)):.4f}")
    print(f"50%: {float(F1.median()):.4f}")
    print(f"75%: {float(np.percentile(F1.numpy(), 75)):.4f}")
    print(f"Max: {float(F1.max()):.4f}")
    print(f"\nSaved CSV: {args.csv_out}")
    
    # Generate visualizations
    if not args.no_viz:
        print("\n" + "-"*60)
        print("Generating visualizations...")
        print("-"*60)
        output_prefix = args.csv_out.replace('.csv', '')
        create_visualizations(df, output_prefix)
        print("-"*60)
        print("✓ All visualizations completed!")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
