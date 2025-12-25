# Postman Testing Guide

## 📥 Import Collection

1. Buka Postman
2. Click **Import** button
3. Pilih file: `Geotags_Chatbot_API.postman_collection.json`
4. Collection akan muncul di sidebar

## 🔧 Setup Environment Variables

Setelah import, set environment variables:

### Method 1: Collection Variables (Recommended)
1. Click pada collection "Geotags Chatbot API"
2. Tab **Variables**
3. Edit values:
   - `base_url`: `http://localhost:5000` (atau port yang Anda gunakan)
   - `jwt_token`: Paste JWT token dari backend service Anda

### Method 2: Environment
1. Click ⚙️ (Settings) → **Environments**
2. Create new environment: "Geotags Local"
3. Add variables:
   ```
   base_url = http://localhost:5000
   jwt_token = your_actual_jwt_token_here
   ```
4. Select environment dari dropdown

## 🔑 Mendapatkan JWT Token

Anda perlu JWT token dari backend service yang sudah ada. Token harus di-generate dengan `JWT_SECRET_KEY` yang sama.

**Contoh cara get token** (sesuaikan dengan backend Anda):
```bash
# Login ke backend service
curl -X POST http://your-backend/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Response akan berisi token
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Copy token tersebut ke variable `jwt_token` di Postman.

## 📋 Available Requests

### 1. Health Check ✅
**No authentication required**
- Method: `GET`
- Endpoint: `/api/health`
- Purpose: Check if service is running

### 2. Root Endpoint
**No authentication required**
- Method: `GET`
- Endpoint: `/`
- Purpose: Get service info

### 3. Chat - Cari Warung Kopi ☕
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Cari warung kopi di Balikpapan",
    "top_k": 5
  }
  ```

### 4. Chat - Cari Usaha Sembako 🛒
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Ada usaha sembako di mana?",
    "top_k": 3
  }
  ```

### 5. Chat - Cari SPBU ⛽
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Cari SPBU atau pom bensin",
    "top_k": 5
  }
  ```

### 6. Chat - Berapa Jumlah Usaha 📊
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Berapa jumlah usaha yang aktif?",
    "top_k": 10
  }
  ```

### 7. Chat - Dengan Conversation History 💬
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Berapa alamat lengkapnya?",
    "top_k": 5,
    "conversation_history": [
      {
        "role": "user",
        "content": "Cari warung kopi di Balikpapan"
      },
      {
        "role": "assistant",
        "content": "Saya menemukan Warung KPK Balikpapan"
      }
    ]
  }
  ```

### 8. Chat - Cari di Kecamatan Tertentu 📍
**Requires JWT**
- Method: `POST`
- Endpoint: `/api/chat`
- Body:
  ```json
  {
    "message": "Usaha apa saja yang ada di Balikpapan Utara?",
    "top_k": 5
  }
  ```

### 9. Get All Businesses 📋
**Requires JWT**
- Method: `GET`
- Endpoint: `/api/businesses`
- Purpose: Get all businesses from database

### 10. API Docs (Swagger) 📚
**No authentication required**
- Method: `GET`
- Endpoint: `/docs`
- Opens interactive Swagger UI in browser

## 🧪 Testing Workflow

### Quick Test (No Auth)
1. **Health Check** → Should return `{"status": "healthy"}`
2. **Root Endpoint** → Should return service info

### Full Test (With Auth)
1. Set your `jwt_token` variable
2. **Get All Businesses** → Verify data is retrieved
3. **Chat - Cari Warung Kopi** → Test basic chat
4. **Chat - Cari Usaha Sembako** → Test different query
5. **Chat - Dengan Conversation History** → Test context awareness

## 📊 Expected Responses

### Success Response (Chat)
```json
{
  "response": "Berikut adalah usaha yang relevan:\n\n1. Warung KPK Balikpapan...",
  "sources": [
    {
      "usaha_id": "92d0db0b-8c35-4bd9-b497-92b9c293ed5d",
      "nama_usaha": "Warung KPK Balikpapan",
      "alamat": "Jalan pol zainal arifin No.2E...",
      "kategori": "MINUMAN KOPI",
      "relevance_score": 0.89
    }
  ],
  "context_used": true,
  "user_id": "4f683f4a-1d2a-44d0-bb26-1b2bc03f494d"
}
```

### Error Response (No Token)
```json
{
  "detail": "Token tidak ditemukan"
}
```

### Error Response (Invalid Token)
```json
{
  "detail": "Token tidak valid"
}
```

## 🔍 Troubleshooting

### 401 Unauthorized
- **Problem**: Token tidak valid atau tidak ada
- **Solution**: 
  - Check `jwt_token` variable sudah di-set
  - Pastikan token belum expired
  - Verify `JWT_SECRET_KEY` sama dengan backend

### 500 Internal Server Error
- **Problem**: Server error
- **Solution**:
  - Check server logs
  - Pastikan database connected
  - Verify Ollama running

### Connection Refused
- **Problem**: Server tidak running
- **Solution**: 
  - Start server: `run.bat`
  - Check `base_url` correct (port 5000)

## 💡 Tips

1. **Save Responses**: Click "Save Response" untuk compare results
2. **Use Tests**: Add test scripts untuk automated validation
3. **Environment Switching**: Create multiple environments (local, staging, prod)
4. **Monitor**: Use Postman Console (View → Show Postman Console) untuk debug

## 🚀 Advanced Usage

### Add Test Script
Di tab **Tests** pada request, tambahkan:

```javascript
// Verify status code
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Verify response structure
pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('response');
    pm.expect(jsonData).to.have.property('sources');
});

// Verify sources not empty
pm.test("Sources array is not empty", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.sources.length).to.be.above(0);
});
```

### Run Collection
1. Click **Runner** button
2. Select "Geotags Chatbot API" collection
3. Click **Run Geotags Chatbot API**
4. View test results

## 📝 Notes

- Server harus running di `http://localhost:5000` (atau sesuai config)
- Ollama harus running untuk chat endpoints
- Database harus accessible
- JWT token harus valid dan belum expired
