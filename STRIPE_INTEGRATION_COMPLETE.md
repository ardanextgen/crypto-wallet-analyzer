# ✅ Stripe Integration - Complete Setup Guide

## 🎉 Was wurde implementiert?

### Backend (Python/FastAPI)
- ✅ `src/api/stripe_routes.py` - Alle Payment Endpoints
- ✅ Integration in `src/api/server.py`
- ✅ Checkout Session Erstellung
- ✅ Customer Portal Access
- ✅ Webhook Handler für alle Events
- ✅ Environment Variables Setup

### Frontend (React)
- ✅ `src/services/stripe.js` - Stripe Checkout Service
- ✅ `src/pages/Success.jsx` - Erfolgs-Seite nach Payment
- ✅ `src/pages/Cancel.jsx` - Abbruch-Seite
- ✅ React Router Integration
- ✅ Pricing Button Integration
- ✅ Environment Variables Setup

---

## 🚀 Nächste Schritte (Setup)

### Schritt 1: Stripe Account erstellen (5 Minuten)

Folge der Anleitung in **STRIPE_SETUP.md** Schritt 1-2:
- Account erstellen
- API Keys kopieren

### Schritt 2: Environment Variables einrichten

#### Backend `.env`
```bash
cd /Users/Arda1/Desktop/crypto-wallet-analyzer
cp .env.example .env
```

Füge in `.env` hinzu:
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # Kommt später
```

#### Frontend `.env`
```bash
cd frontend
cp .env.example .env
```

Füge in `frontend/.env` hinzu:
```env
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_STRIPE_PRO_PRICE_ID=price_...  # Kommt gleich
```

### Schritt 3: Produkt & Price in Stripe erstellen (5 Minuten)

**Option A: Über Dashboard (Empfohlen für Anfänger)**

1. Gehe zu: https://dashboard.stripe.com/test/products
2. Klicke: "Add product"

**Product Details:**
- Name: `CryptoGuard Pro`
- Description: `Unlimited wallet analyses with AI-powered reports`

**Pricing:**
- Type: `Recurring`
- Price: `$29.00`
- Currency: `USD`
- Billing period: `Monthly`
- Free trial: `7 days` (optional)

3. Klicke: "Save product"
4. **Kopiere die Price ID** (beginnt mit `price_...`)
5. Füge in `frontend/.env` ein:
   ```env
   VITE_STRIPE_PRO_PRICE_ID=price_1QoR...
   ```

**Option B: Über Stripe CLI (Fortgeschritten)**

```bash
# Installiere Stripe CLI (macOS)
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Erstelle Produkt
stripe products create \
  --name="CryptoGuard Pro" \
  --description="Unlimited wallet analyses with AI-powered reports"

# Erstelle Price (ersetze prod_... mit deiner Product ID)
stripe prices create \
  --product=prod_... \
  --unit-amount=2900 \
  --currency=usd \
  --recurring[interval]=month

# Kopiere die Price ID und füge in frontend/.env ein
```

### Schritt 4: Webhooks einrichten (3 Minuten)

**Warum Webhooks?**
- Stripe benachrichtigt uns über Zahlungen, Kündigungen, etc.
- WICHTIG für Subscription-Management!

**Setup:**

1. **Gehe zu:** https://dashboard.stripe.com/test/webhooks
2. **Klicke:** "Add endpoint"
3. **Endpoint URL:**
   - Local Testing: `https://your-ngrok-url.ngrok.io/api/stripe/webhook`
   - Production: `https://your-domain.railway.app/api/stripe/webhook`

4. **Events auswählen:**
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`

5. **Klicke:** "Add endpoint"
6. **Kopiere:** Webhook signing secret (`whsec_...`)
7. **Füge in `.env`:**
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

---

## 🧪 Testing (Local)

### 1. Backend starten

```bash
cd /Users/Arda1/Desktop/crypto-wallet-analyzer

# Installiere Stripe SDK (falls noch nicht)
pip install stripe

