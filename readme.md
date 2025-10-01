# Capstone AI - Business Description Generator

A Flask-based API that generates business descriptions in Indonesian using AI and geocoding services. The application takes business name, category, and coordinates as input, then generates contextual descriptions using Ollama LLM and OpenStreetMap geocoding.

## Features

- **Reverse Geocoding**: Converts coordinates to readable addresses using OpenStreetMap Nominatim
- **AI Description Generation**: Uses Ollama Llama 3.2 model to generate business descriptions
- **Indonesian Language Support**: Generates descriptions in Bahasa Indonesia
- **Caching**: Implements LRU cache for geocoding requests
- **Error Handling**: Robust fallback mechanisms for geocoding and AI failures

## Prerequisites

- Python 3.13
- Ollama installed with Llama 3.2 model
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
   pip install flask requests ollama geopy
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
   pip install flask requests ollama geopy
   ```

## Setup Ollama

1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull the Llama 3.2 model:
   ```bash
   ollama pull llama3.2
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

## File Structure

```
capstone-ai/
├── app.py              # Main Flask application
├── geocoding.py        # Geocoding test script
├── run.py             # Ollama test script
├── readme.md          # This file
└── .gitignore         # Git ignore rules
```

## Dependencies

- **Flask**: Web framework for the API
- **requests**: HTTP library for geocoding API calls
- **ollama**: Python client for Ollama LLM
- **geopy**: Geocoding library (used in test script)

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