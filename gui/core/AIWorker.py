from PySide6.QtCore import QThread, Signal as PySignal
from loguru import logger

from core.llm.openai_client import get_openai_client
from core.llm.rag_engine import get_rag_engine, build_context_for_signal
from core.plc.mock_plc import get_plc


class AIWorker(QThread):
    """Background worker for AI requests"""

    response_ready = PySignal(str)
    error_occurred = PySignal(str)

    def __init__(self, request_type: str, data: dict):
        super().__init__()
        self.request_type = request_type
        self.data = data

    def run(self):
        """Execute AI request in background"""
        try:
            if self.request_type == "explain_signal":
                result = self._explain_signal()
            elif self.request_type == "chat":
                result = self._chat()
            else:
                result = "Unknown request type"

            self.response_ready.emit(result)
        except Exception as e:
            import traceback

            logger.error(f"AI worker error: {e}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            self.error_occurred.emit(str(e))

    def _explain_signal(self) -> str:
        """Generate signal explanation"""
        signal_name = self.data["signal_name"]
        plc = get_plc()

        # Get signal data
        signal = plc.signals.get(signal_name)
        if not signal:
            return f"Signal '{signal_name}' not found."

        signal_metadata = {
            "name": signal.name,
            "type": signal.type.value,
            "current_value": signal.value,
            "unit": signal.unit,
            "description": signal.description,
            "range": f"{signal.min_value} - {signal.max_value}",
            "alarm_threshold": signal.alarm_threshold,
        }

        # Get trend data
        history = plc.get_signal_history(signal_name, limit=10)
        if len(history) >= 2:
            trend_start = history[0]["value"]
            trend_end = history[-1]["value"]
            if isinstance(trend_start, (int, float)) and isinstance(trend_end, (int, float)):
                change = trend_end - trend_start
                if change > 0.1:
                    signal_metadata["trend"] = "↗️ steigend"
                elif change < -0.1:
                    signal_metadata["trend"] = "↘️ fallend"
                else:
                    signal_metadata["trend"] = "→ stabil"

        # Build RAG context (with fast fallback if RAG unavailable)
        rag_context = ""
        try:
            rag_engine = get_rag_engine()
            if rag_engine and hasattr(rag_engine, "embedder") and rag_engine.embedder:
                rag_context = build_context_for_signal(
                    rag_engine, signal_name, signal_metadata, top_k=3
                )
        except Exception as e:
            logger.debug(f"RAG unavailable, skipping context: {e}")
            # Continue without RAG context

        # Get AI explanation
        try:
            ai_client = get_openai_client()
            explanation = ai_client.explain_signal(
                signal_name, signal_metadata, rag_context if rag_context else None
            )
            return explanation
        except ValueError as e:
            # OpenAI not configured
            return self._fallback_explanation(signal_metadata)

    def _fallback_explanation(self, signal_metadata: dict) -> str:
        """Fallback explanation when AI is not available"""
        explanation = f"**Signal: {signal_metadata['name']}**\n\n"
        explanation += f"**Typ:** {signal_metadata['type']}\n"
        explanation += f"**Beschreibung:** {signal_metadata['description']}\n"
        explanation += (
            f"**Aktueller Wert:** {signal_metadata['current_value']} {signal_metadata['unit']}\n"
        )
        explanation += f"**Bereich:** {signal_metadata['range']} {signal_metadata['unit']}\n"

        if signal_metadata.get("trend"):
            explanation += f"**Trend:** {signal_metadata['trend']}\n"

        if signal_metadata["alarm_threshold"]:
            explanation += f"\n⚠️ **Alarm-Schwelle:** {signal_metadata['alarm_threshold']} {signal_metadata['unit']}\n"

        explanation += "\n*Hinweis: OpenAI API nicht konfiguriert. Bitte API-Key in .env setzen für KI-gestützte Erklärungen.*"
        return explanation

    def _chat(self) -> str:
        """Handle chat message"""
        user_message = self.data["message"]

        try:
            ai_client = get_openai_client()

            # Simple chat without special context
            response = ai_client.chat(user_message, use_history=True)
            return response.get("message", "Keine Antwort erhalten.")
        except ValueError:
            return (
                "⚠️ OpenAI API nicht konfiguriert. Bitte setzen Sie den API-Key in der .env Datei."
            )
