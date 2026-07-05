from ai_core.tools.registry import tool_registry

from ai_core.tools.knowledge_tool import KnowledgeTool
from ai_core.tools.ticket_tool import TicketTool
from ai_core.tools.memory_tool import MemoryTool
from ai_core.tools.human_review_tool import HumanReviewTool

tool_registry.register(KnowledgeTool())
tool_registry.register(TicketTool())
tool_registry.register(MemoryTool())
tool_registry.register(HumanReviewTool())