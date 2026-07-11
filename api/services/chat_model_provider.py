"""Optional Groq free-tier narration with deterministic fallback and fact anchoring."""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[2]
PROMPT = (ROOT / "prompts/chatbot_system_v1.md").read_text(encoding="utf-8")


@dataclass
class ModelResult:
    content: str
    provider: str
    model: str
    token_usage: dict[str, int] = field(default_factory=dict)
    limitation: str | None = None


def verified_facts_text(facts: dict) -> str:
    """Create an authoritative compact appendix independent of model prose."""
    pairs = []
    for key, value in facts.items():
        if isinstance(value, (str, int, float, bool)):
            pairs.append(f"{key}={value}")
    return "; ".join(pairs[:12])


class GroqNarrativeProvider:
    """Call Groq only with pre-scoped facts; never provide tools or database access."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    def narrate(self, question: str, facts: dict, deterministic_answer: str) -> ModelResult:
        """Return model narration or deterministic fallback, always with verified facts."""
        appendix = verified_facts_text(facts)
        if not self.api_key:
            return ModelResult(
                content=f"{deterministic_answer}\n\nVerified facts: {appendix}",
                provider="deterministic",
                model="deterministic-v1",
                limitation="GROQ_API_KEY is not configured; deterministic response used.",
            )
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": PROMPT},
                {
                    "role": "user",
                    "content": f"Question: {question}\nStructured facts: {json.dumps(facts, ensure_ascii=False)}\nBaseline answer: {deterministic_answer}",
                },
            ],
        }
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
            narrative = data["choices"][0]["message"]["content"].strip()
            usage = data.get("usage", {})
            return ModelResult(
                content=f"{narrative}\n\nVerified facts: {appendix}",
                provider="groq",
                model=self.model,
                token_usage={key: int(value) for key, value in usage.items() if isinstance(value, int)},
            )
        except (requests.RequestException, KeyError, ValueError, TypeError) as exc:
            return ModelResult(
                content=f"{deterministic_answer}\n\nVerified facts: {appendix}",
                provider="deterministic",
                model="deterministic-v1",
                limitation=f"Groq unavailable; deterministic fallback used ({type(exc).__name__}).",
            )
