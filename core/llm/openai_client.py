"""
OpenAI Client with Function Calling Support
Handles LLM interactions for PLC diagnostics and assistance
"""

from datetime import datetime
from typing import Any

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class OpenAIClient:
    """
    OpenAI API client for PLC assistant

    Features:
    - Chat completions with GPT-4/3.5
    - Function calling for PLC operations
    - Context management
    - Token usage tracking
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Conversation history
        self.conversation_history: list[ChatCompletionMessageParam] = []

        # System prompt
        self.system_prompt = self._build_system_prompt()

        # Function definitions
        self.available_functions = self._define_functions()

        logger.info(f"OpenAI client initialized with model: {model}")

    def _build_system_prompt(self) -> str:
        """Build system prompt for PLC assistant"""
        return """Du bist ein erfahrener SPS-Diagnose-Experte und technischer Assistent.

**Deine Aufgaben:**
- Erkläre SPS-Signale, Parameter und Prozesse verständlich
- Analysiere Fehler und Alarme
- Gib präzise Lösungsvorschläge
- Nutze die bereitgestellte Dokumentation und Live-Daten

**Antwort-Struktur:**
1. Haupterklärung (klar und präzise)
2. Technische Details (wenn relevant)
3. Aktueller Status (aus Live-Daten)
4. Warnungen/Empfehlungen (wenn nötig)

**Ton:**
- Professionell, aber verständlich
- Direkt und lösungsorientiert
- Verwende Fachbegriffe, erkläre sie aber kurz

**Quellen:**
- Zitiere immer die Quelle (z.B. "Handbuch S.47")
- Unterscheide zwischen Dokumentation und Live-Daten

Antworte auf Deutsch, außer bei technischen Begriffen (z.B. "Analog Input", "PLC").
"""

    def _define_functions(self) -> list[dict[str, Any]]:
        """Define available functions for function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_signal",
                    "description": "Liest den aktuellen Wert eines PLC-Signals",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "signal_name": {
                                "type": "string",
                                "description": "Name des Signals (z.B. 'AI_02_PressureSensor')",
                            }
                        },
                        "required": ["signal_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_parameter",
                    "description": "Schreibt einen Wert in einen PLC-Parameter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param_name": {"type": "string", "description": "Name des Parameters"},
                            "value": {"type": "number", "description": "Zu schreibender Wert"},
                        },
                        "required": ["param_name", "value"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_alarm_history",
                    "description": "Holt die Alarm-Historie der letzten N Minuten",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "minutes": {
                                "type": "integer",
                                "description": "Zeitraum in Minuten",
                                "default": 60,
                            }
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_signal_trend",
                    "description": "Holt den Trendverlauf eines Signals",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "signal_name": {"type": "string", "description": "Name des Signals"},
                            "duration_minutes": {
                                "type": "integer",
                                "description": "Zeitraum in Minuten",
                                "default": 5,
                            },
                        },
                        "required": ["signal_name"],
                    },
                },
            },
        ]

    def chat(
        self, user_message: str, context: str | None = None, use_history: bool = True
    ) -> dict[str, Any]:
        """
        Send a chat message and get response

        Args:
            user_message: User's message
            context: Optional context from RAG
            use_history: Whether to include conversation history

        Returns:
            Response dict with message, usage, and function calls
        """
        # Build messages
        messages: list[ChatCompletionMessageParam] = []

        # Add system prompt
        messages.append({"role": "system", "content": self.system_prompt})

        # Add conversation history
        if use_history and self.conversation_history:
            messages.extend(self.conversation_history)

        # Add context if provided
        if context:
            messages.append({"role": "system", "content": f"=== KONTEXT ===\n{context}"})

        # Add user message
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=self.available_functions if self.available_functions else None,
            )

            # Extract response
            assistant_message = response.choices[0].message

            # Update conversation history
            if use_history:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append(
                    {"role": "assistant", "content": assistant_message.content or ""}
                )

                # Keep only last 10 messages
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]

            # Build response dict
            result = {
                "message": assistant_message.content,
                "function_calls": [],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "model": response.model,
                "timestamp": datetime.now(),
            }

            # Handle function calls
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    result["function_calls"].append(
                        {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                            "id": tool_call.id,
                        }
                    )

            logger.info(
                f"Chat completion: {response.usage.total_tokens if response.usage else 0} tokens used"
            )
            return result

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return {
                "message": f"Fehler bei der Anfrage: {str(e)}",
                "function_calls": [],
                "usage": {},
                "error": str(e),
            }

    def explain_signal(
        self, signal_name: str, signal_data: dict[str, Any], rag_context: str
    ) -> str:
        """
        Generate explanation for a signal

        Args:
            signal_name: Signal name
            signal_data: Signal metadata and current value
            rag_context: Context from RAG search

        Returns:
            Explanation text
        """
        user_query = f"Erkläre mir das Signal '{signal_name}'. Was misst/steuert es?"

        # Build context
        context = f"{rag_context}\n\n=== LIVE-DATEN ===\n"
        for key, value in signal_data.items():
            context += f"{key}: {value}\n"

        response = self.chat(user_query, context=context, use_history=False)
        return response.get("message", "Keine Antwort erhalten.")

    def diagnose_error(self, error_code: str, error_data: dict[str, Any], rag_context: str) -> str:
        """
        Diagnose an error/alarm

        Args:
            error_code: Error or alarm code
            error_data: Error details
            rag_context: Context from RAG

        Returns:
            Diagnosis and recommendations
        """
        user_query = (
            f"Analysiere Fehlercode {error_code}. Was ist die Ursache und wie behebe ich ihn?"
        )

        context = f"{rag_context}\n\n=== FEHLER-DETAILS ===\n"
        for key, value in error_data.items():
            context += f"{key}: {value}\n"

        response = self.chat(user_query, context=context, use_history=False)
        return response.get("message", "Keine Antwort erhalten.")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_conversation_history(self) -> list[dict[str, str]]:
        """Get conversation history"""
        return [
            {"role": msg["role"], "content": msg["content"]} for msg in self.conversation_history
        ]


# Global OpenAI client instance
_openai_client: OpenAIClient | None = None


def get_openai_client() -> OpenAIClient:
    """Get or create global OpenAI client instance"""
    global _openai_client
    if _openai_client is None:
        import sys
        from pathlib import Path

        # Add config to path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
        from config import settings

        if not settings.openai_api_key:
            logger.warning("OpenAI API key not set. Please configure it in .env")
            raise ValueError("OpenAI API key not configured")

        _openai_client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
        )
    return _openai_client
