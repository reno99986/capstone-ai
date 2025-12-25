# Perbaikan Gaya Penulisan Chatbot

## Masalah

Chatbot menghasilkan response yang **terlalu formal dan bertele-tele** dengan frasa marketing yang berlebihan:

❌ **Contoh Response Buruk:**

```
"Terima kasih telah memilih aplikasi Geotags sebagai sumber informasi untuk menemukan usaha yang Anda cari!

Gamon boba dan es jeruk peras adalah sebuah usaha yang memiliki dua lokasi:..."
```

**Masalah:**

- Salam pembuka yang tidak perlu
- Frasa marketing yang berlebihan
- Terlalu panjang untuk informasi sederhana
- Tidak langsung ke poin

## Solusi

### 1. Update System Prompt

Menambahkan **aturan gaya penulisan** yang eksplisit:

```python
GAYA PENULISAN:
- Langsung ke poin utama, TANPA salam pembuka yang berlebihan
- JANGAN gunakan frasa marketing seperti "Terima kasih telah memilih...", "Saya senang membantu...", dll
- JANGAN gunakan frasa bertele-tele seperti "Berikut adalah informasi yang relevan tentang..."
- Cukup langsung jawab pertanyaan dengan format: "[Nama Usaha] adalah [deskripsi singkat]"
- Sertakan detail penting: alamat, kategori, status (jika relevan)
```

### 2. Tambahkan Contoh Konkret

Memberikan **contoh jawaban yang baik vs buruk** langsung di system prompt:

```
CONTOH JAWABAN YANG BAIK:
User: "Jelaskan tentang Soto Banjar Azizah"
❌ BURUK: "Terima kasih telah memilih aplikasi Geotags! Berikut adalah informasi yang relevan tentang Soto Banjar Azizah Bilqis..."
✅ BAIK: "Soto Banjar Azizah Bilqis adalah rumah makan yang berlokasi di Jl. Serindit No.123, Gunung Bahagia, Balikpapan Selatan. Status: Aktif."

User: "Berapa jumlah usaha di Balikpapan?"
❌ BURUK: "Terima kasih atas pertanyaannya! Saya dengan senang hati menjelaskan bahwa berdasarkan data terkini..."
✅ BAIK: "Terdapat 614 usaha di Balikpapan, dengan 612 usaha aktif dan 2 tidak aktif."
```

## Perbandingan

### Sebelum

**Query:** "Jelaskan tentang Gamon boba dan es jeruk peras"

**Response:**

```
Terima kasih telah memilih aplikasi Geotags sebagai sumber informasi untuk menemukan usaha yang Anda cari!

Gamon boba dan es jeruk peras adalah sebuah usaha yang memiliki dua lokasi:

1.  Alamat: Jl. Klamono, Muara Rapak, Kec. Balikpapan Utara, Kota Balikpapan, Kalimantan Timur
2.  Alamat: QR6M+QJ5, Jl. Klamono, Muara Rapak, Kec. Balikpapan Utara, Kota Balikpapan, Kalimantan Timur 76124

Kedua lokasi ini memiliki beberapa kesamaan, seperti menjadi usaha yang menjual minuman jeruk peras dan memiliki nama komersial yang sama: Gamon boba dan es jeruk peras.

Lokasi kedua memiliki alamat yang berbeda, tetapi keduanya masih terletak di Jl. Klamono, Muara Rapak, Balikpapan Utara.

Kedua lokasi ini juga memiliki status yang sama, yaitu aktif dan memiliki koordinat yang unik:
-1.238191,-116.834070 (lokasi 1) dan -1.238107,-116.834122 (lokasi 2)

Saya harap informasi ini membantu Anda menemukan Gamon boba dan es jeruk peras di Balikpapan!
```

**Masalah:**

- 2 frasa marketing yang tidak perlu
- Terlalu panjang (400+ karakter)
- Informasi redundan

### Sesudah (Expected)

**Query:** "Jelaskan tentang Gamon boba dan es jeruk peras"

**Response:**

```
Gamon boba dan es jeruk peras adalah kedai minuman dengan 2 lokasi di Jl. Klamono, Muara Rapak, Balikpapan Utara:

1. Lokasi 1: Jl. Klamono, Muara Rapak (Koordinat: -1.238191, 116.834070)
2. Lokasi 2: QR6M+QJ5, Jl. Klamono, Muara Rapak 76124 (Koordinat: -1.238107, 116.834122)

Produk utama: Minuman jeruk peras. Status: Aktif.
```

