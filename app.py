# app.py
from flask import Flask, request, jsonify
import requests
import ollama
from functools import lru_cache

app = Flask(__name__)

# ---------- Geocoding ----------
@lru_cache(maxsize=2048)
def reverse_geocode(lat: float, lon: float) -> dict:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": str(lat),
        "lon": str(lon),
        "zoom": 14,
        "addressdetails": 1,
        "accept-language": "id"
    }
    headers = {"User-Agent": "capstone-geotagging/1.0 (mailto:admin@example.com)"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    addr = data.get("address", {})
    # susun lokasi ringkas yang stabil
    parts = [
        addr.get("neighbourhood") or addr.get("suburb") or addr.get("village"),
        addr.get("city_district") or addr.get("town") or addr.get("city"),
        addr.get("county"),
        addr.get("state"),
    ]
    lokasi = ", ".join([p for p in parts if p])
    jalan = addr.get("road")
    return {
        "ringkas": lokasi,                      # ex: "Muara Rapak, Balikpapan Utara, Balikpapan, Kalimantan Timur"
        "jalan": jalan,                          # ex: "Jalan Batu Butok"
        "full": data.get("display_name", "")
    }

def build_lokasi_naratif(geo: dict) -> str:
    # Prioritas: Jalan + ringkas; fallback ke ringkas; terakhir full
    if geo.get("jalan") and geo.get("ringkas"):
        return f"{geo['jalan']}, {geo['ringkas']}"
    if geo.get("ringkas"):
        return geo["ringkas"]
    return geo.get("full", "").strip()

# ---------- Prompting ----------
SYSTEM_MSG = (
    "Kamu menulis deskripsi usaha ringkas dalam Bahasa Indonesia, nada netral, faktual. "
    "Gunakan HANYA data yang diberikan. Dilarang menambahkan klaim, opini, atau asumsi. "
    "JANGAN sebut koordinat. Maks 2 kalimat. Kalimat pertama WAJIB diawali dengan nama usaha persis seperti input."
)

# Few-shot contoh untuk menstabilkan gaya
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
    # format deterministik, tanpa koordinat, tanpa klaim non-faktual
    return f"nama={nama} | kategori={kategori} | lokasi={lokasi_naratif}"

def call_ollama(nama: str, kategori: str, lokasi_naratif: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_MSG}]
    messages.extend(FEW_SHOTS)
    messages.append({"role": "user", "content": build_user_content(nama, kategori, lokasi_naratif)})
    resp = ollama.chat(
        model="llama3.2",
        messages=messages,
        options={
            "temperature": 0.4,
            "top_p": 0.9,
            "repeat_penalty": 1.1
        }
    )
    return resp["message"]["content"].strip()

# ---------- API ----------
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    nama = (data.get("nama_tempat") or "").strip()
    kategori = (data.get("kategori") or "").strip()
    lat_raw = (data.get("latitude") or "").strip()
    lon_raw = (data.get("longitude") or "").strip()

    if not (nama and kategori and lat_raw and lon_raw):
        return jsonify({"error": "nama_tempat, latitude, longitude, kategori wajib diisi"}), 400

    # Normalisasi desimal (ganti koma -> titik jika perlu)
    def to_float(x: str) -> float:
        return float(x.replace(",", "."))
    try:
        lat = to_float(lat_raw)
        lon = to_float(lon_raw)
    except ValueError:
        return jsonify({"error": "latitude/longitude tidak valid"}), 400

    # Reverse geocode → lokasi naratif
    try:
        geo = reverse_geocode(lat, lon)
        lokasi_naratif = build_lokasi_naratif(geo)
    except Exception as e:
        # fallback bila geocoding gagal → tetap bisa generate tanpa alamat rinci
        geo = {"ringkas": "", "jalan": "", "full": ""}
        lokasi_naratif = f"sekitar koordinat {lat:.6f}, {lon:.6f}"

    # Panggil LLM (guardrail: jika tidak ada lokasi, tetap jalan)
    try:
        deskripsi = call_ollama(nama=nama, kategori=kategori, lokasi_naratif=lokasi_naratif)
    except Exception as e:
        # Fallback deterministic bila LLM error
        if lokasi_naratif.startswith("sekitar koordinat"):
            deskripsi = f"{nama} adalah {kategori.lower()} di {lokasi_naratif}."
        else:
            deskripsi = f"{nama} adalah {kategori.lower()} yang berlokasi di {lokasi_naratif}."

    return jsonify({
        "input": {
            "nama_tempat": nama,
            "latitude": lat,
            "longitude": lon,
            "kategori": kategori
        },
        "geocode": geo,
        "lokasi_naratif": lokasi_naratif,
        "deskripsi": deskripsi
    })

if __name__ == "__main__":
    app.run(debug=True)
