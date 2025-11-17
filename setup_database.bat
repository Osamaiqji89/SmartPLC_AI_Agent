@echo off
REM ========================================================================
REM SmartPLC AI Agent - Erste Installation / Database Setup
REM ========================================================================

echo.
echo ========================================================================
echo SmartPLC AI Agent - Erste Installation
echo ========================================================================
echo.
echo Dieses Skript führt folgende Schritte aus:
echo   1. Erstellt die Datenbank
echo   2. Initialisiert alle Tabellen (8 Tabellen)
echo   3. Fügt 16 PLC-Signale hinzu
echo   4. Fügt Standard-Parameter hinzu
echo   5. Lädt Knowledge Base für RAG-System
echo.
echo Dies muss nur EINMAL beim ersten Start ausgeführt werden!
echo.

choice /C JN /M "Möchten Sie fortfahren"
if errorlevel 2 goto :cancel
if errorlevel 1 goto :start

:start
echo.
echo Starte Setup...
call scripts\setup_database.bat
goto :end

:cancel
echo.
echo Setup abgebrochen.
echo.
pause
goto :end

:end