**Improvement:**

- ✅ Langsung ke poin
- ✅ Tidak ada frasa marketing
- ✅ Lebih ringkas (~200 karakter, 50% lebih pendek)
- ✅ Informasi tetap lengkap

## Frasa yang Dihindari

### ❌ Frasa Marketing

- "Terima kasih telah memilih aplikasi Geotags..."
- "Saya dengan senang hati menjelaskan..."
- "Saya akan gembira membantu Anda..."
- "Saya harap informasi ini membantu..."

### ❌ Frasa Bertele-tele

- "Berikut adalah informasi yang relevan tentang..."
- "Tentu, saya dapat membantu Anda menjelaskan..."
- "Berdasarkan data yang tersedia..."
- "Informasi menunjukkan bahwa..."

### ✅ Format yang Baik

- Langsung: "[Nama Usaha] adalah [deskripsi]"
- Ringkas: "Terdapat [jumlah] usaha..."
- Faktual: "Alamat: [alamat]. Kategori: [kategori]. Status: [status]."

## Testing

### Test Case 1: Business Info

**Query:** "Jelaskan tentang Soto Banjar Azizah"

**Expected:**

```
Soto Banjar Azizah Bilqis adalah rumah makan yang berlokasi di Jl. Serindit No.123, RT.02, Gunung Bahagia, Balikpapan Selatan. Status: Aktif.
```

### Test Case 2: Statistics

**Query:** "Berapa jumlah usaha di Balikpapan?"

**Expected:**

```
Terdapat 614 usaha di Balikpapan, dengan 612 usaha aktif (99.7%) dan 2 usaha tidak aktif (0.3%).
```

### Test Case 3: Not Found

**Query:** "Jelaskan tentang McDonald's"

**Expected:**

```
Tidak ditemukan informasi tentang McDonald's dalam database.
```

**NOT:**

```
Maaf, saya tidak menemukan informasi tentang McDonald's dalam data yang Anda berikan. Jika Anda dapat memberikan lebih banyak konteks atau informasi tentang McDonald's, saya akan gembira membantu Anda mencari jawabannya.
```

## Monitoring

Untuk memastikan improvement bekerja:

1. **Re-generate responses:**

   ```bash
   cd evaluation
   python generate_responses.py
   ```

2. **Re-evaluate:**

   ```bash
   python evaluate_chatbot.py
   ```

3. **Check metrics:**

   - BERTScore should remain similar or improve
   - Response length should decrease
   - Discrimination rate should remain high

4. **Manual review:**
   - Cek `generated_responses.json`
   - Pastikan tidak ada frasa marketing
   - Pastikan response langsung ke poin

## Expected Impact

### Metrics

| Metric              | Before            | After (Expected)           |
| ------------------- | ----------------- | -------------------------- |
| Avg Response Length | ~250 chars        | ~150 chars (40% shorter)   |
| BERTScore F1        | 0.87              | 0.85-0.90 (similar/better) |
| Discrimination Rate | 92%               | 90-95% (maintained)        |
| User Satisfaction   | Low (too verbose) | High (concise)             |

### Benefits

1. **Better UX:**

   - Faster to read
   - More professional
   - Less annoying

2. **Better Performance:**

   - Shorter responses = faster generation
   - Less token usage
   - Lower latency

3. **Better Accuracy:**
   - Less hallucination risk
   - More focused on facts
   - Easier to verify

## Rollback

Jika ada masalah, rollback dengan mengembalikan system prompt ke versi sebelumnya:

```python
self.system_prompt = """Anda adalah asisten chatbot untuk aplikasi Geotags yang membantu pengguna mencari informasi tentang usaha/bisnis.

Tugas Anda:
1. Menjawab pertanyaan tentang usaha berdasarkan data yang diberikan
2. Memberikan informasi yang akurat dan relevan
...
"""
```

## Conclusion

Dengan menambahkan **aturan gaya penulisan eksplisit** dan **contoh konkret** di system prompt, chatbot sekarang akan:

- ✅ Lebih ringkas dan langsung ke poin
- ✅ Tidak menggunakan frasa marketing yang berlebihan
- ✅ Lebih profesional dan informatif
- ✅ Tetap sopan tanpa bertele-tele

Server sudah auto-reload, jadi perubahan langsung aktif! Test dengan query baru untuk melihat perbedaannya.
