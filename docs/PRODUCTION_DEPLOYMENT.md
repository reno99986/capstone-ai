# 🚀 Production Deployment Guide

Complete guide untuk deploy chatbot FastAPI + RAG ke production environment.

---

## 📋 **Pre-Deployment Checklist**

### **1. Environment Differences**

| Aspect              | Development            | Production              |
| ------------------- | ---------------------- | ----------------------- |
| **Evaluation Mode** | `EVALUATION_MODE=true` | `EVALUATION_MODE=false` |
| **Data Source**     | CSV file               | Database                |
| **Reload**          | `--reload` enabled     | No reload               |
| **Debug**           | Enabled                | Disabled                |
| **Host**            | `localhost`            | `0.0.0.0` or domain     |
| **HTTPS**           | Optional               | **Required**            |

### **2. Requirements**

- ✅ PostgreSQL database (production)
- ✅ Ollama server (running LLM model)
- ✅ Python 3.11+
- ✅ HTTPS certificate (SSL/TLS)
- ✅ Reverse proxy (Nginx/Apache)
- ✅ Process manager (systemd/supervisor)

---

## 🔧 **Step 1: Configure Production Environment**

### **Edit `.env` for Production**

```bash
# Database (Production PostgreSQL)
DATABASE_URL=postgresql://user:password@production-db-host:5432/geotags_db

# JWT Security
JWT_SECRET_KEY=your-super-secret-256-bit-key-here  # CHANGE THIS!
JWT_ALGORITHM=HS256

# LLM Configuration
CHATBOT_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434

# RAG Configuration
RAG_SYNC_INTERVAL_SECONDS=300  # 5 minutes in production

# PRODUCTION MODE (CRITICAL!)
EVALUATION_MODE=false

# Server (if using environment vars)
HOST=0.0.0.0
PORT=5000
```

**⚠️ SECURITY:**

- **NEVER** commit `.env` to git
- Use strong `JWT_SECRET_KEY` (generate with: `openssl rand -hex 32`)
- Store sensitive data in secrets manager (AWS Secrets, Azure Key Vault)

---

## 🗄️ **Step 2: Database Setup**

### **Option A: Using Existing Database**

If you already have production database with `usaha_llm` view:

```bash
# Test connection
psql "postgresql://user:password@host:5432/dbname" -c "SELECT COUNT(*) FROM usaha_llm;"
```

### **Option B: Fresh Database Setup**

```bash
# 1. Create database
createdb geotags_production

# 2. Run migrations (if you have them)
# Or create tables manually

# 3. Create usaha_llm view
psql geotags_production < db/usaha_llm.sql

# 4. Verify
psql geotags_production -c "SELECT COUNT(*) FROM usaha_llm;"
```

---

## 🐳 **Step 3: Ollama Setup**

Ensure Ollama is running with your model:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull model if needed
ollama pull llama3.2

# Test
ollama run llama3.2 "Hello"
```

**Production Tips:**

- Run Ollama on separate server for better performance
- Update `OLLAMA_BASE_URL` if remote: `http://ollama-server:11434`
- Consider GPU server for faster inference

---

## 📦 **Step 4: Install Dependencies**

```bash
cd /path/to/capstone-ai2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# Or: venv\Scripts\activate  # Windows

# Install production dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, uvicorn, sentence_transformers; print('OK')"
```

---

## 🚀 **Step 5: Run with Production Settings**

### **Option A: Direct Uvicorn (Testing)**

```bash
# Production mode (NO --reload!)
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info
```

### **Option B: Systemd Service (Recommended)**

Create `/etc/systemd/system/geotags-chatbot.service`:

```ini
[Unit]
Description=Geotags Chatbot Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/capstone-ai2
Environment="PATH=/var/www/capstone-ai2/venv/bin"
ExecStart=/var/www/capstone-ai2/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 5000 \
  --workers 4 \
  --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable geotags-chatbot
sudo systemctl start geotags-chatbot
sudo systemctl status geotags-chatbot
```

### **Option C: Supervisor (Alternative)**

Create `/etc/supervisor/conf.d/geotags-chatbot.conf`:

```ini
[program:geotags-chatbot]
directory=/var/www/capstone-ai2
command=/var/www/capstone-ai2/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5000 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/geotags-chatbot.err.log
stdout_logfile=/var/log/geotags-chatbot.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start geotags-chatbot
```

---

## 🔒 **Step 6: Nginx Reverse Proxy (HTTPS)**

Create `/etc/nginx/sites-available/geotags-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to FastAPI
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeout for LLM responses
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
    }

    # Admin endpoints (optional authentication)
    location /admin/ {
        proxy_pass http://localhost:5000;
        # Add basic auth or IP restriction
        # auth_basic "Admin Area";
        # auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/geotags-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Get SSL Certificate (Let's Encrypt):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## ✅ **Step 7: Verification**

### **1. Health Check**

```bash
# Test API
curl https://your-domain.com/api/health

# Test chat endpoint
curl -X POST https://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Test query"}'
```

### **2. Check Logs**

```bash
# Systemd
sudo journalctl -u geotags-chatbot -f

