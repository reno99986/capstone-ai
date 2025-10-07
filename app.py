import logging
import os
from functools import lru_cache
import ollama
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- KONFIGURASI APLIKASI ---
load_dotenv()  # Memuat variabel dari file .env
app = Flask(__name__)

# --------------------------------------------------------------------------
# BAGIAN FUNGSI-FUNGSI UTAMA
# --------------------------------------------------------------------------

@lru_cache(maxsize=2048)
def reverse_geocode(lat: float, lon: float) -> dict:
    """Sedang Mengambil alamat dari koordinat menggunakan Nominatim API."""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": str(lat),
        "lon": str(lon),
        "zoom": 14,
        "addressdetails": 1,
        "accept-language": "id"
    }
    email = os.getenv("USER_AGENT_EMAIL", "admin@example.com")
    headers = {"User-Agent": f"capstone-geotagging/1.0 (mailto:{email})"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()  # Akan memicu error jika status code bukan 2xx
    return r.json()

def build_lokasi_naratif(data: dict) -> str:
    """Menyusun alamat naratif dari data geocoding."""
    addr = data.get("address", {})
    parts = [
        addr.get("neighbourhood") or addr.get("suburb") or addr.get("village"),
        addr.get("city_district") or addr.get("town") or addr.get("city"),
        addr.get("county"),
        addr.get("state"),
    ]
    lokasi_ringkas = ", ".join([p for p in parts if p])
    jalan = addr.get("road")

    if jalan and lokasi_ringkas:
        return f"{jalan}, {lokasi_ringkas}"
    return lokasi_ringkas or data.get("display_name", "").strip()

def call_ollama(nama: str, kategori: str, lokasi_naratif: str) -> str:
    """Memanggil model LLM melalui Ollama untuk menghasilkan deskripsi."""
    SYSTEM_MSG = (
        "Kamu menulis deskripsi usaha ringkas dalam Bahasa Indonesia, nada netral, faktual. "
        "Gunakan HANYA data yang diberikan. Dilarang menambahkan klaim, opini, atau asumsi. "
        "JANGAN sebut koordinat. Maks 2 kalimat. Kalimat pertama WAJIB diawali dengan nama usaha persis seperti input."
    )
    FEW_SHOTS = [
        {"role": "user", "content": "nama=WARUNG BAKSO PAK JOYO | kategori=Restoran | lokasi=Jalan Mawar, Lowokwaru, Malang, Jawa Timur"},
        {"role": "assistant", "content": "WARUNG BAKSO PAK JOYO adalah restoran yang menyajikan bakso di Jalan Mawar, Lowokwaru, Malang, Jawa Timur. Tempat ini cocok untuk santap cepat di kawasan sekitar."}
    ]
    
    model_name = os.getenv("OLLAMA_MODEL", "llama3")
    user_content = f"nama={nama} | kategori={kategori} | lokasi={lokasi_naratif}"
    
    messages = [{"role": "system", "content": SYSTEM_MSG}]
    messages.extend(FEW_SHOTS)
    messages.append({"role": "user", "content": user_content})
    
    resp = ollama.chat(
        model=model_name,
        messages=messages,
        options={"temperature": 0.4, "top_p": 0.9, "repeat_penalty": 1.1}
    )
    return resp["message"]["content"].strip()


# --------------------------------------------------------------------------
# BAGIAN API ENDPOINT
# --------------------------------------------------------------------------

@app.route("/generate", methods=["POST"])
def generate():
    """Endpoint utama untuk menerima data dan menghasilkan deskripsi."""
    data = request.get_json(silent=True) or {}
    nama = (data.get("nama_tempat") or "").strip()
    kategori = (data.get("kategori") or "").strip()
    lat_raw = (data.get("latitude") or "").strip()
    lon_raw = (data.get("longitude") or "").strip()

    if not (nama and kategori and lat_raw and lon_raw):
        return jsonify({"error": "nama_tempat, latitude, longitude, kategori wajib diisi"}), 400

    try:
        lat = float(lat_raw.replace(",", "."))
        lon = float(lon_raw.replace(",", "."))
    except ValueError:
        return jsonify({"error": "latitude/longitude tidak valid"}), 400

    # --- Proses Geocoding dengan Logging Error ---
    try:
        geo_data = reverse_geocode(lat, lon)
        lokasi_naratif = build_lokasi_naratif(geo_data)
    except Exception as e:
        # Jika geocoding gagal, catat errornya dan buat respons darurat.
        logging.error(f"Geocoding GAGAL untuk lat={lat}, lon={lon}. Error: {e}")
        geo_data = {}
        lokasi_naratif = f"sekitar koordinat {lat:.6f}, {lon:.6f}"

    # --- Panggil LLM dengan Logging Error ---
    try:
        deskripsi = call_ollama(nama=nama, kategori=kategori, lokasi_naratif=lokasi_naratif)
    except Exception as e:
        # Jika Ollama gagal, catat errornya dan buat deskripsi darurat.
        logging.error(f"Panggilan Ollama GAGAL untuk nama='{nama}'. Error: {e}")
        deskripsi = f"{nama} adalah {kategori.lower()} yang berlokasi di {lokasi_naratif}."

    return jsonify({
        "input": {"nama_tempat": nama, "latitude": lat, "longitude": lon, "kategori": kategori},
        "geocode": geo_data.get("address", {}),
        "lokasi_naratif": lokasi_naratif,
        "deskripsi": deskripsi
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")