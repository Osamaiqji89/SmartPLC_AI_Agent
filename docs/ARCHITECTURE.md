# Projektübersicht: SmartPLC AI Agent

## 📊 Architektur-Diagramm

```text
┌────────────────────────────────────────────────────────────────┐
│                         GUI LAYER (PySide6)                    │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Dashboard   │  Signal      │  Parameter   │   AI Chat         │
│  • Status    │  Monitor     │  Editor      │   • RAG Context   │
│  • Prozesse  │  • I/O-Table │  • CRUD      │   • OpenAI GPT-4  │
│              │  • Button    │              │   • Chat-UI       │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                       │
├──────────────────┬────────────────────┬────────────────────────┤
│   PLC Service    │   LLM + RAG        │   Data Layer           │
│                  │                    │                        │
│ • Mock PLC       │ • FAISS            │ • SQLite               │
│ • Tank Process   │ • Embeddings       │ • SQLAlchemy           │
│ • Conveyor       │ • OpenAI Client    │ • Models               │
│ • I/O Signals    │ • Function Calling │ • Persistence          │
│ • Threading      │ • Context Builder  │ • Logging              │
└──────────────────┴────────────────────┴────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                      DATA & KNOWLEDGE                          │
├─────────────────┬───────────────────┬──────────────────────────┤
│ plc_data.db     │ vector_store/     │ knowledge_base/          │
│                 │                   │                          │
│ • projects      │ • FAISS Index     │ • error_codes.md         │
│ • signals       │ • Embeddings      │ • signal_docs.md         │
│ • parameters    │ • Documents       │ • faqs.md                │
│ • chat_history  │                   │                          │
│ • logs          │                   │                          │
└─────────────────┴───────────────────┴──────────────────────────┘
```

---

## 🔄 Signal Explainer - Datenfluss

```text
USER ACTION: Klick auf [🤖 Explain] neben "AI_02_PressureSensor"
    │
    ├─▶ SignalMonitorView
    │      └─▶ emit signal_explain_requested("AI_02_PressureSensor")
    │
    ├─▶ MainWindow (empfängt Signal)
    │      └─▶ Wechsel zu AI-Chat Tab
    │      └─▶ ai_chat_view.explain_signal("AI_02_PressureSensor")
    │
    ├─▶ AIChatView
    │      └─▶ Startet AIWorker Thread (Background)
    │
    ├─▶ AIWorker._explain_signal()
    │      │
    │      ├─▶ 1. PLC Daten holen
    │      │     • signal = plc.signals["AI_02_PressureSensor"]
    │      │     • value = 6.47 bar
    │      │     • trend = "↗️ steigend"
    │      │
    │      ├─▶ 2. RAG-Suche
    │      │     • Query: "Erkläre AI_02_PressureSensor..."
    │      │     • FAISS.search(query, top_k=3)
    │      │     • Ergebnis: [Handbuch S.47, Fehlercode-DB, FAQ]
    │      │
    │      ├─▶ 3. Kontext aufbereiten
    │      │     • Signal-Metadaten
    │      │     • RAG-Dokumente
    │      │     • Live-Werte
    │      │     • Trend-Daten
    │      │
    │      ├─▶ 4. OpenAI API Call
    │      │     • Model: GPT-4-turbo
    │      │     • System Prompt: "Du bist SPS-Experte..."
    │      │     • Context: [RAG + Live Data]
    │      │     • User Query: "Was misst dieser Parameter?"
    │      │
    │      └─▶ 5. Antwort generieren
    │            • "Dieser Parameter steht für den analogen
    │               Eingang 2 des Drucksensors..."
    │
    └─▶ AIChatView._on_response_received()
           └─▶ Anzeige im Chat-Fenster
```

---

## 📁 Datei-Struktur

