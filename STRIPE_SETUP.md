# 💳 Stripe Setup-Anleitung

## Schritt 1: Stripe Account erstellen (5 Minuten)

1. **Gehe zu:** https://dashboard.stripe.com/register
2. **Registriere dich** mit Email
3. **Verifiziere Email**
4. **Überspringen** erstmal "Business Details" (kannst später ausfüllen)

---

## Schritt 2: API Keys holen (2 Minuten)

1. **Gehe zu:** https://dashboard.stripe.com/test/apikeys
2. **Kopiere:**
   - **Publishable Key** (beginnt mit `pk_test_...`)
   - **Secret Key** (beginnt mit `sk_test_...`) - GEHEIM!

3. **Füge in `.env` ein:**
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_... (kommt später)
```

4. **Frontend `.env`:**
```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## Schritt 3: Produkte & Preise erstellen (5 Minuten)

### Option A: Über Dashboard (Einfach)

1. **Gehe zu:** https://dashboard.stripe.com/test/products
2. **Klicke:** "Add product"

#### Product 1: Free Tier
- **Name:** CryptoGuard Free
- **Description:** 10 analyses per day
- **Pricing:**
  - Type: Recurring
  - Price: $0
  - Billing period: Monthly
- **Klicke:** Save
- **Kopiere:** Price ID (beginnt mit `price_...`)

#### Product 2: Pro Tier
- **Name:** CryptoGuard Pro
- **Description:** Unlimited analyses + AI reports
- **Pricing:**
  - Type: Recurring
  - Price: $29
  - Billing period: Monthly
- **Add free trial:** 7 days (optional)
- **Klicke:** Save
- **Kopiere:** Price ID

#### Product 3: Enterprise
- **Name:** CryptoGuard Enterprise
- **Description:** White-label + Custom integration
- **Pricing:**
  - Type: Custom (handled manually)

### Option B: Über Stripe CLI (Fortgeschritten)

```bash
# Installiere Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Erstelle Pro Product & Price
stripe products create \
  --name="CryptoGuard Pro" \
  --description="Unlimited wallet analyses with AI-powered reports"

stripe prices create \
  --product=prod_... \
  --unit-amount=2900 \
  --currency=usd \
  --recurring[interval]=month
```

---

## Schritt 4: Webhooks einrichten (3 Minuten)

**Warum?** Um zu wissen, wenn jemand bezahlt/kündigt.

1. **Gehe zu:** https://dashboard.stripe.com/test/webhooks
2. **Klicke:** "Add endpoint"
3. **Endpoint URL:**
   - Local: `https://your-domain.railway.app/api/stripe/webhook`
   - Später: `https://cryptoguard.io/api/stripe/webhook`
4. **Events auswählen:**
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
5. **Kopiere:** Webhook signing secret (`whsec_...`)
6. **Füge in `.env`:** `STRIPE_WEBHOOK_SECRET=whsec_...`

---

## Schritt 5: Test-Kreditkarten (für Testing)

**Stripe Test Cards:**
- **Success:** `4242 4242 4242 4242`
- **Declined:** `4000 0000 0000 0002`
- **3D Secure:** `4000 0025 0000 3155`

**Weitere Infos:**
- CVV: Beliebig (z.B. `123`)
- Ablaufdatum: Beliebig in Zukunft (z.B. `12/34`)
- ZIP: Beliebig (z.B. `12345`)

---

## Schritt 6: Von Test zu Live Mode wechseln

**WICHTIG:** Erst wechseln, wenn du echte Kunden hast!

1. **Toggle** oben rechts: "Test mode" → "Live mode"
2. **Neue API Keys** kopieren (live keys!)
3. **Business Details** ausfüllen (Pflicht für Auszahlungen)
4. **Bank Account** hinzufügen
5. **Neue Webhooks** für Live Mode erstellen

---

## Kosten

**Stripe Gebühren:**
- **2.9% + $0.30** pro erfolgreicher Zahlung
- **Keine monatlichen Gebühren**
- **Keine Setup-Gebühren**

**Beispiel:**
- Kunde zahlt $29
- Stripe behält: $29 × 0.029 + $0.30 = **$1.14**
- Du bekommst: **$27.86**

---

## Support & Docs

- **Dashboard:** https://dashboard.stripe.com
- **Docs:** https://stripe.com/docs
- **Support:** https://support.stripe.com

---

## Nächste Schritte

Nach Setup:
1. ✅ API Keys in `.env` eintragen
2. ✅ Price IDs notieren
3. ✅ Backend Stripe Integration testen
4. ✅ Frontend Checkout testen
5. ✅ Webhooks testen

**Ready!** 🚀
