from ai_core.llm.service import llm_service

from ai_core.models.execution_plan import ExecutionPlan
from ai_core.models.tool_call import ToolCall

from .planner_prompt import PLANNER_PROMPT


class PlannerAgent:

    async def run(
        self,
        query: str,
    ) -> ExecutionPlan:

        try:
            plan = await llm_service.generate_structured(
                prompt=PLANNER_PROMPT,
                output_schema=ExecutionPlan,
                variables={
                    "query": query,
                },
            )
        except Exception:
            plan = self._fallback_plan(query)

        if not getattr(plan, "tool_calls", None):
            plan = self._fallback_plan(query)

        return plan

    def _fallback_plan(self, query: str) -> ExecutionPlan:
        lowered_query = query.lower()
        tool_calls: list[ToolCall] = []

        # Check for escalation keywords first
        escalation_keywords = [
            "angry", "furious", "unacceptable", "manager", "lawyer", "lawsuit", 
            "cancel my account", "sue", "legal action", "escalate", "supervisor",
            "disgusting", "terrible", "horrible", "worst"
        ]
        
        if any(keyword in lowered_query for keyword in escalation_keywords):
            tool_calls.append(
                ToolCall(
                    tool="human_review",
                    parameters={"reason": "Customer expressed frustration or requested escalation"},
                )
            )

        if any(word in lowered_query for word in ["refund", "return", "cancel", "ticket"]):
            tool_calls.append(
                ToolCall(
                    tool="ticket",
                    parameters={"priority": "medium"},
                )
            )

        tool_calls.append(
            ToolCall(
                tool="knowledge",
                parameters={"question": query},
            )
        )

        if any(word in lowered_query for word in ["history", "previous", "before"]):
            tool_calls.append(
                ToolCall(
                    tool="memory",
                    parameters={"conversation_id": "default"},
                )
            )

        return ExecutionPlan(
            reasoning="Fallback planning due to unavailable model",
            tool_calls=tool_calls,
        )