# Supervisor
tail -f /var/log/geotags-chatbot.out.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **3. Monitor RAG Performance**

```bash
# Check sync stats
curl https://your-domain.com/admin/sync-stats

# Expected:
# {
#   "total_indexed_documents": 1000,
#   "last_sync": "2025-12-18T04:00:00",
#   ...
# }
```

---

## 📊 **Step 8: Performance Optimization**

### **1. Uvicorn Workers**

```bash
# Calculate optimal workers: 2-4 × CPU cores
nproc  # Check CPU cores

# Set workers (in systemd service)
--workers 4  # For 2-4 core server
```

### **2. Database Connection Pooling**

Already configured in `database.py`:

- min_size: 10
- max_size: 20

Monitor with:

```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'geotags_db';
```

### **3. Caching (Optional)**

Add Redis for caching frequent queries:

```python
# In app/chatbot_service.py
import redis

cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def process_query(query):
    # Check cache
    cached = cache.get(f"query:{query}")
    if cached:
        return json.loads(cached)

    # Process and cache
    result = await _process_query(query)
    cache.setex(f"query:{query}", 3600, json.dumps(result))  # 1 hour
    return result
```

---

## 🔐 **Security Best Practices**

### **1. JWT Token Management**

```bash
# Generate strong secret
openssl rand -hex 32

# Rotate secrets periodically (quarterly)
# Update JWT_SECRET_KEY in .env
# Restart service
```

### **2. Rate Limiting**

Add to Nginx config:

```nginx
# Limit requests per IP
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/chat {
    limit_req zone=api_limit burst=20 nodelay;
    # ... rest of config
}
```

### **3. Firewall**

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Block port 5000 (only accessible via Nginx)
sudo ufw deny 5000/tcp
```

### **4. Database Security**

- Use separate database user with limited permissions
- Enable SSL for database connections
- Regular backups

```sql
-- Create limited user
CREATE USER chatbot_app WITH PASSWORD 'strong_password';
GRANT SELECT ON usaha_llm TO chatbot_app;
```

---

## 📈 **Monitoring & Logging**

### **1. Application Logs**

Configure structured logging in `app/main.py`:

```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/geotags-chatbot/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### **2. Monitoring Stack (Optional)**

**Prometheus + Grafana:**

```python
# Install prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator

# In app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### **3. Alerts**

Set up alerts for:

- High error rate
- Slow response times (>10s)
- Database connection failures
- High memory usage

---

## 🔄 **Maintenance**

### **Daily Tasks**

```bash
# Check service status
sudo systemctl status geotags-chatbot

# Check disk space
df -h

# Check logs for errors
sudo journalctl -u geotags-chatbot --since "1 hour ago" | grep ERROR
```

### **Weekly Tasks**

```bash
# Rotate logs
sudo logrotate /etc/logrotate.d/geotags-chatbot

# Check database size
psql -c "SELECT pg_size_pretty(pg_database_size('geotags_db'));"

# Update dependencies
pip list --outdated
```

### **Monthly Tasks**

```bash
# Security updates
sudo apt update && sudo apt upgrade

# Renew SSL certificate (auto with Let's Encrypt)
sudo certbot renew --dry-run

# Database vacuum
psql geotags_db -c "VACUUM ANALYZE;"
```

---

## 🆘 **Troubleshooting**

### **Service Won't Start**

```bash
# Check service status
sudo systemctl status geotags-chatbot

# Check logs
sudo journalctl -u geotags-chatbot -n 100

# Common issues:
# - Wrong Python path
# - Missing .env file
# - Database connection failed
# - Port already in use
```

### **503 Service Unavailable**

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart service
sudo systemctl restart geotags-chatbot
```

### **Slow Responses**

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Monitor resources
htop

# Check database queries
# In psql:
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

---

## 📋 **Deployment Checklist**

- [ ] `.env` configured for production
- [ ] `EVALUATION_MODE=false` set
- [ ] Database connection tested
- [ ] Ollama running and accessible
- [ ] Dependencies installed in venv
- [ ] Service manager configured (systemd/supervisor)
- [ ] Nginx reverse proxy setup
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Logs directory created with proper permissions
- [ ] Health check endpoint working
- [ ] RAG indexing successful
- [ ] Chat endpoint tested
- [ ] Monitoring setup (optional)
- [ ] Backup strategy defined

---

## 🎯 **Quick Deploy Commands**

```bash
# 1. Clone and setup
git clone <repo>
cd capstone-ai2
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
nano .env  # Edit configuration

# 3. Test locally
uvicorn app.main:app --host 0.0.0.0 --port 5000

# 4. Setup systemd
sudo cp deployment/geotags-chatbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable geotags-chatbot
sudo systemctl start geotags-chatbot

# 5. Setup Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/geotags-chatbot
sudo ln -s /etc/nginx/sites-available/geotags-chatbot /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx

# 6. Verify
curl https://your-domain.com/api/health
```

---

**Last Updated:** 2025-12-18  
**Version:** 1.0  
**Environment:** Production
