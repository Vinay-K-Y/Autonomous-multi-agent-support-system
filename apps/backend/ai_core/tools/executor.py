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

        return tool.execute(**kwargs)

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