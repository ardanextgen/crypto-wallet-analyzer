# ⚡ Schnellstart-Anleitung

**Für absolute Anfänger** - Von 0 bis zur ersten Analyse in 10 Minuten!

---

## ✅ Checkliste

Stelle sicher, dass du folgendes hast:

- [ ] **Python 3.9+** installiert
- [ ] **Terminal/Kommandozeile** geöffnet
- [ ] **Internet-Verbindung** aktiv
- [ ] **10 Minuten Zeit** ⏰

---

## 📝 Schritt-für-Schritt

### Schritt 1: Python prüfen

Öffne Terminal und tippe:

```bash
python3 --version
```

**Sollte ausgeben:** `Python 3.9.x` oder höher

**Falls nicht installiert:**
- **Windows**: [python.org/downloads](https://www.python.org/downloads/)
- **Mac**: `brew install python3` (mit Homebrew)
- **Linux**: `sudo apt install python3 python3-pip`

---

### Schritt 2: Projekt herunterladen

```bash
# Wechsle in dein gewünschtes Verzeichnis
cd ~/Desktop

# Klone das Repository (oder lade ZIP herunter)
git clone https://github.com/yourusername/crypto-wallet-analyzer.git

# Wechsle in den Projektordner
cd crypto-wallet-analyzer
```

**Kein Git?** Lade die ZIP-Datei herunter und entpacke sie.

---

### Schritt 3: Virtual Environment erstellen

**Warum?** Hält Dependencies sauber getrennt von anderen Projekten.

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Erfolgreich wenn:** Dein Terminal zeigt `(venv)` am Anfang der Zeile.

---

### Schritt 4: Dependencies installieren

```bash
pip install -r requirements.txt
```

**Dauer:** ~2 Minuten (lädt alle benötigten Bibliotheken)

**Bei Fehlern:**
```bash
# Upgrade pip zuerst
pip install --upgrade pip
# Dann nochmal versuchen
pip install -r requirements.txt
```

---

### Schritt 5: API-Keys besorgen

#### 5a) Etherscan API Key (PFLICHT)

1. **Gehe zu:** [etherscan.io/register](https://etherscan.io/register)
2. **Erstelle Account** (kostenlos, dauert 2 Minuten)
3. **Gehe zu:** [etherscan.io/myapikey](https://etherscan.io/myapikey)
4. **Klicke:** "Add" Button
5. **Kopiere** den generierten API Key

**Sieht aus wie:** `ABC123DEF456GHI789...`

#### 5b) Infura Project ID (EMPFOHLEN)

1. **Gehe zu:** [infura.io/register](https://infura.io/register)
2. **Erstelle Account** (kostenlos)
3. **Create New Project**
4. **Kopiere** die Project ID

**Sieht aus wie:** `9aa3d95b3bc440fa88ea12eaa4456789`

#### 5c) Anthropic API Key (OPTIONAL - für AI)

1. **Gehe zu:** [console.anthropic.com](https://console.anthropic.com/)
2. **Erstelle Account**
3. **API Keys** → "Create Key"
4. **Lade Guthaben auf** ($5 reicht für ~1600 Reports)

---

### Schritt 6: .env Datei erstellen

```bash
# Kopiere Beispiel-Datei
cp .env.example .env

# Öffne mit Editor
# Mac: open .env
# Windows: notepad .env
# Linux: nano .env
```

**Fülle aus:**

```env
ETHERSCAN_API_KEY=dein_etherscan_key_hier
INFURA_PROJECT_ID=deine_infura_project_id_hier
ANTHROPIC_API_KEY=dein_anthropic_key_hier
```

**Speichere** die Datei!

---

### Schritt 7: Erste Analyse! 🚀

```bash
# Analysiere Vitalik Buterin's Wallet
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

**Dauer:** ~10-20 Sekunden

**Erwartete Ausgabe:**
```
🔍 Analysiere Wallet: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

✅ Blockchain-Daten abgerufen
✅ Risk-Score berechnet
✅ AI-Report generiert

═══════════════════════════════════════════
📊 WALLET RISK ANALYSIS
═══════════════════════════════════════════
...
```

**🎉 Glückwunsch! Du hast deine erste Analyse durchgeführt!**

---

## 🧪 Weitere Test-Beispiele

### Ohne AI-Report (schneller, kostenlos)

```bash
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --no-ai
```

### Mit JSON-Export

```bash
python -m src.cli.main 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --json output.json
```

### Eigene Wallet

```bash
# Ersetze 0x123... mit deiner Wallet-Adresse
python -m src.cli.main 0x123...
```

---

## 🔥 REST API starten

```bash
# Server starten
uvicorn src.api.server:app --reload --port 8000
```

**Dann öffne im Browser:**
- **Swagger Docs:** http://localhost:8000/docs
- **API Root:** http://localhost:8000

**Im Browser testen:**
```
http://localhost:8000/analyze/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
```

---

## ❓ Häufige Probleme

### "ModuleNotFoundError: No module named 'web3'"

**Lösung:**
```bash
# Stelle sicher, dass venv aktiviert ist
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Installiere nochmal
pip install -r requirements.txt
```

---

### "Kein Etherscan API Key gefunden"

**Lösung:**
```bash
# Prüfe ob .env Datei existiert
ls -la .env

# Falls nicht:
cp .env.example .env

# Öffne und fülle aus
open .env  # oder nano .env
```

---

### "HTTPError: 403 Forbidden" (Etherscan)

**Ursache:** Ungültiger API Key

**Lösung:**
1. Prüfe API Key in .env
2. Generiere neuen Key auf Etherscan
3. Ersetze in .env

---

### "Rate limit exceeded"

**Ursache:** Zu viele Requests

**Lösung:**
- Warte 1 Minute
- Nutze `--no-ai` für schnellere Analysen
- Reduziere `max_transactions`

---

## 📚 Nächste Schritte

Jetzt wo du das Tool kennst:

1. **Lies die [README.md](README.md)** für detaillierte Infos
2. **Verstehe die [Heuristiken](README.md#-heuristiken-erklärt)**
3. **Teste verschiedene Wallets**
4. **Spiele mit den API-Parametern**
5. **Entwickle eigene Features!**

---

## 💬 Hilfe benötigt?

- **GitHub Issues**: [Issues](https://github.com/yourusername/crypto-wallet-analyzer/issues)
- **README**: [README.md](README.md)
- **Code**: Alle Dateien sind ausführlich kommentiert!

---

**Happy Analyzing! 🔍✨**
