# Capstone AI - Business Description Generator

A Flask-based API that generates business descriptions in Indonesian using AI and geocoding services. The application takes business name, category, and coordinates as input, then generates contextual descriptions using Ollama LLM and OpenStreetMap geocoding.

## Features

- **Reverse Geocoding**: Converts coordinates to readable addresses using OpenStreetMap Nominatim
- **AI Description Generation**: Uses Ollama Llama 3.2 model to generate business descriptions
- **Indonesian Language Support**: Generates descriptions in Bahasa Indonesia
- **Caching**: Implements LRU cache for geocoding requests
- **Error Handling**: Robust fallback mechanisms for geocoding and AI failures
- **BERTScore Evaluation**: Evaluate model performance with BERTScore metrics and visualizations

## Prerequisites

- Python 3.13
- Ollama installed with Llama 3.2 and DeepSeek-R1 models
- Internet connection for geocoding services

## Installation

### Windows

1. **Create virtual environment**:
   ```cmd
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```cmd
   pip install flask requests ollama geopy pandas bert-score torch transformers tqdm matplotlib seaborn scipy
   ```

### Linux/macOS

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask requests ollama geopy pandas bert-score torch transformers tqdm matplotlib seaborn scipy
   ```

## Setup Ollama

1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the required models:
   ```bash
   ollama pull llama3.2
   ollama pull deepseek-r1:1.5b
   ```

## Running the Application

### Start the Flask API

**Windows**:
```cmd
python app.py
```

**Linux/macOS**:
```bash
python3 app.py
```

The API will be available at `http://localhost:5000`

### Test the Geocoding (Optional)

Run the geocoding test script:

**Windows**:
```cmd
python geocoding.py
```

**Linux/macOS**:
```bash
python3 geocoding.py
```

### Test Ollama Connection (Optional)

Run the Ollama test script:

**Windows**:
```cmd
python run.py
```

**Linux/macOS**:
```bash
python3 run.py
```

## API Usage

### Endpoint: POST /generate

Generate a business description based on name, category, and coordinates.

**Request Body**:
```json
{
    "nama_tempat": "WARUNG BAKSO PAK JOYO",
    "kategori": "Restoran",
    "latitude": "-7.9666",
    "longitude": "112.6326"
}
```

**Response**:
```json
{
    "input": {
        "nama_tempat": "WARUNG BAKSO PAK JOYO",
        "latitude": -7.9666,
        "longitude": 112.6326,
        "kategori": "Restoran"
    },
    "geocode": {
        "ringkas": "Lowokwaru, Malang, Jawa Timur",
        "jalan": "Jalan Mawar",
        "full": "Jalan Mawar, Lowokwaru, Malang, Jawa Timur, Indonesia"
    },
    "lokasi_naratif": "Jalan Mawar, Lowokwaru, Malang, Jawa Timur",
    "deskripsi": "WARUNG BAKSO PAK JOYO adalah restoran yang menyajikan bakso di Jalan Mawar, Lowokwaru, Malang, Jawa Timur. Tempat ini cocok untuk santap cepat di kawasan sekitar."
}
```

### Example cURL Request

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "nama_tempat": "TOKO MEGA JAYA",
    "kategori": "Toko Furnitur",
    "latitude": "0.5070",
    "longitude": "101.4476"
  }'
```

---

## 📊 BERTScore Evaluation

Evaluate the quality of AI-generated descriptions using BERTScore metrics.

### Evaluation Files

| File | Model | Visualizations |
|------|-------|----------------|
| `eval_ollama_bertscore.py` | Llama 3.2 | ✅ 5 charts |
| `eval_deepseek_bertscore.py` | DeepSeek-R1 1.5B | ✅ 5 charts |

### Dataset Requirements

Your CSV must contain these columns:
- `nama_tempat` - Business name
- `kategori` - Business category
- `latitude` - Latitude coordinate
- `longitude` - Longitude coordinate
- `deskripsi_referensi` - Ground truth description (reference)

### Quick Start Evaluation

#### 1. Evaluate Llama 3.2 (Test with 5 samples)

**Windows**:
```cmd
python eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_test.csv --max-rows 5 --no-geocode
```

**Linux/macOS**:
```bash
python3 eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_test.csv --max-rows 5 --no-geocode
```

#### 2. Evaluate DeepSeek-R1 (Test with 5 samples)

**Windows**:
```cmd
python eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_test.csv --max-rows 5 --no-geocode
```

**Linux/macOS**:
```bash
python3 eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_test.csv --max-rows 5 --no-geocode
```

### Full Evaluation (All Data)

#### Llama 3.2 Full Evaluation

**Windows**:
```cmd
python eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_full_results.csv --bert-model xlm-roberta-base
```

**Linux/macOS**:
```bash
python3 eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_full_results.csv --bert-model xlm-roberta-base
```

#### DeepSeek-R1 Full Evaluation

**Windows**:
```cmd
python eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_full_results.csv --bert-model xlm-roberta-base
```

**Linux/macOS**:
```bash
python3 eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_full_results.csv --bert-model xlm-roberta-base
```

### Evaluation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--csv-in` | **required** | Input CSV file path |
| `--csv-out` | `bertscore_result.csv` | Output CSV file path |
| `--model-name` | `llama3.2` / `deepseek-r1:1.5b` | Ollama model to use |
| `--max-rows` | `None` | Limit rows for testing (e.g., `5`, `10`) |
| `--no-geocode` | `False` | Skip geocoding (faster) |
| `--no-viz` | `False` | Skip visualization generation |
| `--bert-model` | `xlm-roberta-base` | BERT model for scoring |
| `--temperature` | `0.3` | LLM temperature (0.0-1.0) |
| `--top-p` | `0.9` | Nucleus sampling parameter |
| `--repeat-penalty` | `1.1` | Repetition penalty |