# Starte Server
uvicorn src.api.server:app --reload --port 8000
```

**Überprüfe:**
- ✅ Server läuft: http://localhost:8000
- ✅ Swagger Docs: http://localhost:8000/docs
- ✅ Stripe Endpoints sichtbar:
  - `POST /api/stripe/create-checkout-session`
  - `POST /api/stripe/webhook`
  - `GET /api/stripe/config`

### 2. Frontend starten

```bash
cd frontend
npm run dev
```

**Überprüfe:**
- ✅ Frontend läuft: http://localhost:5173
- ✅ Pricing Section sichtbar
- ✅ "Start Free Trial" Button vorhanden

### 3. Teste Checkout Flow

1. **Öffne:** http://localhost:5173
2. **Scrolle zu:** Pricing Section
3. **Klicke:** "Start Free Trial" Button (Pro Plan)
4. **Expected:**
   - Redirect zu Stripe Checkout
   - Test-Zahlungs-Formular erscheint

5. **Fülle aus mit Stripe Test Card:**
   - Card Number: `4242 4242 4242 4242`
   - Expiry: Beliebig in Zukunft (z.B. `12/34`)
   - CVC: Beliebig (z.B. `123`)
   - ZIP: Beliebig (z.B. `12345`)
   - Email: Deine Test-Email

6. **Klicke:** "Subscribe"
7. **Expected:**
   - Redirect zu `/success`
   - Erfolgs-Seite mit Konfetti-Animation
   - Session ID angezeigt

### 4. Teste Cancel Flow

1. **Wiederhole Schritte 1-4**
2. **Klicke:** "Back" Button in Stripe Checkout
3. **Expected:**
   - Redirect zu `/cancel`
   - Abbruch-Seite mit Retry-Option

---

## 🔒 Webhook Testing (Local)

**Problem:** Stripe kann keine Webhooks an `localhost` senden!

**Lösung:** Verwende ngrok oder Stripe CLI

### Option A: Stripe CLI (Empfohlen)

```bash
# Forwarde Webhooks zu localhost
stripe listen --forward-to localhost:8000/api/stripe/webhook

# Terminal zeigt webhook secret (whsec_...)
# Kopiere diesen in deine .env:
# STRIPE_WEBHOOK_SECRET=whsec_...

# Teste Webhook manuell
stripe trigger checkout.session.completed
```

### Option B: ngrok

```bash
# Installiere ngrok
brew install ngrok

# Starte ngrok
ngrok http 8000

# Kopiere HTTPS URL (z.B. https://abc123.ngrok.io)
# Füge in Stripe Dashboard Webhook Endpoint hinzu:
# https://abc123.ngrok.io/api/stripe/webhook
```

**Teste Webhook:**
1. Führe Checkout durch
2. Überprüfe Backend Logs:
   ```
   INFO: Received webhook: checkout.session.completed
   ✅ New subscription: sub_... for test@example.com
   ```

---

## 🌐 Production Deployment

### 1. Railway Backend Update

```bash
cd /Users/Arda1/Desktop/crypto-wallet-analyzer

# Füge Stripe Environment Variables in Railway hinzu
# Dashboard: https://railway.app/project/...

# Variables:
STRIPE_SECRET_KEY=sk_test_...  # Später sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 2. Vercel Frontend Update

```bash
cd frontend

# Füge Environment Variables in Vercel hinzu
# Dashboard: https://vercel.com/...

# Variables:
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_STRIPE_PRO_PRICE_ID=price_...
```

### 3. Stripe Webhook Endpoint (Production)

1. **Gehe zu:** https://dashboard.stripe.com/test/webhooks
2. **Füge neuen Endpoint hinzu:**
   - URL: `https://web-production-e32f3.up.railway.app/api/stripe/webhook`
   - Events: (gleiche wie oben)
3. **Kopiere:** Webhook Secret
4. **Update** Railway Environment Variable: `STRIPE_WEBHOOK_SECRET`

---

## 📊 Monitoring & Testing

### Test-Szenarien

✅ **Erfolgreiche Zahlung:**
- Card: `4242 4242 4242 4242`
- Expected: Redirect zu `/success`, Webhook `checkout.session.completed`

✅ **Abgelehnte Karte:**
- Card: `4000 0000 0000 0002`
- Expected: Error in Stripe Checkout

✅ **3D Secure:**
- Card: `4000 0025 0000 3155`
- Expected: 3D Secure Authentication Popup

