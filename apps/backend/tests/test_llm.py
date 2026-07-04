import asyncio

from ai_core.llm.client import llm_client


async def main():

    response = await llm_client.ask(
        "What is the capital of India?"
    )

    print(response)


asyncio.run(main())