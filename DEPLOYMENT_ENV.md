# 🔐 Environment Variables for Deployment

## 🎯 Backend Environment Variables (Railway)

Add these in Railway Dashboard → Your Service → Variables tab:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# OpenRouter AI API Key
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Session Secret (CHANGE THIS IN PRODUCTION!)
SESSION_SECRET=your-super-secret-random-string-change-this-in-production

# Google OAuth Redirect URI (Update after getting Railway URL)
GOOGLE_REDIRECT_URI=https://your-app-name.railway.app/auth/google/callback

# Port (Railway sets this automatically, but you can specify)
PORT=8000

# Database URL (Railway PostgreSQL sets this automatically)
# DATABASE_URL=postgresql://user:password@host:port/database
# Don't set this manually - Railway will provide it when you add PostgreSQL
```

---

## 📝 Important Notes

### 1. **GOOGLE_REDIRECT_URI** - Two-Step Process:
   
   **Step 1:** Initial deployment
   ```env
   GOOGLE_REDIRECT_URI=https://temporary-url.railway.app/auth/google/callback
   ```
   
   **Step 2:** After Railway generates your domain, update to:
   ```env
   GOOGLE_REDIRECT_URI=https://your-actual-app.railway.app/auth/google/callback
   ```

### 2. **SESSION_SECRET** - Generate a Strong Secret:
   
   Use one of these methods to generate a secure secret:
   
   ```bash
   # Method 1: Using OpenSSL
   openssl rand -hex 32
   
   # Method 2: Using Python
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Method 3: Using Node.js
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
   ```
   
   Example output: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

### 3. **DATABASE_URL** - Automatic Setup:
   
   - Railway automatically provides this when you add PostgreSQL
   - Format: `postgresql://user:password@host:port/database`
   - **DO NOT** set this manually
   - The app auto-detects PostgreSQL and uses it in production

---

## 🌐 Frontend Configuration

The frontend is bundled with the backend in this setup (served from the same Railway service).

### Frontend API Base URL:

The frontend automatically uses the same domain as the backend since they're deployed together.

In `src/lib/api.ts`, update for production:

```typescript
// For local development
const API_BASE = "http://localhost:8000";

// For production (Railway), use relative URLs or same domain
// const API_BASE = ""; // Empty string uses same domain
// OR
// const API_BASE = window.location.origin;
```

**Recommended approach:** Use environment variable:

```typescript
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
```

Then in Railway, add:
```env
VITE_API_BASE=https://your-app.railway.app
```

---

## 🔄 Google Cloud Console Setup

After deploying to Railway, update your Google OAuth settings:

### 1. Go to: https://console.cloud.google.com/

### 2. Navigate to: **APIs & Services** → **Credentials**

### 3. Click on your OAuth 2.0 Client ID

### 4. Add **Authorized JavaScript origins:**
```
https://your-app.railway.app
```

### 5. Add **Authorized redirect URIs:**
```
https://your-app.railway.app/auth/google/callback
```

### 6. Click **Save**

---

## 📋 Quick Copy-Paste for Railway

### Initial Deployment (Before you have Railway URL):

```env
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
OPENROUTER_API_KEY=your-openrouter-api-key-here
SESSION_SECRET=CHANGE-THIS-TO-A-RANDOM-SECRET-KEY
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
PORT=8000
```

### After Getting Railway URL:

Update only this variable:
```env
GOOGLE_REDIRECT_URI=https://your-actual-railway-url.railway.app/auth/google/callback
```

---

## ✅ Deployment Checklist

- [ ] Copy all environment variables to Railway
- [ ] Generate a strong `SESSION_SECRET`
- [ ] Add PostgreSQL database in Railway
- [ ] Deploy and get Railway URL
- [ ] Update `GOOGLE_REDIRECT_URI` with actual Railway URL
- [ ] Update Google Cloud Console with Railway URL
- [ ] Test Google OAuth login
- [ ] Verify all features work

---

## 🔒 Security Best Practices

### ⚠️ **NEVER commit these to Git:**
- `.env` files
- API keys
- Client secrets
- Session secrets
- Database credentials

### ✅ **DO:**
- Use Railway's environment variables feature
- Generate unique `SESSION_SECRET` for production
- Rotate secrets periodically
- Use different credentials for dev/staging/prod
- Keep `.env` in `.gitignore`

---

## 🆘 Troubleshooting

### Issue: "OAuth redirect_uri_mismatch"
**Solution:** 
- Check `GOOGLE_REDIRECT_URI` matches exactly in Railway
- Verify Google Cloud Console has the correct redirect URI
- No trailing slashes, exact match required

### Issue: "Database connection failed"
**Solution:**
- Ensure PostgreSQL is added in Railway
- Check `DATABASE_URL` is automatically set
- View logs in Railway dashboard

### Issue: "Session/Cookie not working"
**Solution:**
- Check `SESSION_SECRET` is set
- Verify CORS settings in `backend/main.py`
- Ensure cookies are set with correct domain

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Google OAuth Docs: https://developers.google.com/identity/protocols/oauth2
- OpenRouter Docs: https://openrouter.ai/docs

---

**Ready to deploy!** 🚀