### Output Files

Each evaluation generates:

1. **CSV Results** - Contains predictions and BERTScore metrics
   - `{output_name}.csv`

2. **5 Visualization Charts** (PNG format):
   - `{output_name}_distribution.png` - Histogram of P, R, F1 scores
   - `{output_name}_boxplot.png` - Box plot comparison
   - `{output_name}_progression.png` - Score progression per sample
   - `{output_name}_heatmap.png` - Performance by category
   - `{output_name}_summary.png` - Summary bar chart with error bars

### Understanding BERTScore Metrics

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| **Precision (P)** | How many predicted tokens are relevant | Higher = fewer irrelevant words |
| **Recall (R)** | How many reference tokens are covered | Higher = more complete coverage |
| **F1** | Harmonic mean of P and R | **Main metric** for overall quality |

### Quality Benchmarks

| F1 Score | Quality Level |
|----------|---------------|
| > 0.90 | 🟢 Excellent |
| 0.80 - 0.90 | 🟡 Good |
| 0.70 - 0.80 | 🟠 Fair |
| < 0.70 | 🔴 Needs Improvement |

### Example: Compare Both Models

**Windows**:
```cmd
REM Evaluate Llama 3.2
python eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_results.csv --no-geocode

REM Evaluate DeepSeek-R1
python eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_results.csv --no-geocode
```

**Linux/macOS**:
```bash
# Evaluate Llama 3.2
python3 eval_ollama_bertscore.py --csv-in added_ref.csv --csv-out llama_results.csv --no-geocode

# Evaluate DeepSeek-R1
python3 eval_deepseek_bertscore.py --csv-in added_ref.csv --csv-out deepseek_results.csv --no-geocode
```

### Analyzing Results in Python

```python
import pandas as pd

# Load results
llama_df = pd.read_csv("llama_results.csv")
deepseek_df = pd.read_csv("deepseek_results.csv")

# Compare F1 scores
print(f"Llama 3.2 Mean F1: {llama_df['BERT_F1'].mean():.4f}")
print(f"DeepSeek-R1 Mean F1: {deepseek_df['BERT_F1'].mean():.4f}")

# Per-category analysis
llama_by_cat = llama_df.groupby('kategori')['BERT_F1'].mean()
deepseek_by_cat = deepseek_df.groupby('kategori')['BERT_F1'].mean()

comparison = pd.DataFrame({
    'Llama_F1': llama_by_cat,
    'DeepSeek_F1': deepseek_by_cat
})
print(comparison.sort_values('Llama_F1', ascending=False))
```

### Troubleshooting Evaluation

#### Error: `KeyError: 'indobenchmark/indobert-base-p2'`
**Solution**: Use supported BERT model
```cmd
--bert-model xlm-roberta-base
```

#### Error: `TclError: Can't find a usable init.tcl`
**Solution**: Already fixed - scripts use `matplotlib.use('Agg')` backend

#### Evaluation too slow
**Solutions**:
- Use `--no-geocode` flag (skip reverse geocoding)
- Use `--max-rows 10` for testing
- Add `--sleep-llm 0` to remove delays

#### Ollama connection refused
**Solution**: Make sure Ollama is running
```bash
ollama serve
```

---

## File Structure

```
capstone-ai/
├── app.py                        # Main Flask application
├── geocoding.py                  # Geocoding test script
├── run.py                        # Ollama test script
├── eval_ollama_bertscore.py      # Llama 3.2 evaluation script
├── eval_deepseek_bertscore.py    # DeepSeek-R1 evaluation script
├── evaluate_bertscore.py         # Simple evaluation (deprecated)
├── EVALUATION_GUIDE.md           # Detailed evaluation documentation
├── readme.md                     # This file
├── added_ref.csv                 # Sample dataset with references
└── .gitignore                    # Git ignore rules
```

## Dependencies

### Core API
- **Flask**: Web framework for the API
- **requests**: HTTP library for geocoding API calls
- **ollama**: Python client for Ollama LLM
- **geopy**: Geocoding library (used in test script)

### Evaluation
- **pandas**: Data manipulation and CSV handling
- **bert-score**: BERTScore metric calculation
- **torch**: PyTorch for BERT model backend
- **transformers**: Hugging Face transformers library
- **tqdm**: Progress bars for long operations
- **matplotlib**: Visualization library
- **seaborn**: Statistical data visualization
- **scipy**: Scientific computing utilities

## Error Handling

The application includes comprehensive error handling:

- **Invalid coordinates**: Returns 400 error with validation message
- **Missing required fields**: Returns 400 error listing required fields
- **Geocoding failures**: Falls back to coordinate-based location description
- **AI model failures**: Falls back to template-based description generation

## Deactivating Virtual Environment

When you're done working:

**Windows**:
```cmd
deactivate
```

**Linux/macOS**:
```bash
deactivate
```

## Notes

- The application uses OpenStreetMap Nominatim for geocoding (free service)
- Geocoding results are cached using LRU cache for better performance
- The AI model generates descriptions in Indonesian with neutral, factual tone
- Coordinate formats support both comma and period decimal separators
- BERTScore evaluation uses `xlm-roberta-base` model optimized for Indonesian
- Visualizations are automatically saved as PNG files (300 DPI)
- Evaluation scripts support both CPU and GPU (CUDA) execution

## License

This project is for educational purposes (Capstone Project).

## Support

For detailed evaluation guide, see [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)
