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

        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Executing tool: {tool_name}")
        logger.info(f"Available kwargs: {kwargs.keys()}")
        logger.info(f"Method signature: {signature}")

        normalized_kwargs = {}
        for name, parameter in signature.parameters.items():
            if name == "self":
                continue
            if name in kwargs:
                normalized_kwargs[name] = kwargs[name]
            elif name == "question":
                # Try multiple possible parameter names for question
                if "query" in kwargs:
                    normalized_kwargs[name] = kwargs["query"]
                elif "message" in kwargs:
                    normalized_kwargs[name] = kwargs["message"]
                elif "question" in kwargs:
                    normalized_kwargs[name] = kwargs["question"]
                elif parameter.default != inspect.Parameter.empty:
                    normalized_kwargs[name] = parameter.default
                else:
                    # Last resort: use empty string if no default
                    normalized_kwargs[name] = ""
            elif name == "conversation" and "conversation_id" in kwargs:
                normalized_kwargs[name] = kwargs["conversation_id"]
            elif parameter.default != inspect.Parameter.empty:
                # Use default value if parameter is missing and has a default
                normalized_kwargs[name] = parameter.default
        
        logger.info(f"Normalized kwargs: {normalized_kwargs}")

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