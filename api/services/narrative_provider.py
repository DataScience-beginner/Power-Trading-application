"""Provider-neutral narrative boundary for evidence-backed AI explanations."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class MarketNarrativeFacts:
    """Structured facts that a narrative provider may explain but never alter."""

    file_count: int
    transaction_count: int
    total_cost: float
    total_quantity: float
    average_rate: float


class NarrativeProvider(Protocol):
    """Contract future LLM adapters must implement without database access."""

    provider_id: str

    def market_summary(self, facts: MarketNarrativeFacts) -> str:
        """Render structured facts into business language."""


class DeterministicNarrativeProvider:
    """Default key-free provider used as the reliable AI-1 baseline."""

    provider_id = "deterministic-v1"

    def market_summary(self, facts: MarketNarrativeFacts) -> str:
        """Render a stable narrative without inference or external calls."""
        if facts.file_count == 0:
            return "There is no source data in the selected scope, so a market explanation cannot be supported."
        return (
            f"The selected period contains {facts.file_count} files and {facts.transaction_count} interval records. "
            f"Recorded buy cost is ₹{facts.total_cost:,.2f}; the sum of buy quantity_mw values is "
            f"{facts.total_quantity:,.2f} MW-blocks, with an average recorded buy rate of ₹{facts.average_rate:,.2f}/MWh."
        )


def get_narrative_provider() -> NarrativeProvider:
    """Return the approved provider; external adapters require governance review."""
    return DeterministicNarrativeProvider()
