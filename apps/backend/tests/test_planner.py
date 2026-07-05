import pytest

from ai_core.planner.planner import PlannerAgent


@pytest.mark.asyncio
async def test_planner():

    planner = PlannerAgent()

    plan = await planner.run(
        "How do I get a refund?"
    )

    print()

    print(plan)

    assert len(plan.tool_calls) > 0