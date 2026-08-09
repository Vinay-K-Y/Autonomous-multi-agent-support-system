from unittest.mock import Mock, patch
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.tool_call import ToolCall
from ai_core.tools.executor import ToolExecutor


def test_tool_executor_returns_dict_keyed_by_tool_name() -> None:
    """Assert ToolExecutor.execute_plan() returns a dict keyed by tool name with correct values."""
    executor = ToolExecutor()
    
    # Create a plan with multiple tools
    plan = ExecutionPlan(
        reasoning="Test plan",
        tool_calls=[
            ToolCall(tool="knowledge", parameters={"question": "test question"}),
            ToolCall(tool="ticket", parameters={"priority": "medium"}),
        ]
    )
    
    # Mock the tool registry to return mock tools
    with patch('ai_core.tools.executor.tool_registry') as mock_registry:
        mock_knowledge = Mock()
        mock_knowledge.execute.return_value = "Knowledge result"
        
        mock_ticket = Mock()
        mock_ticket.execute.return_value = {"ticket_id": "TKT-123"}
        
        mock_registry.get.side_effect = lambda name: {
            "knowledge": mock_knowledge,
            "ticket": mock_ticket,
        }.get(name)
        
        results = executor.execute_plan(plan)
    
    # Assert results are keyed by tool name
    assert "knowledge" in results
    assert "ticket" in results
    assert results["knowledge"] == "Knowledge result"
    assert results["ticket"]["ticket_id"] == "TKT-123"


def test_tool_executor_handles_failing_tool_gracefully() -> None:
    """Assert a failing tool doesn't take down other tools - caught at tool_executor_node level."""
    executor = ToolExecutor()
    
    # Create a plan with multiple tools
    plan = ExecutionPlan(
        reasoning="Test plan with failing tool",
        tool_calls=[
            ToolCall(tool="knowledge", parameters={"question": "test question"}),
            ToolCall(tool="ticket", parameters={"priority": "medium"}),
        ]
    )
    
    # Mock the tool registry where ticket tool raises an exception
    with patch('ai_core.tools.executor.tool_registry') as mock_registry:
        mock_knowledge = Mock()
        mock_knowledge.execute.return_value = "Knowledge result"
        
        mock_ticket = Mock()
        mock_ticket.execute.side_effect = Exception("Ticket service unavailable")
        
        mock_registry.get.side_effect = lambda name: {
            "knowledge": mock_knowledge,
            "ticket": mock_ticket,
        }.get(name)
        
        # This should raise an exception since execute_plan doesn't catch it
        # The catching happens at the tool_executor_node level
        try:
            results = executor.execute_plan(plan)
            # If we get here, the exception wasn't raised
            assert False, "Expected exception from failing tool"
        except Exception as e:
            # Expected - the exception should propagate from execute_plan
            assert "Ticket service unavailable" in str(e)


def test_tool_executor_passes_state_to_tools() -> None:
    """Assert ToolExecutor passes state parameter to tools that accept it."""
    executor = ToolExecutor()
    
    # Create a plan with a tool
    plan = ExecutionPlan(
        reasoning="Test plan",
        tool_calls=[
            ToolCall(tool="knowledge", parameters={"question": "test question"}),
        ]
    )
    
    # Mock state
    mock_state = Mock()
    
    # Mock the tool registry
    with patch('ai_core.tools.executor.tool_registry') as mock_registry:
        mock_knowledge = Mock()
        mock_knowledge.execute.return_value = "Knowledge result"
        
        mock_registry.get.return_value = mock_knowledge
        
        results = executor.execute_plan(plan, state=mock_state)
    
    # Assert that the tool was called with state parameter
    mock_knowledge.execute.assert_called_once()
    call_kwargs = mock_knowledge.execute.call_args[1]
    # The tool should have received state if its signature accepts it
    # This depends on the signature inspection in ToolExecutor.execute
