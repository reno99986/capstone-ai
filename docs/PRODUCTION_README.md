# Production Deployment - Quick Reference

**CRITICAL CHANGES for Production:**

## 🔴 Must Change

### 1. Environment Variables (.env)

```bash
# TURN OFF EVALUATION MODE!
EVALUATION_MODE=false

# Strong JWT secret
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Production database
DATABASE_URL=postgresql://user:pass@prod-host:5432/dbname
```

### 2. Run Command

```bash
# ❌ Development (with --reload)
uvicorn app.main:app --reload

# ✅ Production (no --reload, multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 5000 --workers 4
```

### 3. HTTPS Required

- Use Nginx reverse proxy
- Install SSL certificate (Let's Encrypt)
- Redirect HTTP → HTTPS

## ⚠️ Security Checklist

- [ ] `EVALUATION_MODE=false`
- [ ] Strong `JWT_SECRET_KEY`
- [ ] HTTPS enabled
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] `.env` not committed to git

## 📝 See Full Guide

Complete instructions: `docs/PRODUCTION_DEPLOYMENT.md`
