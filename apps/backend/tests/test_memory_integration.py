from ai_core.memory.conversation_manager import conversation_manager


def test_memory_integration():
    conversation_manager.clear("demo")
    conversation_manager.add_user_message(
        "demo",
        "My laptop is damaged.",
    )
    conversation_manager.add_assistant_message(
        "demo",
        "I'm sorry to hear that.",
    )
    history = conversation_manager.formatted_history("demo")

    assert "damaged" in history
    assert "sorry" in history
