import logging
from typing import Callable, TypeVar, Any
from functools import wraps
from ai_core.models.intent import IntentOutput
from ai_core.models.knowledge import KnowledgeOutput, KnowledgeSource
from ai_core.models.ticket import TicketOutput
from ai_core.models.response import ResponseOutput

logger = logging.getLogger(__name__)

T = TypeVar('T')


class AgentError(Exception):
    """Base exception for agent errors"""
    def __init__(self, agent_name: str, original_error: Exception):
        self.agent_name = agent_name
        self.original_error = original_error
        super().__init__(f"Agent {agent_name} failed: {str(original_error)}")


def with_fallback(
    agent_name: str,
    fallback_value: Any,
    log_error: bool = True,
) -> Callable:
    """
    Decorator to add error handling and fallbacks to agent methods.
    
    Usage:
        @with_fallback("intent_agent", IntentOutput(intent="general", confidence=0.5, reasoning="Fallback"))
        async def intent_agent_execute(state: SupportState) -> SupportState:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Agent {agent_name} failed: {type(e).__name__}: {str(e)}",
                        exc_info=True
                    )
                # If the first argument is a SupportState, return it with the fallback value
                if args and hasattr(args[0], '__class__') and args[0].__class__.__name__ == 'SupportState':
                    state = args[0]
                    # Set the appropriate field based on agent name
                    if agent_name == "response_agent":
                        state.response = fallback_value
                    elif agent_name == "intent_agent":
                        state.intent = fallback_value
                    elif agent_name == "knowledge_agent":
                        state.knowledge = fallback_value
                    elif agent_name == "ticket_agent":
                        state.ticket = fallback_value
                    return state
                return fallback_value
        return wrapper
    return decorator


# Fallback values for each agent
INTENT_FALLBACK = IntentOutput(
    intent="general_query",
    confidence=0.3,
    reasoning="Fallback due to agent error"
)

KNOWLEDGE_FALLBACK = KnowledgeOutput(
    answer="I apologize, but I'm unable to retrieve information from the knowledge base at this time. Please try again later.",
    confidence=0.0,
    sources=[
        KnowledgeSource(
            title="System Error",
            source="fallback",
            confidence=0.0
        )
    ]
)

TICKET_FALLBACK = TicketOutput(
    ticket_required=False,
    ticket_id=None,
    priority="low",
    assigned_team=None
)

RESPONSE_FALLBACK = ResponseOutput(
    response="I apologize, but I encountered an error processing your request. Please try again or contact support directly.",
    tone="professional",
    follow_up_actions=[],
    confidence=0.0
)


def safe_execute_agent(
    agent_func: Callable,
    agent_name: str,
    fallback_value: Any,
    *args,
    **kwargs
) -> Any:
    """
    Safely execute an agent function with error handling and fallback.
    This is a synchronous version for use in non-async contexts.
    """
    try:
        result = agent_func(*args, **kwargs)
        # If it's a coroutine, we need to await it
        if hasattr(result, '__await__'):
            import asyncio
            return asyncio.run(result)
        return result
    except Exception as e:
        logger.error(
            f"Agent {agent_name} failed: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        return fallback_value
