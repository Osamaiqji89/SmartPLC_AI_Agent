@echo off
REM ========================================================================
REM SmartPLC AI Agent - Database Setup
REM Erstellt und initialisiert die Datenbank mit allen Standarddaten
REM ========================================================================

echo.
echo ========================================================================
echo SmartPLC AI Agent - Database Setup
echo ========================================================================
echo.

REM Wechsel ins Projekt-Verzeichnis
cd /d "%~dp0.."

REM Überprüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    echo Bitte installieren Sie Python 3.8 oder neuer.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python gefunden
echo.

REM Überprüfe ob virtuelle Umgebung existiert
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Aktiviere virtuelle Umgebung...
    call venv\Scripts\activate.bat
) else (
    echo [WARNUNG] Keine virtuelle Umgebung gefunden
    echo [INFO] Verwende System-Python
)

echo.
echo ========================================================================
echo Starte Database Setup...
echo ========================================================================
echo.

REM Führe Setup-Skript aus
python scripts\init_database.py

REM Überprüfe Exit-Code
if errorlevel 1 (
    echo.
    echo ========================================================================
    echo FEHLER: Database Setup fehlgeschlagen!
    echo ========================================================================
    echo.
    echo Bitte überprüfen Sie:
    echo   - Alle Python-Abhängigkeiten sind installiert (pip install -r requirements.txt)
    echo   - Keine andere Anwendung greift auf die Datenbank zu
    echo   - Sie haben Schreibrechte im data/db Verzeichnis
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo Database Setup erfolgreich abgeschlossen!
echo ========================================================================
echo.
echo Die Datenbank wurde erstellt und mit folgenden Daten gefüllt:
echo   - PLC Signals (16 Signale)
echo   - Default Parameters
echo   - Knowledge Base (RAG System)
echo.
echo Sie können jetzt die Anwendung starten:
echo   - Doppelklick auf start.bat
echo   - Oder: python main.py
echo.

pause
