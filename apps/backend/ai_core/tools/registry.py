from ai_core.tools.base_tool import BaseTool


class ToolRegistry:

    def __init__(self):

        self.tools: dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ):

        self.tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> BaseTool:

        if name not in self.tools:
            raise ValueError(
                f"Unknown tool: {name}"
            )

        return self.tools[name]


tool_registry = ToolRegistry()