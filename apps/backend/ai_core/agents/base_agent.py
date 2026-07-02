from abc import ABC, abstractmethod
from ai_core.state.support_state import SupportState


class BaseAgent(ABC):
    @abstractmethod
    async def execute(self, state: SupportState) -> SupportState:
        """Execute the agent and return the updated state."""
        pass