"""Agent state management."""

from enum import Enum, auto


class AgentState(Enum):
    """Enum representing the agent's current state in the workflow."""

    INIT = auto()
    COLLECTING_CRITERIA = auto()
    GENERATING_QUERIES = auto()
    SEARCHING = auto()
    SCRAPING = auto()
    EVALUATING = auto()
    OUTPUTTING = auto()
    COMPLETE = auto()
    ERROR = auto()

    def __str__(self) -> str:
        """Return human-readable state name."""
        return self.name.replace("_", " ").title()
