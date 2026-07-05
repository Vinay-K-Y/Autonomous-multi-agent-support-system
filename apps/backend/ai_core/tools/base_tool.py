from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Base class for every tool.
    """

    name: str

    @abstractmethod
    def execute(
        self,
        **kwargs,
    ) -> Any:
        ...