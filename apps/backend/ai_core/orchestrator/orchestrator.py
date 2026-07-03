from ai_core.orchestrator.agent_registry import AgentRegistry
from ai_core.state.support_state import SupportState
from ai_core.orchestrator.workflow_router import WorkflowRouter

class SupportOrchestrator:
    """
    Executes the customer support workflow.

    The orchestrator coordinates agents but does not contain
    business logic itself.
    """

    def __init__(self):

        self.registry = AgentRegistry()
        self.router = WorkflowRouter()


    async def run(self, state: SupportState) -> SupportState:

        workflow = [
            "intent",
            "knowledge",
            "ticket",
            "human_review",
            "response",
        ]

        for agent_name in workflow:

            state.workflow.current_agent = agent_name

            agent = self.registry.get(agent_name)

            state = await agent.execute(state)

            state.workflow.completed_agents.append(agent_name)

        state.workflow.current_agent = None
        state.workflow.status = "completed"

        return state