```text
SmartPLC_AI_Agent/
│
├── 🚀 ENTRY POINTS
│   ├── main.py                    # Haupt-Einstiegspunkt
│   ├── start.bat                  # Windows-Starter
│   └── init_knowledge_base.py     # RAG initialisieren
│
├── ⚙️ CONFIGURATION
│   ├── config.py                  # Config-Loader
│   ├── config.yaml                # Einstellungen
│   ├── .env.example               # Template
│   └── requirements.txt           # Dependencies
│
├── 🧠 CORE LOGIC
│   ├── plc/
│   │   ├── mock_plc.py           # ⭐ PLC-Simulator
│   │   │   • Tank-Füllanlage
│   │   │   • Förderband
│   │   │   • 14 Signale (DI/DO/AI/AO)
│   │   │   • Threading (500ms Update)
│   │   └── __init__.py
│   │
│   ├── llm/
│   │   ├── rag_engine.py         # ⭐ RAG + FAISS
│   │   │   • Vector Search
│   │   │   • Document Chunking
│   │   │   • Embedding Generation
│   │   ├── openai_client.py      # ⭐ OpenAI Integration
│   │   │   • Chat Completions
│   │   │   • Function Calling
│   │   │   • Context Management
│   │   └── __init__.py
│   │
│   └── data/
│       ├── database.py           # ⭐ SQLAlchemy Models
│       │   • Project, Signal, Parameter
│       │   • AlarmLog, ChatHistory
│       │   • SignalDocumentation
│       └── __init__.py
│
├── 🖥️ GUI (PySide6)
│   └── views/
│       ├── main_window.py        # Haupt-Fenster + Tabs
│       ├── dashboard.py          # Prozess-Übersicht
│       ├── signal_monitor.py     # ⭐ I/O-Tabelle + Explain-Button
│       ├── ai_chat.py            # ⭐ Chat-Interface + RAG
│       ├── parameter_editor.py   # Parameter-CRUD
│       └── __init__.py
│
├── 📚 KNOWLEDGE BASE
│   ├── error_codes.md            # Fehlercode-Datenbank
│   ├── manuals/
│   │   └── signal_documentation.md  # Signal-Handbuch
│   └── faqs/
│       └── common_questions.md   # FAQ
│
├── 📖 DOCUMENTATION
│   ├── README.md                 # Vollständige Doku
│   ├── QUICKSTART.md             # Schnelleinstieg
│   └── ARCHITECTURE.md           # Diese Datei
│
└── 🗂️ RUNTIME DATA
    ├── plc_data.db               # SQLite (erstellt automatisch)
    ├── vector_store/             # FAISS Vector Store (nach init)
    └── logs/                     # Log-Dateien
```

---

## 🎯 Kern-Features: Implementation

### 1️⃣ Mock PLC (`core/plc/mock_plc.py`)

**Klasse: `MockPLC`**

- ✅ 14 I/O-Signale (DI, DO, AI, AO)
- ✅ Tank-Füllanlage-Simulation
  - Pumpe → Level steigt
  - Drain → Level sinkt
  - Auto-Stop bei 90%
- ✅ Förderband-Simulation
  - Motor → Belt Speed
  - Objekt-Erkennung (random)
  - Zyklus-Counter
- ✅ Threading (500ms Update)
- ✅ Callbacks für Signal-Änderungen
- ✅ Alarm-Trigger bei Schwellenwert

**Signale:**

```python
AI_01_TankLevel       # 0-100%
AI_02_PressureSensor  # 0-10 bar ⭐
AI_03_BeltSpeed       # 0-100 m/min
DI_01_StartButton
DO_01_Pump
DO_03_Motor
...
```

---

### 2️⃣ RAG Engine (`core/llm/rag_engine.py`)

**Klasse: `RAGEngine`**

- ✅ FAISS Vector Store
- ✅ SentenceTransformer Embeddings
- ✅ Document Chunking (512 chars, 50 overlap)
- ✅ Semantic Search (top_k=3)
- ✅ Metadata Filtering

**Workflow:**

```python
# 1. Dokument hinzufügen
rag.add_document(
    content="AI_02: Drucksensor Endress+Hauser...",
    metadata={"source": "Handbuch S.47", "category": "signals"}
)

# 2. Suchen
results = rag.search(
    query="Erkläre AI_02_PressureSensor",
    top_k=3
)

# 3. Kontext aufbauen
context = build_context_for_signal(rag, signal_name, metadata)
```

---

### 3️⃣ OpenAI Client (`core/llm/openai_client.py`)

**Klasse: `OpenAIClient`**

- ✅ GPT-4-turbo / GPT-3.5-turbo
- ✅ System Prompt (SPS-Experte)
- ✅ Conversation History
- ✅ Function Calling (4 Funktionen)
- ✅ Token Usage Tracking

**Functions:**

1. `read_signal(signal_name)` - PLC lesen
2. `write_parameter(name, value)` - PLC schreiben
3. `get_alarm_history(minutes)` - Alarme
4. `get_signal_trend(signal_name)` - Trend