✅ **Checkout Abbruch:**
- Expected: Redirect zu `/cancel`

### Stripe Dashboard Monitoring

**Live-Modus:** https://dashboard.stripe.com/test/payments

Überprüfe:
- ✅ Payments erfolgreich
- ✅ Subscriptions erstellt
- ✅ Webhooks delivered
- ✅ Keine Fehler in Logs

---

## 🔄 User Flow Diagram

```
User klickt "Start Free Trial"
          ↓
Frontend: startCheckout('price_...')
          ↓
Backend: POST /api/stripe/create-checkout-session
          ↓
Stripe: Erstellt Checkout Session
          ↓
User: Redirect zu Stripe Checkout
          ↓
User: Füllt Payment Details aus
          ↓
        ╔════════╗
        ║ Cancel ║ → /cancel
        ╚════════╝
          ↓
        ╔════════╗
        ║  Pay   ║
        ╚════════╝
          ↓
Stripe: Zahlung erfolgreich
          ↓
Stripe Webhook → Backend /api/stripe/webhook
          ↓
Backend: handle_checkout_completed()
  - User in DB speichern
  - Pro-Zugang aktivieren
  - Welcome-Email senden
          ↓
User: Redirect zu /success
```

---

## 🛠️ Troubleshooting

### Problem: "Stripe not configured yet!" Alert

**Ursache:** VITE_STRIPE_PRO_PRICE_ID nicht gesetzt

**Lösung:**
```bash
# Überprüfe frontend/.env
cat frontend/.env | grep VITE_STRIPE_PRO_PRICE_ID

# Falls leer, füge Price ID hinzu
echo "VITE_STRIPE_PRO_PRICE_ID=price_..." >> frontend/.env

# Restart Frontend
npm run dev
```

### Problem: Checkout Session Error 400

**Ursache:** Backend kann Stripe nicht erreichen oder API Key falsch

**Lösung:**
```bash
# Überprüfe Backend .env
cat .env | grep STRIPE_SECRET_KEY

# Teste Stripe Connection
python -c "import stripe; stripe.api_key='sk_test_...'; print(stripe.Product.list())"
```

### Problem: Webhook 400 Invalid Signature

**Ursache:** STRIPE_WEBHOOK_SECRET falsch oder fehlt

**Lösung:**
```bash
# Überprüfe .env
cat .env | grep STRIPE_WEBHOOK_SECRET

# Verwende Stripe CLI für lokales Testing
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

### Problem: Nach Zahlung kein Redirect

**Ursache:** Success/Cancel URLs falsch konfiguriert

**Lösung:**
```javascript
// In stripe.js überprüfen:
success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`
cancel_url: `${window.location.origin}/cancel`
```

---

## 📝 Next Steps (User Management)

**Aktuell implementiert:**
- ✅ Checkout Flow
- ✅ Webhook Empfang
- ✅ Success/Cancel Pages

**TODO (für vollständiges Subscription-System):**
1. **User Authentication:**
   - Login/Signup System
   - User Dashboard
   - Session Management

2. **Database Integration:**
   - User Table (email, stripe_customer_id, subscription_status)
   - Webhook → DB Update Logic
   - Pro-Features nur für zahlende User freischalten

3. **Customer Portal:**
   - "Manage Subscription" Button im Dashboard
   - Redirect zu Stripe Customer Portal
   - Erlaubt Kündigung, Zahlungsmethode ändern

4. **Usage Limits:**
   - Free: 10 Analysen/Tag
   - Pro: Unlimited
   - API-Check vor jeder Analyse

---

## 🎯 Summary

**Fertig implementiert:**
- ✅ Backend API (Checkout, Webhooks, Portal)
- ✅ Frontend Integration (Checkout Button, Success/Cancel)
- ✅ Environment Setup Guides
- ✅ Test-Ready mit Stripe Test Cards

**Bereit für:**
- ✅ Local Testing
- ✅ Stripe Dashboard Configuration
- ✅ Production Deployment

**Nächste Schritte:**
1. Stripe Account einrichten
2. API Keys & Price ID konfigurieren
3. Testen mit Test Cards
4. User Authentication implementieren (Task #23)
5. Live schalten!

🚀 **Du bist startklar für Payments!**
