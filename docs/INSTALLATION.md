# 🎉 Installation & Erste Schritte

## ✅ Was wurde erstellt?

Das **SmartPLC AI Agent** ist vollständig implementiert mit:

### 🏗️ Architektur
- ✅ Modulare Ordnerstruktur (gui/, core/, knowledge_base/)
- ✅ MVP-Pattern (Model-View-Presenter)
- ✅ Saubere Trennung: GUI ↔ Business Logic ↔ Data

### 🧠 Core Features
- ✅ **Mock PLC** mit 14 Signalen (Tank + Förderband)
- ✅ **RAG-System** mit FAISS + sentence-transformers
- ✅ **OpenAI Integration** (GPT-4-turbo + Function Calling)
- ✅ **SQLite Datenbank** (8 Tabellen für vollständige Persistenz)

### 🖥️ GUI (PySide6)
- ✅ **Dashboard** - Prozess-Übersicht
- ✅ **Signal Monitor** - Echtzeit I/O-Tabelle mit 🤖 Explain-Buttons
- ✅ **AI Chat** - Interaktiver Assistent mit RAG-Kontext
- ✅ **Parameter Editor** - CRUD für SPS-Parameter

### 📚 Wissensbasis
- ✅ Fehlercode-Datenbank (E4401, A-0023, W-1205, E-3301)
- ✅ Signal-Dokumentation (14 Signale vollständig beschrieben)
- ✅ FAQ (20+ häufige Fragen beantwortet)

---

## 🚀 Installation (Windows)

### Methode 1: Automatisch (Empfohlen)

```powershell
cd SmartPLC_AI_Agent
.\install.bat
```

Das Skript:
1. ✅ Prüft Python-Installation
2. ✅ Erstellt Virtual Environment
3. ✅ Installiert alle Dependencies
4. ✅ Erstellt .env-Datei

### Methode 2: Manuell

```powershell
# 1. Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. .env konfigurieren
Copy-Item .env.example .env
notepad .env
```

---

## ⚙️ Konfiguration

### 1. OpenAI API Key setzen

Bearbeiten Sie `.env`:

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

**Wichtig:** Ohne API-Key läuft die App, aber AI-Features zeigen Fallback-Erklärungen.

### 2. (Optional) Einstellungen anpassen

`config.yaml`:
```yaml
openai:
  model: "gpt-4-turbo-preview"  # oder "gpt-3.5-turbo" (günstiger)
  temperature: 0.7
  max_tokens: 2000

plc:
  update_interval_ms: 500  # Signal-Update-Frequenz

rag:
  top_k_results: 3  # Anzahl RAG-Dokumente pro Anfrage
```

---

## 📖 Wissensbasis initialisieren

**Einmalig vor dem ersten Start:**

```powershell
python init_knowledge_base.py
```

Output:
```
INFO: Initializing FAISS...<|diff_marker|>
INFO:   Created 12 chunks
✅ Knowledge base initialized:
   Total documents: 44
   Files processed: 3
```

→ Erstellt `vector_store/` mit allen Embeddings

---

## ▶️ Anwendung starten

### Methode 1: Start-Skript (Empfohlen)

```powershell
.\start.bat
```

Das Skript:
- Aktiviert venv
- Prüft Dependencies
- Initialisiert RAG (falls nötig)
- Startet Anwendung

### Methode 2: Direkt

```powershell
venv\Scripts\activate
python main.py
```

---

## 🎯 Erste Schritte in der Anwendung

### 1. Dashboard erkunden
- Übersicht: PLC-Status, Signale, Alarme
- Prozess-Status: Tank-Level, Pumpe, Förderband

### 2. Tank-Prozess steuern

```
1. Tab "Signal Monitor" öffnen
2. Klick auf "▶️ Start Pump"
3. Beobachten: Tank Level steigt von 20% → 90%
4. Pumpe stoppt automatisch bei 90%
5. Klick auf "💧 Open Drain" zum Entleeren
```

### 3. AI-Signal-Erklärung testen

```
1. Im Signal Monitor: Klick auf "🤖 Explain" neben "AI_02_PressureSensor"
2. AI-Chat-Tab öffnet sich automatisch
3. System analysiert:
   - Signal-Metadaten
   - Aktuelle Werte
   - Trend (letzte 5 Min)
   - RAG-Dokumente (Handbuch, FAQ)
4. GPT-4 generiert Erklärung:
   "Dieser Parameter steht für den analogen Eingang 2 des
    Drucksensors. Der Wert wird in bar gemessen..."
```

### 4. Freie Fragen stellen

Im AI-Chat-Tab:
```
✅ "Erkläre Signal AI_01_TankLevel"
✅ "Was bedeutet Fehlercode E4401?"
✅ "Wie kalibriere ich einen Drucksensor?"
✅ "Warum läuft die Pumpe nicht?"
```

---

## 🐛 Troubleshooting

