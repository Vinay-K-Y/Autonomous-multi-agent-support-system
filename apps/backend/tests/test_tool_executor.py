import ai_core.tools
from ai_core.tools.executor import tool_executor


def test_tool_registry():
    result = tool_executor.execute(
        "ticket",
        priority="high",
    )
    assert result.ticket_required is True
    assert result.priority == "high"


def test_memory_tool():
    result = tool_executor.execute(
        "memory",
        conversation_id="demo",
    )
    assert isinstance(result, str)
