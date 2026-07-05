import asyncio

from langgraph.graph import StateGraph, START, END

from ai_core.agents.memory_agent import MemoryAgent
from ai_core.agents.planner import planner_node
from ai_core.agents.tool_executor import tool_executor_node
from ai_core.graph.nodes import (
    intent_node,
    knowledge_node,
    ticket_node,
    human_review_node,
    response_node,
)
from ai_core.state.support_state import SupportState
from ai_core.workflow.decision_engine import DecisionEngine

engine = DecisionEngine()

graph = StateGraph(SupportState)

memory_agent = MemoryAgent()


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


def tool_executor_node_sync(state: SupportState) -> SupportState:
    return _run_async(tool_executor_node, state)


def knowledge_node_sync(state: SupportState) -> SupportState:
    return _run_async(knowledge_node, state)


def ticket_node_sync(state: SupportState) -> SupportState:
    return _run_async(ticket_node, state)


def human_review_node_sync(state: SupportState) -> SupportState:
    return _run_async(human_review_node, state)


def response_node_sync(state: SupportState) -> SupportState:
    return _run_async(response_node, state)


graph.add_node("memory", memory_node)
graph.add_node("intent", intent_node_sync)
graph.add_node("planner", planner_node_sync)
graph.add_node("tool_executor", tool_executor_node_sync)
graph.add_node("knowledge", knowledge_node_sync)
graph.add_node("ticket", ticket_node_sync)
graph.add_node("human_review", human_review_node_sync)
graph.add_node("response", response_node_sync)

graph.add_edge(START, "memory")
graph.add_edge("memory", "intent")
graph.add_edge("intent", "planner")
graph.add_edge("planner", "tool_executor")
graph.add_edge("tool_executor", "response")
graph.add_edge("response", END)

compiled_graph = graph.compile()


class SupportGraphWrapper:
    def __init__(self, graph):
        self._graph = graph

    def invoke(self, state: SupportState) -> SupportState:
        result = self._graph.invoke(state)
        if isinstance(result, dict):
            return SupportState(**result)
        return result

    async def ainvoke(self, state: SupportState) -> SupportState:
        result = await self._graph.ainvoke(state)
        if isinstance(result, dict):
            return SupportState(**result)
        return result

    def __getattr__(self, name):
        return getattr(self._graph, name)


support_graph = SupportGraphWrapper(compiled_graph)


def invoke_sync(state: SupportState):
    return support_graph.invoke(state)
