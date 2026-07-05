from ai_core.tools.registry import tool_registry


class ToolExecutor:
    """
    Executes registered tools.
    """

    def execute(
        self,
        tool_name: str,
        **kwargs,
    ):

        tool = tool_registry.get(tool_name)

        return tool.execute(**kwargs)


tool_executor = ToolExecutor()