from ai_core.llm.service import llm_service


class LLMClient:
    async def ask(self, prompt: str) -> str:
        try:
            return await llm_service.get().ainvoke(prompt)
        except Exception:
            return "I’m unable to reach the language model right now, but I can still help."


llm_client = LLMClient()
