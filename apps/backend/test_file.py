import asyncio
from uuid import uuid4

from ai_core.agents.intent_agent import IntentAgent
from ai_core.models.customer_request import CustomerRequest
from ai_core.models.metadata import ProcessingMetadata
from ai_core.state.support_state import SupportState


async def main():

    state = SupportState(
        request=CustomerRequest(
            message="My laptop is damaged and I want a refund.",
            customer_id="CUST-001",
            conversation_id="CONV-001",
        ),
        metadata=ProcessingMetadata(
            request_id=str(uuid4()),
        ),
    )

    agent = IntentAgent()

    updated_state = await agent.execute(state)

    print(updated_state.model_dump_json(indent=4))


asyncio.run(main())