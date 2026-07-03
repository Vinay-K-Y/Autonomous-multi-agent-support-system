import asyncio

from ai_core.llm.gemini import GeminiProvider


async def main():
    provider = GeminiProvider()

    response = await provider.generate(
        "Say hello in exactly five words."
    )

    print(response)


asyncio.run(main())