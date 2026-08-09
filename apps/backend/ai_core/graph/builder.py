import asyncio
import logging

from langgraph.graph import StateGraph, START, END

from ai_core.agents.decision import decision_node
from ai_core.agents.memory_agent import MemoryAgent
from ai_core.agents.planner import planner_node
from ai_core.agents.tool_executor import tool_executor_node
from ai_core.graph.nodes import (
    intent_node,
    response_node,
)
from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

engine = DecisionEngine()

graph = StateGraph(SupportState)

memory_agent = MemoryAgent()


def route_after_intent(state: SupportState) -> str:
    """Route after intent detection based on intent type and confidence."""
    if state.intent is None:
        logger.info(f"Route after intent: No intent detected, routing to planner")
        return "planner"
    
    # High-confidence general queries can skip the planner/tool loop entirely
    if (
        state.intent.intent.value == "general_query"
        and state.intent.confidence > 0.85
    ):
        logger.info(f"Route after intent: High-confidence general_query (confidence={state.intent.confidence:.2f}), skipping to response")
        return "response"
    
    logger.info(f"Route after intent: Intent={state.intent.intent.value}, confidence={state.intent.confidence:.2f}, routing to planner")
    return "planner"


def _run_async(func, state: SupportState):
    result = func(state)
    if asyncio.iscoroutine(result):
        return asyncio.run(result)
    return result


def memory_node(state: SupportState) -> SupportState:
    return _run_async(memory_agent.run, state)


def intent_node_sync(state: SupportState) -> SupportState:
    return _run_async(intent_node, state)


def planner_node_sync(state: SupportState) -> SupportState:
    return _run_async(planner_node, state)


def decision_node_sync(state: SupportState) -> SupportState:
    return _run_async(decision_node, state)


def tool_executor_node_sync(state: SupportState) -> SupportState:
    return _run_async(tool_executor_node, state)


def response_node_sync(state: SupportState) -> SupportState:
    return _run_async(response_node, state)


graph.add_node("memory", memory_node)
graph.add_node("intent", intent_node_sync)
graph.add_node("planner", planner_node_sync)
graph.add_node("decision", decision_node_sync)
graph.add_node("tool_executor", tool_executor_node_sync)
graph.add_node("response", response_node_sync)

graph.add_edge(START, "memory")
graph.add_edge("memory", "intent")
graph.add_conditional_edges(
    "intent",
    route_after_intent,
    {"planner": "planner", "response": "response"},
)
graph.add_edge("planner", "decision")
graph.add_edge("decision", "tool_executor")
graph.add_edge("tool_executor", "response")
graph.add_edge("response", END)

compiled_graph = graph.compile()


class SupportGraphWrapper:
    def __init__(self, graph):
        self._graph = graph

    def invoke(self, state: SupportState) -> SupportState:
        result = self._graph.invoke(state)
        if isinstance(result, dict):
            # Handle case where response might be a string instead of ResponseOutput
            if 'response' in result and isinstance(result['response'], str):
                from ai_core.models.response import ResponseOutput
                result['response'] = ResponseOutput(
                    response=result['response'],
                    tone="professional",
                    confidence=0.0,
                    follow_up_actions=[]
                )
            return SupportState(**result)
        return result

    async def ainvoke(self, state: SupportState) -> SupportState:
        result = await self._graph.ainvoke(state)
        if isinstance(result, dict):
            # Handle case where response might be a string instead of ResponseOutput
            if 'response' in result and isinstance(result['response'], str):
                from ai_core.models.response import ResponseOutput
                result['response'] = ResponseOutput(
                    response=result['response'],
                    tone="professional",
                    confidence=0.0,
                    follow_up_actions=[]
                )
            return SupportState(**result)
        return result

    def __getattr__(self, name):
        return getattr(self._graph, name)


support_graph = SupportGraphWrapper(compiled_graph)


def invoke_sync(state: SupportState):
    return support_graph.invoke(state)


def invoke_async(state: SupportState):
    return support_graph.ainvoke(state)
