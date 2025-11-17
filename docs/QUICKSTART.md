# Quick Start Guide

## 🚀 Schnellstart in 3 Schritten

### 1. Installation
```powershell
cd SmartPLC_AI_Agent
pip install -r requirements.txt
```

### 2. Konfiguration
```powershell
# .env erstellen
Copy-Item .env.example .env

# OpenAI API Key eintragen
notepad .env
```

Fügen Sie hinzu:
```
OPENAI_API_KEY=sk-ihr-key-hier
```

### 3. Starten
```powershell
# Wissensbasis initialisieren
python init_knowledge_base.py

# Anwendung starten
python main.py
```

Oder einfach:
```powershell
.\start.bat
```

---

## 📖 Erste Schritte

1. **Dashboard öffnen**: Übersicht über PLC-Status
2. **Signal Monitor**: 
   - Klicken Sie auf "▶️ Start Pump"
   - Beobachten Sie den Tank-Level steigen
   - Klicken Sie auf "🤖 Explain" neben AI_02_PressureSensor
3. **AI Assistant**: 
   - Fragen Sie: "Erkläre Signal AI_02_PressureSensor"
   - Oder: "Was bedeutet Fehlercode E4401?"

---

## 🎯 Features ausprobieren

### Tank-Prozess steuern
```
1. Signal Monitor → "▶️ Start Pump"
2. Tank füllt sich bis 90%
3. Pumpe stoppt automatisch
4. "💧 Open Drain" zum Entleeren
```

### AI-Erklärung erhalten
```
1. Klick auf "🤖 Explain" bei beliebigem Signal
2. AI-Chat öffnet sich automatisch
3. Erklärung basierend auf Handbuch + Live-Daten
```

### Förderband-Simulation
```
1. "▶️ Start Motor" klicken
2. Objekte werden zufällig erkannt
3. Cycle Counter erhöht sich
```

---

## 🐛 Häufige Probleme

**PySide6 ImportError**
```powershell
pip install --upgrade PySide6
```

**OpenAI API Error**
- Prüfen Sie den API-Key in `.env`
- Guthaben auf OpenAI-Account prüfen

---

## 📚 Weitere Infos

- Vollständige Dokumentation: `README.md`
- Konfiguration: `config.yaml`
- Logs: `logs/plc_studio_*.log`

---

Viel Erfolg! 🚀
