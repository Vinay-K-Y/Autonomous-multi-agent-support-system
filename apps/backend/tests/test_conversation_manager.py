from ai_core.memory.conversation_manager import ConversationManager


def test_conversation_manager():

    manager = ConversationManager()

    manager.add_user_message(
        "abc",
        "Hello"
    )

    manager.add_assistant_message(
        "abc",
        "Hi!"
    )

    history = manager.formatted_history(
        "abc"
    )

    assert "USER: Hello" in history
    assert "ASSISTANT: Hi!" in history