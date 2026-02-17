# 🔍 Krypto-Wallet-Analyse-Tool

Ein vollständiges Python-Tool zur Analyse von Ethereum-Wallets mit **Scam-Risiko-Bewertung** und **AI-generierten Reports**.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Wie funktioniert es?](#-wie-funktioniert-es)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Verwendung](#-verwendung)
  - [CLI (Command-Line)](#cli-command-line)
  - [API (REST)](#api-rest)
- [Architektur](#-architektur)
- [Heuristiken erklärt](#-heuristiken-erklärt)
- [Beispiele](#-beispiele)
- [Kosten](#-kosten)
- [Troubleshooting](#-troubleshooting)
- [Entwicklung](#-entwicklung)

---

## ✨ Features

### 🎯 Risiko-Analyse
- **6 Heuristiken** zur Bewertung von Wallet-Risiken
- **Gewichteter Risiko-Score** (0-100)
- **Automatische Kategorisierung** (low/medium/high)
- **Scam-Datenbank** mit bekannten bösartigen Adressen

### 🤖 AI-Integration
- **Claude AI** generiert verständliche Reports
- **Zusammenfassungen** in natürlicher Sprache
- **Handlungsempfehlungen** basierend auf Risiko-Profil

### 📊 Datenquellen
- **Web3.py**: Direkte Blockchain-Anbindung
- **Etherscan API**: Historische Transaktionen & Token-Daten
- **Echtzeit-Balances**: Aktuelle Wallet-Informationen

### 🚀 Zwei Interfaces
- **CLI**: Kommandozeilen-Tool mit schöner Formatierung
- **REST API**: FastAPI-Server mit Swagger-Docs

---

## 🔧 Wie funktioniert es?

```
┌─────────────────┐
│ Wallet-Adresse  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  1. DATENSAMMLUNG                   │
│  ├─ Etherscan: Transaktionen        │
│  ├─ Etherscan: Token-Holdings       │
│  └─ Web3: Aktuelle Balance          │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  2. RISIKO-ANALYSE (6 Heuristiken)  │
│  ├─ Wallet-Alter                    │
│  ├─ Transaktionsvolumen             │
│  ├─ Token-Konzentration             │
│  ├─ Scam-Interaktionen              │
│  ├─ Mixer-Nutzung                   │
│  └─ Ein-/Ausgangs-Muster            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. SCORE-BERECHNUNG                │
│  Gewichteter Durchschnitt → 0-100   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  4. AI-REPORT (Optional)            │
│  Claude AI erstellt verständlichen  │
│  Report mit Empfehlungen            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Finale Analyse │
│  • Risiko-Score │
│  • Detail-Scores│
│  • AI-Report    │
│  • Warnungen    │
└─────────────────┘
```

---

## 📦 Installation

### Voraussetzungen

- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Git** (optional, für Klonen des Repos)

### Schritt 1: Repository klonen

```bash
git clone https://github.com/yourusername/crypto-wallet-analyzer.git
cd crypto-wallet-analyzer
```

### Schritt 2: Virtual Environment erstellen

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Package installieren (Development Mode)

```bash
pip install -e .
```

**Was macht das?**
- Installiert das Package im "Development Mode"
- Änderungen am Code sind sofort aktiv (kein Re-Install nötig)
- Erstellt den `crypto-analyze` Befehl

---

## ⚙️ Konfiguration

### API-Keys besorgen

#### 1. Etherscan API Key (PFLICHT)

1. Gehe zu [etherscan.io/register](https://etherscan.io/register)
2. Erstelle einen kostenlosen Account
3. Gehe zu [etherscan.io/myapikey](https://etherscan.io/myapikey)
4. Erstelle einen neuen API Key

**Limits (kostenlos):**
- 5 Requests/Sekunde
- 100.000 Requests/Tag

#### 2. Infura/Alchemy Project ID (EMPFOHLEN)

**Option A: Infura**
1. Gehe zu [infura.io/register](https://infura.io/register)
2. Erstelle ein neues Projekt
3. Kopiere die "Project ID"

**Option B: Alchemy**
1. Gehe zu [alchemy.com](https://www.alchemy.com/)
2. Erstelle ein neues "App" für Ethereum Mainnet
3. Kopiere die URL oder API Key

**Limits (kostenlos):**
- 100.000 Requests/Tag (Infura)
- 300M Requests/Monat (Alchemy)

#### 3. Anthropic API Key (FÜR AI-REPORTS)

1. Gehe zu [console.anthropic.com](https://console.anthropic.com/)
2. Erstelle einen Account
3. Gehe zu "API Keys"
4. Erstelle einen neuen API Key

**Kosten:**
- ~$0.003 pro Report (Claude Haiku)
- Prepaid-Modell (Guthaben aufladen)

### .env Datei erstellen

Kopiere die Beispiel-Datei:

```bash
cp .env.example .env
```

Fülle die API-Keys ein:

```env
# .env Datei

# Etherscan API Key (PFLICHT)
ETHERSCAN_API_KEY=your_etherscan_api_key_here

# Infura Project ID (Option A)
INFURA_PROJECT_ID=your_infura_project_id_here

# ODER Alchemy URL (Option B)
# ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/your_api_key_here

# Anthropic API Key (für AI-Reports)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Claude-Modell
CLAUDE_MODEL=claude-3-haiku-20240307

# Optional: API-Server Konfiguration
API_PORT=8000
DEBUG=false
```

---

## 🚀 Verwendung

### CLI (Command-Line)

#### Grundlegende Verwendung

```bash
# Mit Wallet-Adresse als Argument
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Interaktive Eingabe
python -m src.cli.main
```

#### Mit Optionen

```bash
# Ohne AI-Report (schneller, spart Kosten)
python -m src.cli.main 0x123... --no-ai

# Mit JSON-Export
python -m src.cli.main 0x123... --json output.json

# Beides kombiniert
python -m src.cli.main 0x123... --no-ai --json output.json
```

#### Beispiel-Output

```
═══════════════════════════════════════════════════════════════
🔍 KRYPTO-WALLET ANALYSE
═══════════════════════════════════════════════════════════════

📊 Wallet-Informationen
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Feld                ┃ Wert                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Adresse             │ 0xd8dA6BF26964aF9D7eEd9e03E53415D3... │
│ ETH Balance         │ 1.5000 ETH                             │
│ Wallet-Alter        │ 837 Tage (~27 Monate)                  │
│ Transaktionen       │ 234                                    │
│ Token-Holdings      │ 5                                      │
└─────────────────────┴────────────────────────────────────────┘

╭─────────────────────────────────────────────────╮
│ ⚠️  RISIKO-SCORE: 45.0/100                      │
│ Level: MEDIUM                                   │
╰─────────────────────────────────────────────────╯

🎯 Detail-Scores
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┓
┃ Heuristik             ┃ Score ┃ Bewertung┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━┩
│ Wallet-Alter          │  15.0 │ ✅ Gut   │
│ Transaktionsvolumen   │  25.0 │ ✅ Gut   │
│ Token-Konzentration   │  60.0 │ ⚠️  Mittel│
│ Scam-Interaktion      │  80.0 │ 🚨 Hoch  │
│ Mixer-Nutzung         │   0.0 │ ✅ Gut   │
│ Ein-/Ausgangs-Muster  │  20.0 │ ✅ Gut   │
└───────────────────────┴───────┴──────────┘

🤖 AI-Analyse
Diese Wallet zeigt gemischte Signale. Während das Wallet-Alter und
Transaktionsvolumen normal sind, gibt es Interaktionen mit zwei
bekannten Scam-Contracts...

💡 Empfehlungen
  1. Überprüfe die verdächtigen Contract-Interaktionen
  2. Diversifiziere Token-Holdings
  3. Nutze einen Hardware-Wallet für größere Beträge
```

---

### API (REST)

#### Server starten

```bash
# Development (mit Auto-Reload)
uvicorn src.api.server:app --reload --port 8000

# Production
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Swagger-Dokumentation

Öffne im Browser: **http://localhost:8000/docs**

Hier kannst du die API direkt testen!

#### Endpoints

##### 1. Einzelne Wallet analysieren

```bash
# Basic
curl http://localhost:8000/analyze/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Mit Optionen
curl "http://localhost:8000/analyze/0x123...?generate_ai=false&max_transactions=50"
```

**Response:**
```json
{
  "wallet_data": {
    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "eth_balance": "1500000000000000000",
    "total_transactions": 234,
    "wallet_age_days": 837
  },
  "risk_score": {
    "total_score": 45.0,
    "risk_level": "medium",
    "wallet_age_score": 15.0,
    "transaction_volume_score": 25.0,
    "token_concentration_score": 60.0,
    "scam_interaction_score": 80.0,
    "mixer_usage_score": 0.0,
    "inflow_outflow_score": 20.0,
    "flags": [...]
  },
  "ai_report": {
    "summary": "...",
    "recommendations": [...]
  }
}
```

##### 2. Mehrere Wallets analysieren (Batch)

```bash
curl -X POST http://localhost:8000/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
      "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    ],
    "generate_ai_report": false
  }'
```

##### 3. Health Check

```bash
curl http://localhost:8000/health
```

---

## 🏗️ Architektur

### Projekt-Struktur

```
crypto-wallet-analyzer/
│
├── src/                          # Haupt-Quellcode
│   ├── blockchain/               # Blockchain-Interaktion
│   │   ├── web3_client.py       # Web3.py Wrapper
│   │   ├── etherscan_client.py  # Etherscan API Client
│   │   └── data_models.py       # Pydantic Datenmodelle
│   │
│   ├── analysis/                 # Risiko-Analyse
│   │   ├── heuristics.py        # 6 Heuristiken
│   │   ├── risk_engine.py       # Score-Berechnung
│   │   └── scam_lists.py        # Scam-Datenbank-Manager
│   │
│   ├── ai/                       # AI-Integration
│   │   └── report_generator.py  # Claude API Client
│   │
│   ├── api/                      # REST API
│   │   └── server.py            # FastAPI Server
│   │
│   └── cli/                      # Command-Line Interface
│       └── main.py              # CLI Hauptdatei
│
├── data/                         # Daten
│   └── scam_addresses.json      # Bekannte Scam-Adressen
│
├── tests/                        # Unit Tests
│   └── ...
│
├── requirements.txt              # Python Dependencies
├── setup.py                      # Package Setup
├── .env.example                  # Beispiel-Konfiguration
└── README.md                     # Diese Datei
```

### Datenfluss

```
User Input (Wallet-Adresse)
    │
    ├─> Web3Client.get_eth_balance()
    │   └─> Ethereum Node (Infura/Alchemy)
    │
    ├─> EtherscanClient.get_complete_wallet_data()
    │   └─> Etherscan API
    │       ├─> Transaktionen
    │       ├─> Token-Holdings
    │       └─> Internal-TXs
    │
    ├─> RiskEngine.analyze()
    │   ├─> calculate_wallet_age_score()
    │   ├─> calculate_transaction_volume_score()
    │   ├─> calculate_token_concentration_score()
    │   ├─> calculate_scam_interaction_score()
    │   │   └─> ScamListManager (scam_addresses.json)
    │   ├─> calculate_mixer_usage_score()
    │   └─> calculate_inflow_outflow_score()
    │   └─> Weighted Average → Total Score
    │
    └─> AIReportGenerator.generate_report()
        └─> Claude API (Anthropic)
            └─> Natürlichsprachiger Report

Final Output: CompleteAnalysis
```

---

## 📊 Heuristiken erklärt

### 1. Wallet-Alter 🕰️ (Gewicht: 20%)

**Frage:** Wie lange existiert die Wallet schon?

**Logik:**
- 2+ Jahre alt: Score = 0 (sehr vertrauenswürdig)
- 1-2 Jahre: Score = 10 (vertrauenswürdig)
- 6-12 Monate: Score = 20 (ok)
- 3-6 Monate: Score = 40 (etwas verdächtig)
- 1-3 Monate: Score = 60 (verdächtig)
- < 1 Monat: Score = 90 (sehr verdächtig)

**Warum?**
Scammer erstellen oft neue Wallets für jeden Betrug. Langlebige Wallets haben etablierte Reputation.

---

### 2. Transaktionsvolumen 📈 (Gewicht: 15%)

**Frage:** Wie viele Transaktionen hat die Wallet?

**Logik:**
- 0 TXs: Score = 100 (keine Historie)
- < 5 TXs: Score = 80 (sehr wenig)
- 5-50 TXs: Score = 30 (wenig)
- 50-500 TXs: Score = 0 (normal)
- 500-1000 TXs: Score = 30 (viel)
- > 1000 TXs: Score = 60 (sehr viel, möglicherweise Bot)

**Warum?**
Normale User haben moderate Aktivität. Zu wenig kann Scam-Vorbereitung sein, zu viel kann auf Bots hindeuten.

---

### 3. Token-Konzentration 🎯 (Gewicht: 15%)

**Frage:** Ist der Großteil des Vermögens in einem Token?

**Logik:**
- > 90% in einem Token: Score = 100
- > 80%: Score = 80
- > 60%: Score = 50
- > 40%: Score = 20
- < 40%: Score = 0 (gut diversifiziert)

**Warum?**
Scammer halten oft nur den gerade gestohlenen Token. Normale User diversifizieren.

---

### 4. Scam-Interaktion 🚨 (Gewicht: 30% - WICHTIGSTER!)

**Frage:** Hat die Wallet mit bekannten Scam-Adressen interagiert?

**Logik:**
- 0 Interaktionen: Score = 0
- 1 Interaktion: Score = 40
- 2-3 Interaktionen: Score = 70
- 4+ Interaktionen: Score = 100

**Warum?**
Kontakt mit Scams ist das stärkste Warnsignal! Könnte Opfer oder Täter sein.

**Datenquelle:** `data/scam_addresses.json`

---

### 5. Mixer-Nutzung 🌪️ (Gewicht: 10%)

**Frage:** Nutzt die Wallet Privacy-Mixer (z.B. Tornado Cash)?

**Logik:**
- Tornado Cash 100 ETH: Score = 90
- Tornado Cash 10 ETH: Score = 70
- Tornado Cash 1 ETH: Score = 50
- Tornado Cash 0.1 ETH: Score = 40
- Andere Mixer: Score = 60
- Keine Mixer: Score = 0

**Warum?**
Mixer verschleiern Geldflüsse. Oft für Geldwäsche genutzt, aber auch legitime Privacy-Gründe möglich.

---

### 6. Ein-/Ausgangs-Muster 💸 (Gewicht: 10%)

**Frage:** Werden eingehende Gelder schnell weitergeleitet?

**Logik:**
- > 95% ausgezahlt: Score = 90 (Durchleitungs-Muster!)
- > 80%: Score = 60
- > 60%: Score = 30
- < 60%: Score = 0 (normale Balance-Haltung)

**Warum?**
Scammer leiten Gelder oft schnell durch mehrere Wallets (Tumbling). Normale User halten Balance.

---

### Gesamt-Score Berechnung

```python
Total = (
    wallet_age          × 0.20 +
    transaction_volume  × 0.15 +
    token_concentration × 0.15 +
    scam_interaction    × 0.30 +  # WICHTIGSTER!
    mixer_usage         × 0.10 +
    inflow_outflow      × 0.10
)
```

**Risiko-Level:**
- 0-30: **LOW** (niedriges Risiko) ✅
- 31-60: **MEDIUM** (mittleres Risiko) ⚠️
- 61-100: **HIGH** (hohes Risiko) 🚨

---

## 💡 Beispiele

### Beispiel 1: Vitalik Buterin's Wallet

```bash
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Erwartetes Ergebnis:**
- Wallet-Alter: Sehr niedrig (alte Wallet)
- TX-Volumen: Normal
- Gesamt-Score: ~15-25 (LOW)

---

### Beispiel 2: Uniswap Router (Contract)

```bash
python -m src.cli.main 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
```

**Erwartetes Ergebnis:**
- Sehr hohe TX-Anzahl (Bot-Score)
- Gesamt-Score: ~30-40 (MEDIUM)
- Hinweis: Ist ein Smart Contract, kein Scam!

---

### Beispiel 3: JSON-Export

```bash
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 \
  --json vitalik_analysis.json
```

Nutze den JSON-Output für:
- Weitere Verarbeitung
- Datenbank-Speicherung
- Visualisierungen
- Batch-Analysen

---

## 💰 Kosten

### Etherscan API
- **Kostenlos** bis 100.000 Requests/Tag
- 1 Wallet-Analyse = ~3-5 Requests
- **→ ~20.000-30.000 Analysen/Tag kostenlos**

### Infura/Alchemy
- **Kostenlos** bis 100.000 Requests/Tag (Infura)
- 1 Wallet-Analyse = ~1-2 Requests
- **→ ~50.000 Analysen/Tag kostenlos**

### Claude AI (Anthropic)
- **~$0.003 pro Report** (Haiku-Modell)
- Input: ~500 Tokens
- Output: ~300 Tokens
- **→ 1000 Reports = ~$3**

**Gesamt-Kosten pro Wallet-Analyse:**
- Ohne AI: **$0 (kostenlos)**
- Mit AI: **~$0.003**

---

## 🐛 Troubleshooting

### Fehler: "Kein Etherscan API Key gefunden"

**Lösung:**
```bash
# Prüfe .env Datei
cat .env | grep ETHERSCAN_API_KEY

# Sollte ausgeben:
# ETHERSCAN_API_KEY=dein_key_hier

# Falls leer: .env Datei anlegen
cp .env.example .env
# Dann Key eintragen
```

---

### Fehler: "Konnte nicht zur Ethereum-Blockchain verbinden"

**Lösung:**
```bash
# Prüfe Internet-Verbindung
ping infura.io

# Prüfe API-Keys
cat .env | grep INFURA_PROJECT_ID

# Fallback: Nutze öffentlichen Node (langsam)
# Lösche INFURA_PROJECT_ID aus .env
```

---

### Fehler: "AI-Report fehlgeschlagen"

**Mögliche Ursachen:**
1. **Kein API-Key:** Setze `ANTHROPIC_API_KEY` in `.env`
2. **Kein Guthaben:** Lade Guthaben auf bei Anthropic
3. **Rate-Limit:** Warte kurz und versuche erneut

**Workaround:**
```bash
# Analyse ohne AI-Report
python -m src.cli.main 0x123... --no-ai
```

---

### Fehler: "Rate limit exceeded"

**Etherscan:**
- Max. 5 Requests/Sekunde
- Tool wartet automatisch
- Falls Problem bleibt: Warte 1 Minute

**Claude AI:**
- Abhängig von API-Key-Tier
- Nutze `--no-ai` für schnellere Analysen

---

## 👩‍💻 Entwicklung

### Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=src

# Spezifischer Test
pytest tests/test_heuristics.py
```

### Code-Style

```bash
# Black Formatter
black src/

# Flake8 Linter
flake8 src/

# Type Checking
mypy src/
```

### Scam-Datenbank aktualisieren

1. Öffne `data/scam_addresses.json`
2. Füge neue Adressen hinzu (mit Quelle!)
3. Aktualisiere `_update_date`
4. Teste: `python -m src.analysis.scam_lists`

**Quellen für Scam-Adressen:**
- https://etherscan.io/accounts/label/scam
- https://github.com/MyCrypto/ethereum-lists
- Community-Reports

---

## 📝 License

MIT License - siehe [LICENSE](LICENSE) Datei.

---

## 🙏 Credits

- **Web3.py**: Ethereum-Interaktion
- **Etherscan**: Blockchain-Daten
- **Anthropic Claude**: AI-Reports
- **FastAPI**: REST API Framework
- **Rich**: Terminal-Formatierung

---

## 📧 Support

Bei Fragen oder Problemen:
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/crypto-wallet-analyzer/issues)
- 📖 **Docs**: [Wiki](https://github.com/yourusername/crypto-wallet-analyzer/wiki)
- 💬 **Discord**: (Link einfügen)

---

## 🗺️ Roadmap

### v0.2.0 (geplant)
- [ ] Multi-Chain Support (BSC, Polygon, etc.)
- [ ] NFT-Analyse
- [ ] Historische Score-Entwicklung
- [ ] Web-Dashboard

### v0.3.0 (geplant)
- [ ] Machine Learning Risk-Model
- [ ] Real-Time Monitoring
- [ ] Webhook-Benachrichtigungen
- [ ] Telegram-Bot

---

**⭐ Wenn dir dieses Tool gefällt, gib dem Repo einen Star!**
