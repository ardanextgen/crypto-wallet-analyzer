# 🚀 Deployment-Anleitung - CryptoGuard

## Schnell-Deployment (15 Minuten)

### Option A: Vercel + Railway (EMPFOHLEN)

---

## Teil 1: Backend auf Railway deployen

### Schritt 1: Railway-Account erstellen

1. Gehe zu https://railway.app
2. Klicke "Login with GitHub"
3. Autorisiere Railway

### Schritt 2: Backend deployen

1. **New Project** klicken
2. **Deploy from GitHub repo** wählen
3. Repository auswählen: `crypto-wallet-analyzer`
4. Railway erkennt automatisch Python

### Schritt 3: Environment Variables setzen

In Railway Dashboard → Variables:

```env
ETHERSCAN_API_KEY=5CJPIAQ2FFDJA22ARFHX5HHN1JVS7WK5BD
PORT=8000
ANTHROPIC_API_KEY=sk-... (optional)
```

### Schritt 4: Domain notieren

Nach Deployment:
- Railway generiert URL: `https://crypto-wallet-analyzer-production.up.railway.app`
- **Diese URL kopieren!** (brauchst du für Frontend)

✅ **Backend ist live!**

Test: `https://deine-url.railway.app/health`

---

## Teil 2: Frontend auf Vercel deployen

### Schritt 1: Vercel-Account erstellen

1. Gehe zu https://vercel.com
2. "Sign up with GitHub"
3. Autorisiere Vercel

### Schritt 2: Environment Variable setzen

**WICHTIG:** Bevor du deployest!

1. Öffne `.env.production` im `frontend/` Ordner
2. Ersetze die URL:

```env
VITE_API_URL=https://deine-railway-url.railway.app
```

(Nutze die URL von Railway Schritt 4!)

### Schritt 3: Frontend deployen

#### Option A: Vercel CLI (Terminal)

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

Bei Fragen:
- Framework: **Vite**
- Build Command: `npm run build`
- Output Directory: `dist`

#### Option B: Vercel Dashboard (Browser)

1. Gehe zu https://vercel.com/new
2. Import Git Repository
3. Wähle `crypto-wallet-analyzer`
4. **Root Directory**: `frontend`
5. Framework Preset: **Vite**
6. Environment Variables:
   - Key: `VITE_API_URL`
   - Value: `https://deine-railway-url.railway.app`
7. **Deploy** klicken

### Schritt 4: Domain notieren

Vercel generiert URL: `https://crypto-wallet-analyzer.vercel.app`

✅ **Frontend ist live!**

---

## Teil 3: CORS aktivieren (wichtig!)

Dein Backend muss das Frontend erlauben!

### In Railway:

1. Gehe zu deinem Backend-Projekt
2. Variables → Add Variable:

```env
ALLOWED_ORIGINS=https://crypto-wallet-analyzer.vercel.app
```

3. Backend wird automatisch neu deployed

---

## 🎉 Fertig!

Deine App ist jetzt live:

- **Frontend**: https://crypto-wallet-analyzer.vercel.app
- **Backend API**: https://crypto-wallet-analyzer-production.up.railway.app
- **API Docs**: https://deine-backend-url.railway.app/docs

---

## Alternative: Render.com (Alles in einem)

### Einfacher aber langsamer:

1. Gehe zu https://render.com
2. **New +** → **Web Service**
3. Verbinde GitHub Repo

**Backend:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn src.api.server:app --host 0.0.0.0 --port $PORT`
- Environment Variables: (wie bei Railway)

**Frontend:**
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Environment Variables: `VITE_API_URL`

---

## Kosten-Übersicht

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Vercel** | ✅ Kostenlos | 100 GB Bandwidth |
| **Railway** | $5 Credit | ~500h Runtime |
| **Render** | ✅ Kostenlos | Schläft nach 15min Inaktivität |

**Empfehlung:** Vercel + Railway für bestes Performance/Preis-Verhältnis

---

## Custom Domain (optional)

### Vercel:
1. Domains → Add Domain
2. Folge DNS-Anweisungen

### Railway:
1. Settings → Public Networking
2. Custom Domain → Add
3. DNS konfigurieren

---

## Monitoring & Logs

### Railway Logs:
```bash
# Echtzeit-Logs
railway logs --tail
```

### Vercel Logs:
Dashboard → Deployments → View Logs

---

## Troubleshooting

### Problem: CORS-Fehler im Browser

**Lösung:**
```python
# In src/api/server.py prüfen:
allow_origins=["*"]  # Für Testing
# In Production:
allow_origins=["https://deine-frontend-url.vercel.app"]
```

### Problem: Railway "Application Error"

**Lösung:**
- Checke Environment Variables (ETHERSCAN_API_KEY gesetzt?)
- Logs prüfen: `railway logs`

### Problem: Frontend zeigt "Failed to fetch"

**Lösung:**
- API-URL in `.env.production` korrekt?
- Backend läuft? (Test `/health` endpoint)

---

## Next Steps

1. ✅ Deployen
2. ⚙️ Custom Domain einrichten
3. 💳 Stripe Payment integrieren
4. 📊 Analytics hinzufügen (Google Analytics)
5. 🚀 Product Hunt Launch

**Good luck! 🎉**
