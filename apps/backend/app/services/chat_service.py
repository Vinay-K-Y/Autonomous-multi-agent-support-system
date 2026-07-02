from ai_core.orchestrator.orchestrator import SupportOrchestrator


class ChatService:

    def __init__(self):

        self.orchestrator = SupportOrchestrator()

    async def process(self, message: str):

        state = {
            "user_query": message,
            "intent": "",
            "confidence": 0,
            "retrieved_documents": [],
            "ticket_required": False,
            "ticket_id": "",
            "final_response": "",
            "escalation_required": False,
        }

        return await self.orchestrator.run(state)