from ai_core.agents.intent_agent import IntentAgent
from ai_core.agents.response_agent import ResponseAgent
from ai_core.observability.decorators import traced
from ai_core.state.support_state import SupportState

intent_agent = IntentAgent()
response_agent = ResponseAgent()


@traced("intent")
async def intent_node(state: SupportState) -> SupportState:
    return await intent_agent.execute(state)


@traced("response")
async def response_node(state: SupportState) -> SupportState:
    result = await response_agent.execute(state)
    
    if hasattr(state, "_tracer"):
        state._tracer.finish_workflow()
        state.trace = state._tracer.workflow
    
    return result