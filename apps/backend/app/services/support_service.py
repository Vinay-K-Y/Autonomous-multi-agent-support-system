import logging

from app.mappers import SupportMapper
from app.services.workflow_executor import WorkflowExecutor
from app.services.analytics_service import analytics_service
from ai_core.factories import SupportStateFactory
from ai_core.memory.conversation_manager import conversation_manager
from app.db import AsyncSessionLocal, database_available
import asyncio

logger = logging.getLogger(__name__)


class SupportService:

    def __init__(self):
        self.executor = WorkflowExecutor()
        # Use the same singleton conversation_manager that MemoryTool uses
        # This ensures single source of truth for conversation memory
        self.conversation_manager = conversation_manager
        self.use_db_memory = database_available

    async def process_request(
        self,
        message: str,
        customer_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
        channel: str = "web",
    ):
        # Use the singleton conversation_manager for consistency with MemoryTool
        conv_manager = self.conversation_manager

        # If using database, get a DB session
        db_session = None
        if self.use_db_memory:
            db_session = AsyncSessionLocal()
            # Switch conversation manager to DB mode with session
            from ai_core.memory.conversation_manager import ConversationManager
            conv_manager = ConversationManager(use_db=True, db_session=db_session)

        try:
            # 1. Save user message to conversation history
            if conversation_id:
                if self.use_db_memory and db_session:
                    await conv_manager.add_user_message(conversation_id, message, db_session=db_session)
                else:
                    conv_manager.add_user_message(conversation_id, message)

            # 2. Load conversation history if available
            conversation_history = None
            if conversation_id:
                if self.use_db_memory and db_session:
                    history = await conv_manager.history(conversation_id, db_session=db_session)
                else:
                    history = conv_manager.history(conversation_id)
                    
                if history and history.messages:
                    if self.use_db_memory and db_session:
                        conversation_history = await conv_manager.formatted_history(conversation_id, db_session=db_session)
                    else:
                        conversation_history = conv_manager.formatted_history(conversation_id)
                    logger.debug(f"Loaded conversation history for {conversation_id}: {len(history.messages)} messages")

            # 3. Initialize state using the factory with conversation history
            initial_state = SupportStateFactory.create(
                message=message,
                customer_id=customer_id,
                conversation_id=conversation_id,
                language=language,
                channel=channel,
                conversation_history=conversation_history,
            )

            # 4. Execute the workflow (make async for DB compatibility)
            state = await self.executor.execute_async(initial_state)

            # 5. Record metrics for analytics
            analytics_service.record_request(state)

            # 5b. Log this decision's confidence/threshold/outcome shell for
            # adaptive recalibration. outcome_correct is left unlabeled here
            # (we don't know yet whether the decision was right) — it gets
            # filled in later via the feedback endpoint once ground truth
            # is available. See ai_core/calibration/outcome_store.py and
            # ADAPTIVE_THRESHOLDS.md.
            if state.intent is not None and state.decision is not None:
                from ai_core.calibration.outcome_store import log_outcome

                try:
                    log_outcome(
                        request_id=state.metadata.request_id,
                        confidence=state.intent.confidence,
                        threshold_used=(
                            state.decision.escalation_threshold_used
                            if state.decision.escalation_threshold_used is not None
                            else 0.0
                        ),
                        was_escalated=(
                            state.human_review.required if state.human_review else False
                        ),
                    )
                except Exception:
                    # Outcome logging must never break a live request.
                    logger.exception("Failed to log calibration outcome record")

            # 6. Save assistant response to conversation history
            if conversation_id and state.response:
                if self.use_db_memory and db_session:
                    await conv_manager.add_assistant_message(conversation_id, state.response.response, db_session=db_session)
                else:
                    conv_manager.add_assistant_message(conversation_id, state.response.response)

            # 6. Map the final state directly to the response object
            return SupportMapper.to_response(state)
        finally:
            # Clean up DB session if we created one
            if db_session:
                await db_session.close()