**Methoden:**

```python
# Signal erklären
explanation = client.explain_signal(
    signal_name="AI_02_PressureSensor",
    signal_data={...},
    rag_context="..."
)

# Chat
response = client.chat(
    user_message="Was bedeutet E4401?",
    context=rag_context,
    use_history=True
)
```

---

### 4️⃣ AI Chat View (`gui/views/ai_chat.py`)

**Klasse: `AIChatView`**
- ✅ QTextEdit für Chat-Historie
- ✅ QLineEdit für User-Input
- ✅ Background Worker (QThread)
- ✅ Signal-Erklärung per Button
- ✅ Fallback ohne OpenAI

**Besonderheit: AIWorker Thread**
```python
class AIWorker(QThread):
    def run(self):
        # 1. Signal-Daten holen
        # 2. RAG-Suche
        # 3. OpenAI-Anfrage
        # 4. emit response_ready(text)
```

→ GUI bleibt responsive während AI-Anfrage!

---

### 5️⃣ Signal Monitor (`gui/views/signal_monitor.py`)

**Klasse: `SignalMonitorView`**
- ✅ QTableWidget mit 6 Spalten
- ✅ Echtzeit-Update (500ms)
- ✅ 🤖 Explain-Button pro Signal
- ✅ Farbcodierung (Alarm-Status)
- ✅ Steuerungs-Buttons

**Explain-Button Logik:**
```python
explain_btn.clicked.connect(
    lambda checked, s=name: self._on_explain_clicked(s)
)

def _on_explain_clicked(self, signal_name: str):
    self.signal_explain_requested.emit(signal_name)
```

→ Signal wird zu MainWindow → AI Chat

---

## 🔧 Technologie-Entscheidungen

| Technologie | Warum? |
|-------------|--------|
| **PySide6** | Offizielle Qt-Bindings, LGPL-Lizenz, bessere Performance als PyQt |
| **FAISS** | Hochperformant, CPU-only möglich, keine DLL-Probleme unter Windows |
| **sentence-transformers** | Kostenlos, offline nutzbar, gute Qualität |
| **OpenAI GPT-4** | State-of-the-art LLM, Function Calling, gute Deutsch-Unterstützung |
| **SQLite** | Embedded, keine Installation, ausreichend für Desktop-App |
| **loguru** | Moderner als logging, bessere Formatierung |

---

## 📊 Datenfluss-Übersicht

```
┌──────────────┐
│ User-Aktion  │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ GUI View     │─────▶│ Presenter/   │─────▶│ Core Logic   │
│ (PySide6)    │      │ MainWindow   │      │ (Business)   │
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                    │
                      ┌─────────────────────────────┼─────────┐
                      ▼                             ▼         ▼
                ┌───────────┐               ┌──────────┐ ┌─────────┐
                │ Mock PLC  │               │ RAG      │ │ OpenAI  │
                │ (Signals) │               │ Engine   │ │ Client  │
                └───────────┘               └──────────┘ └─────────┘
                      │                          │            │
                      ▼                          ▼            │
                ┌───────────┐               ┌──────────┐     │
                │ SQLite DB │               │  FAISS   │     │
                └───────────┘               └──────────┘     │
                                                             │
                                                             ▼
                                                    ┌─────────────┐
                                                    │ OpenAI API  │
                                                    │ (Internet)  │
                                                    └─────────────┘
```

---

## 🚀 Erweiterungsmöglichkeiten

### Kurzfristig
- [ ] Matplotlib-Charts für Trends
- [ ] Alarm-Manager mit Filter/Suche
- [ ] Export zu CSV/JSON
- [ ] Import von Konfigurationen

### Mittelfristig
- [ ] Echte PLC-Unterstützung
  - [ ] ADS (Beckhoff) via pyads
  - [ ] Modbus TCP via pymodbus
  - [ ] OPC UA via opcua
- [ ] Benutzer-Rollen (Operator/Engineer/Admin)
- [ ] Project-Management (Speichern/Laden)

### Langfristig
- [ ] Web-Interface (FastAPI + React)
- [ ] Multi-PLC Support
- [ ] Predictive Maintenance (ML)
- [ ] Cloud-Integration (Azure IoT)

---

**Autor:** SmartPLC AI Agent Team  
**Version:** 1.0.0  
**Datum:** Oktober 2025
