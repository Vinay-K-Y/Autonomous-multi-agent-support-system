import inspect
from typing import Any

from ai_core.models.execution_plan import ExecutionPlan
from ai_core.tools.registry import tool_registry


class ToolExecutor:
    """
    Executes one or more registered tools.
    """

    def execute(
        self,
        tool_name: str,
        **kwargs,
    ) -> Any:

        tool = tool_registry.get(tool_name)
        method = getattr(tool, "execute")
        signature = inspect.signature(method)

        normalized_kwargs = {}
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if name in kwargs:
                normalized_kwargs[name] = kwargs[name]
            elif name == "question" and "query" in kwargs:
                normalized_kwargs[name] = kwargs["query"]
            elif name == "conversation" and "conversation_id" in kwargs:
                normalized_kwargs[name] = kwargs["conversation_id"]

        return tool.execute(**normalized_kwargs)

    def execute_plan(
        self,
        plan: ExecutionPlan,
    ) -> dict[str, Any]:
        """
        Executes every tool requested by the planner.

        Returns:
            {
                "knowledge": ...,
                "ticket": ...,
                "memory": ...
            }
        """

        results: dict[str, Any] = {}

        for call in plan.tool_calls:

            results[call.tool] = self.execute(
                call.tool,
                **call.parameters,
            )

        return results


tool_executor = ToolExecutor()