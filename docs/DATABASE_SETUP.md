# Database Setup - SmartPLC AI Agent

## 🚀 Schnellstart

### Erste Installation (nur einmal ausführen)

```bash
# Doppelklick auf:
setup_database.bat
```

Das Skript erstellt automatisch:
- ✅ SQLite Datenbank (`data/db/plc_data.db`)
- ✅ 8 Tabellen (projects, signals, signal_history, parameters, alarm_logs, chat_history, signal_documentation, user_settings)
- ✅ 16 PLC-Signale (4 DI, 5 DO, 4 AI, 3 AO)
- ✅ Default-Parameter (Timer, Setpoints, Thresholds)
- ✅ RAG Knowledge Base (Vector Store)

---

## 📋 Was macht das Setup?

### Schritt 1: Database Schema
Erstellt alle 8 Tabellen mit korrekten Relationen:
- `projects` - PLC Projekte
- `signals` - I/O Signale (16 Stück)
- `signal_history` - Zeit-Serien Daten (alle 5s)
- `parameters` - Konfigurations-Parameter
- `alarm_logs` - Alarm Historie
- `chat_history` - AI Chat Konversationen
- `signal_documentation` - RAG Dokumentation
- `user_settings` - Benutzer-Einstellungen

### Schritt 2: PLC Signals
Fügt 16 vorkonfigurierte Signale hinzu:

**Digital Inputs:**
- `DI_01_StartButton` - Start-Taste
- `DI_02_StopButton` - Stop-Taste
- `DI_03_ObjectSensor` - Objekt-Sensor
- `DI_04_LimitSwitch` - Endschalter

**Digital Outputs:**
- `DO_01_Pump` - Tank-Pumpe
- `DO_02_DrainValve` - Ablassventil
- `DO_03_Motor` - Förderband-Motor
- `DO_04_Stopper` - Stopper-Zylinder
- `DO_02_Drain` - Ablassventil (Alternative)

**Analog Inputs:**
- `AI_01_TankLevel` (%, Alarm bei 95%)
- `AI_02_PressureSensor` (bar, Alarm bei 9.5)
- `AI_03_BeltSpeed` (m/min, Alarm bei 95)
- `AI_04_CycleCounter` (cycles, kein Alarm)

**Analog Outputs:**
- `AO_01_FlowControl` (%, 0-100)
- `AO_02_MotorSpeed` (%, 0-100)
- `AO_03_HeatingPower` (%, 0-100)

### Schritt 3: Default Parameters
Erstellt Standard-Parameter:
- Timer-Einstellungen (Motor Start Delay, Pump Runtime)
- Setpoints (Tank Target Level, Pressure Setpoint)
- Thresholds (Temperature Limits, Speed Limits)
- Safety-Parameter (Emergency Stop Delay)

### Schritt 4: Knowledge Base
Lädt Dokumentation aus `knowledge_base/`:
- Error Codes (`error_codes.md`)
- FAQs (`faqs/common_questions.md`)
- Signal Dokumentation (`manuals/signal_documentation.md`)

---

## 🔧 Manuelle Ausführung

Falls Sie einzelne Schritte manuell ausführen möchten:

```bash
# Nur Schema erstellen
python -c "from core.data.database import init_database; init_database()"

# Nur Signals initialisieren
python scripts\init_signals.py

# Nur Parameters initialisieren
python scripts\init_parameters.py

# Nur Knowledge Base laden
python scripts\init_knowledge_base.py

# ODER: Alles auf einmal
python scripts\init_database.py
```

---

## ⚠️ Datenbank zurücksetzen

Falls Sie die Datenbank komplett neu erstellen möchten:

```bash
# 1. Alte Datenbank löschen
del data\db\plc_data.db
del data\db\plc_data.db-journal

# 2. Vector Store löschen (optional)
rmdir /s /q data\vector_store

# 3. Setup erneut ausführen
setup_database.bat
```

---

## 📊 Datenbank-Struktur

```
data/
├── db/
│   ├── plc_data.db         # SQLite Hauptdatenbank
│   └── plc_data.db-journal # SQLite Journal (temporär)
├── vector_store/           # FAISS Vector Store (veraltet)
│   ├── plc_knowledge.index
│   ├── plc_knowledge_docs.txt
│   └── plc_knowledge_meta.txt
```

---

## ✅ Verifikation

Nach erfolgreichem Setup sollten Sie sehen:

```
Database Setup Complete - Verification:
================================================================================
  Projects:   1
  Signals:    16
  Parameters: 21

  Active Project: 'Default Project'
  Description:    SmartPLC Simulation Project
================================================================================
✓ Database setup successful!
```

---

## 🐛 Troubleshooting

### Fehler: "Python ist nicht installiert"
- Installieren Sie Python 3.8+ von https://www.python.org/
- Fügen Sie Python zum PATH hinzu

### Fehler: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Fehler: "Database is locked"
- Schließen Sie alle anderen Anwendungen, die auf `plc_data.db` zugreifen
- Löschen Sie `plc_data.db-journal`
- Führen Sie Setup erneut aus

### Fehler: "Permission denied"
- Führen Sie die BAT-Datei als Administrator aus
- Überprüfen Sie Schreibrechte im `data/` Verzeichnis

---

## 📚 Weitere Informationen

- **Architecture:** `docs/ARCHITECTURE.md`
- **Installation:** `docs/INSTALLATION.md`
- **Quickstart:** `docs/QUICKSTART.md`

---

**Hinweis:** Das Setup muss nur EINMAL beim ersten Start ausgeführt werden. Danach können Sie die Anwendung normal mit `start.bat` oder `python main.py` starten.
