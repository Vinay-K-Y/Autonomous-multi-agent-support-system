from ai_core.llm.factory import LLMFactory

provider = LLMFactory.create()

print(type(provider))