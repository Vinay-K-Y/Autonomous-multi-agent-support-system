"""Tests for LLM call tracking across agents.

This tests the fix for the bug where increment_llm_calls() was only called
from intent_agent.py, but not from PlannerAgent, ResponseAgent, or the RAG
pipeline — causing state.metadata.llm_call_count to always report 1 regardless
of the actual number of LLM calls made.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from ai_core.agents.response_agent import ResponseAgent
from ai_core.agents.planner import PlannerAgent
from ai_core.factories.support_state_factory import SupportStateFactory
from ai_core.models.response import ResponseOutput
from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.tool_call import ToolCall


class TestResponseAgentLLMCallTracking:
    """Test that ResponseAgent correctly tracks LLM calls vs fallbacks."""

    @pytest.mark.asyncio
    async def test_successful_llm_call_increments_count(self):
        """When ResponseAgent's LLM call succeeds, llm_call_count increments by 1."""
        state = SupportStateFactory.create(message="Test message")
        initial_count = state.metadata.llm_call_count

        with patch("ai_core.agents.response_agent.llm_service.generate_structured") as mock_llm:
            mock_llm.return_value = ResponseOutput(
                response="Test response",
                tone="professional",
                confidence=0.9,
            )

            agent = ResponseAgent()
            await agent.execute(state)

            # Should have incremented by exactly 1
            assert state.metadata.llm_call_count == initial_count + 1
            # Fallback count should not have changed
            assert state.metadata.llm_fallback_count == 0

    @pytest.mark.asyncio
    async def test_llm_fallback_does_not_increment_count(self):
        """When ResponseAgent falls back, llm_call_count does NOT increment, but llm_fallback_count does."""
        state = SupportStateFactory.create(message="Test message")
        initial_llm_count = state.metadata.llm_call_count
        initial_fallback_count = state.metadata.llm_fallback_count

        with patch("ai_core.agents.response_agent.llm_service.generate_structured") as mock_llm:
            mock_llm.side_effect = Exception("LLM failed")

            agent = ResponseAgent()
            await agent.execute(state)

            # LLM call count should NOT have incremented
            assert state.metadata.llm_call_count == initial_llm_count
            # Fallback count should have incremented
            assert state.metadata.llm_fallback_count == initial_fallback_count + 1


class TestPlannerAgentLLMCallTracking:
    """Test that PlannerAgent correctly tracks LLM calls vs fallbacks."""

    @pytest.mark.asyncio
    async def test_successful_llm_call_increments_count(self):
        """When PlannerAgent's LLM call succeeds, llm_call_count increments by 1."""
        state = SupportStateFactory.create(message="Test message")
        initial_count = state.metadata.llm_call_count

        with patch("ai_core.planner.planner.llm_service.generate_structured") as mock_llm:
            mock_llm.return_value = ExecutionPlan(
                reasoning="Test reasoning",
                tool_calls=[ToolCall(tool="knowledge", parameters={"question": "test"})],
            )

            planner = PlannerAgent()
            plan = await planner.run(state.request.message)

            # Plan should not have used fallback
            assert not plan.used_fallback

            # Now run through planner_node to test the tracking
            from ai_core.agents.planner import planner_node
            state = await planner_node(state)

            # Should have incremented by exactly 1
            assert state.metadata.llm_call_count == initial_count + 1
            # Fallback count should not have changed
            assert state.metadata.llm_fallback_count == 0

    @pytest.mark.asyncio
    async def test_llm_fallback_does_not_increment_count(self):
        """When PlannerAgent falls back, llm_call_count does NOT increment, but llm_fallback_count does."""
        state = SupportStateFactory.create(message="Test message")
        initial_llm_count = state.metadata.llm_call_count
        initial_fallback_count = state.metadata.llm_fallback_count

        with patch("ai_core.planner.planner.llm_service.generate_structured") as mock_llm:
            mock_llm.side_effect = Exception("LLM failed")

            planner = PlannerAgent()
            plan = await planner.run(state.request.message)

            # Plan should have used fallback
            assert plan.used_fallback

            # Now run through planner_node to test the tracking
            from ai_core.agents.planner import planner_node
            state = await planner_node(state)

            # LLM call count should NOT have incremented
            assert state.metadata.llm_call_count == initial_llm_count
            # Fallback count should have incremented
            assert state.metadata.llm_fallback_count == initial_fallback_count + 1
