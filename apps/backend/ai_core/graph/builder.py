from langgraph.graph import StateGraph, START, END

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

graph.add_node("intent", intent_node)
graph.add_node("knowledge", knowledge_node)
graph.add_node("ticket", ticket_node)
graph.add_node("human_review", human_review_node)
graph.add_node("response", response_node)

graph.add_edge(START, "intent")

graph.add_conditional_edges(
    "intent",
    lambda state: engine.route_after_intent(state),
    {
        "knowledge": "knowledge",
        "ticket": "ticket",
    },
)

graph.add_edge("knowledge", "human_review")
graph.add_edge("ticket", "human_review")

graph.add_edge("human_review", "response")

graph.add_edge("response", END)

support_graph = graph.compile()