from ai_core.state.support_state import SupportState


class MemoryAgent:
    """
    Loads conversation history into the workflow state.
    The history is now provided by the support service before workflow execution.
    """

    async def run(
        self,
        state: SupportState,
    ) -> SupportState:
        # Conversation history is now loaded in SupportService before workflow execution
        # This agent just passes through the state with the history already set
        if state.conversation_history:
            print(f"MemoryAgent: Using conversation history with {len(state.conversation_history)} characters")
        else:
            print("MemoryAgent: No conversation history available")
        
        return state