import logging

from ai_core.observability.decorators import traced
from ai_core.state.support_state import SupportState

from ai_core.models.human_review import HumanReview
from ai_core.models.ticket import TicketOutput
from ai_core.tools.executor import tool_executor

logger = logging.getLogger(__name__)


@traced("tool_executor")
async def tool_executor_node(
    state: SupportState,
) -> SupportState:

    if state.execution_plan is None:
        return state

    if state.decision is None:
        return state

    if not state.decision.approved:
        return state

    plan = state.decision.modified_plan or state.execution_plan

    try:
        results = tool_executor.execute_plan(plan, state=state)
    except Exception as e:
        # One misbehaving tool call shouldn't take down the whole request.
        logger.error(f"Tool execution failed: {type(e).__name__}: {e}", exc_info=True)
        state.metadata.routing_reasons.append(f"tool execution failed: {e}")
        return state

    state.tool_results = results
    state.metadata.routing_reasons.append("tools executed")

    # Sync individual tool outputs onto state so downstream consumers
    # (SupportMapper, API response) actually see them, not just the
    # opaque tool_results dict.
    if "human_review" in results:
        review = results["human_review"]
        state.human_review = (
            review if isinstance(review, HumanReview) else HumanReview(**review)
        )

    if "ticket" in results:
        ticket = results["ticket"]
        state.ticket = (
            ticket if isinstance(ticket, TicketOutput) else TicketOutput(**ticket)
        )

    return state
