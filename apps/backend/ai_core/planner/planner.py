from ai_core.llm.service import llm_service

from ai_core.models.execution_plan import ExecutionPlan

from .planner_prompt import PLANNER_PROMPT


class PlannerAgent:

    async def run(
        self,
        query: str,
    ) -> ExecutionPlan:

        plan = await llm_service.generate_structured(
            prompt=PLANNER_PROMPT,
            output_schema=ExecutionPlan,
            variables={
                "query": query,
            },
        )

        return plan