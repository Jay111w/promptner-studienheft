"""KI-Dienste: OpenAI-Anbindung, Prompts, Antwort-Parser."""

from korrektor.services.ai.openai_client import OpenAiClient
from korrektor.services.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from korrektor.services.ai.response_parser import parse_corrections

__all__ = ["OpenAiClient", "SYSTEM_PROMPT", "build_user_prompt", "parse_corrections"]
