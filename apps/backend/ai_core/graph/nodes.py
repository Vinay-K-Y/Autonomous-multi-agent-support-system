from ai_core.agents.intent_agent import IntentAgent
from ai_core.agents.knowledge_agent import KnowledgeAgent
from ai_core.agents.ticket_agent import TicketAgent
from ai_core.agents.human_review_agent import HumanReviewAgent
from ai_core.agents.response_agent import ResponseAgent
from ai_core.observability.decorators import traced
from ai_core.state.support_state import SupportState

intent_agent = IntentAgent()
knowledge_agent = KnowledgeAgent()
ticket_agent = TicketAgent()
human_review_agent = HumanReviewAgent()
response_agent = ResponseAgent()


@traced("intent")
async def intent_node(state: SupportState) -> SupportState:
    return await intent_agent.execute(state)


@traced("knowledge")
async def knowledge_node(state: SupportState) -> SupportState:
    return await knowledge_agent.execute(state)


@traced("ticket")
async def ticket_node(state: SupportState) -> SupportState:
    return await ticket_agent.execute(state)


async def human_review_node(state: SupportState) -> SupportState:
    return await human_review_agent.execute(state)


@traced("response")
async def response_node(state: SupportState) -> SupportState:
    result = await response_agent.execute(state)
    
    if hasattr(state, "_tracer"):
        state._tracer.finish_workflow()
        state.trace = state._tracer.workflow
    
    return result