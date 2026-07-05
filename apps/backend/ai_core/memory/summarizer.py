class ConversationSummarizer:
    """
    Future component.

    Will summarize long conversations
    before they exceed the model context.
    """

    def summarize(
        self,
        history: str,
    ) -> str:

        return history