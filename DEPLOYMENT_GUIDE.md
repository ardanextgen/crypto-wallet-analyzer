# 🚀 DEPLOYMENT GUIDE - CryptoGuard Production

## ✅ STATUS AKTUELL

- ✅ Backend-Code ready
- ✅ Frontend-Code ready & buildet erfolgreich  
- ✅ PostgreSQL-Driver in requirements.txt
- ✅ Database Models ready
- ⏳ Warte auf API-Keys (holst du gerade)
- ⏳ PostgreSQL auf Railway (3 Klicks von dir)

---

## 🎯 DEPLOYMENT STEPS

### 1️⃣ RAILWAY - Backend (5 Min)

**A) PostgreSQL hinzufügen (3 Klicks):**
```
1. https://railway.app → Dein Projekt
2. "+ New" → "Database" → "Add PostgreSQL"  
3. Fertig! DATABASE_URL wird automatisch gesetzt ✅
```

**B) Environment Variables setzen:**
Gehe zu Variables Tab, copy-paste diese (ersetze Platzhalter):

```bash
ETHERSCAN_API_KEY=5CJPIAQ2FFDJA22ARFHX5HHN1JVS7WK5BD
ANTHROPIC_API_KEY=sk-ant-DEIN_KEY_HIER
STRIPE_SECRET_KEY=sk_test_DEIN_KEY_HIER  
STRIPE_WEBHOOK_SECRET=whsec_DEIN_KEY_HIER
CLAUDE_MODEL=claude-3-haiku-20240307
API_PORT=8000
DEBUG=false
ENVIRONMENT=production
```

**C) Redeploy:**
- Click "Redeploy" → Warte 2 Min → Check Health

---

### 2️⃣ VERCEL - Frontend (2 Min)

**Im Terminal:**
```bash
cd frontend
npx vercel --prod
```
- Login → Follow prompts
- Copy Vercel-URL ✅

---

### 3️⃣ STRIPE WEBHOOK (2 Min)

1. https://dashboard.stripe.com/test/webhooks
2. "Add endpoint"
3. URL: `https://web-production-e32f3.up.railway.app/stripe/webhook`
4. Events: `checkout.session.completed`, `customer.subscription.*`
5. Copy Webhook Secret → Railway Variables → Redeploy

---

## 🧪 FINAL TEST

**Backend Health:**
```bash
curl https://web-production-e32f3.up.railway.app/health
```
Sollte alle Services "ok" zeigen ✅

**Frontend:**
- Öffne Vercel-URL
- Teste Wallet: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- Registriere User → Login → Dashboard ✅
- Pro Upgrade → Test Card: `4242 4242 4242 4242` ✅

---

## 🔑 API KEYS CHECKLIST

- ✅ ETHERSCAN (haben wir)
- ⏳ ANTHROPIC (https://console.anthropic.com/settings/keys)
- ⏳ STRIPE SECRET (https://dashboard.stripe.com/test/apikeys)
- ⏳ STRIPE WEBHOOK (nach Step 3)

