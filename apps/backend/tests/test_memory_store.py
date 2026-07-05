from ai_core.memory.memory_store import MemoryStore
from ai_core.memory.models import ConversationMessage


def test_memory_store():

    store = MemoryStore()

    store.add_message(
        "conv-1",
        ConversationMessage(
            role="user",
            content="Hello"
        )
    )

    history = store.get("conv-1")

    assert len(history.messages) == 1
    assert history.messages[0].content == "Hello"