### ❌ "Import PySide6 could not be resolved"

```powershell
pip install --upgrade PySide6
```

### ❌ "OpenAI API nicht konfiguriert"

1. Prüfen Sie `.env`: OPENAI_API_KEY gesetzt?
2. API-Key korrekt? Testen:
   ```powershell
   python -c "from openai import OpenAI; print(OpenAI(api_key='sk-...').models.list())"
   ```

### ❌ "Vector Store collection empty"

```powershell
# Wissensbasis neu initialisieren
Remove-Item -Recurse -Force data\vector_store
python init_knowledge_base.py
```

### ❌ "Database locked"

```powershell
# SQLite-Datei löschen (Datenbank wird neu erstellt)
Remove-Item plc_data.db
```

### ❌ Import-Fehler bei sentence-transformers

```powershell
# Torch manuell installieren (Windows)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

---

## 📊 Test-Szenarien

### Szenario 1: Tank-Überfüllung simulieren

```
1. Start Pump
2. Warten bis Level > 95%
3. System zeigt Alarm (roter Hintergrund in Tabelle)
4. AI fragen: "Warum ist der Tank-Level so hoch?"
   → AI schlägt Drain-Ventil öffnen vor
```

### Szenario 2: Förderband-Produktion

```
1. Start Motor
2. Beobachten: Cycle Counter steigt
3. Belt Speed stabilisiert sich bei ~50 m/min
4. AI fragen: "Wie funktioniert die Objekt-Erkennung?"
```

### Szenario 3: Signal-Dokumentation abrufen

```
1. Klick auf 🤖 bei DI_01_StartButton
2. AI erklärt: NOT-AUS-Taster, SIL 2, 24V DC
3. Quelle: signal_documentation.md
```

---

## 📈 Performance-Tipps

### Kosten reduzieren (OpenAI)

`config.yaml`:
```yaml
openai:
  model: "gpt-3.5-turbo"  # Statt GPT-4 (10x günstiger)
```

### Schnellere RAG-Suche

`config.yaml`:
```yaml
rag:
  top_k_results: 1  # Statt 3 (weniger Dokumente = schneller)
```

### Weniger häufige Updates

`config.yaml`:
```yaml
plc:
  update_interval_ms: 1000  # Statt 500ms
```

---

## 📚 Weitere Dokumentation

| Datei | Inhalt |
|-------|--------|
| `README.md` | Vollständige Projekt-Dokumentation |
| `ARCHITECTURE.md` | Architektur-Diagramme & Datenfluss |
| `QUICKSTART.md` | Schnelleinstieg (Kurzversion) |
| `knowledge_base/*.md` | Technische Handbücher für RAG |

---

## 🎓 Lernressourcen

### Code-Struktur verstehen

**Start hier:**
1. `main.py` - Entry Point
2. `gui/views/main_window.py` - GUI-Aufbau
3. `gui/views/signal_monitor.py` - Signal-Tabelle + Explain-Button
4. `gui/views/ai_chat.py` - ⭐ Kern-Feature: RAG + OpenAI
5. `core/llm/rag_engine.py` - Wie RAG funktioniert
6. `core/llm/openai_client.py` - OpenAI API-Aufrufe
7. `core/plc/mock_plc.py` - PLC-Simulation

### RAG-Workflow nachvollziehen

```python
# 1. Wissensbasis laden
from core.llm.rag_engine import get_rag_engine
rag = get_rag_engine()

# 2. Suchen
results = rag.search("Drucksensor AI_02", top_k=3)
print(results[0]["content"])  # Handbuch-Auszug

# 3. OpenAI anfragen
from core.llm.openai_client import get_openai_client
ai = get_openai_client()
response = ai.chat("Erkläre AI_02", context=results[0]["content"])
print(response["message"])
```

---

## 🚀 Nächste Schritte

### Jetzt testen:
```powershell
cd SmartPLC_AI_Agent
.\install.bat
# .env bearbeiten: OpenAI API-Key eintragen
python init_knowledge_base.py
.\start.bat
```

### Dann:
1. ✅ Dashboard ansehen
2. ✅ Pumpe starten → Tank füllen
3. ✅ 🤖 Explain-Button testen
4. ✅ Eigene Fragen im AI-Chat stellen

### Erweitern (für Fortgeschrittene):
- Eigene Signale zur Mock-PLC hinzufügen
- Neue Dokumente zu `knowledge_base/` hinzufügen
- Trend-Charts mit matplotlib implementieren
- Echte PLC-Verbindung (pyads/pymodbus)

---

**Viel Erfolg! Bei Fragen: Nutzen Sie den AI-Assistenten im Tool! 🤖**

---

**Projekt:** SmartPLC AI Agent  
**Technologien:** PySide6, FAISS, OpenAI GPT-4, SQLite  
**Status:** ✅ Vollständig funktionsfähig (Phase 1 abgeschlossen)
