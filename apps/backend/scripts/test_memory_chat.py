from ai_core.rag.pipeline import RAGPipeline


def main() -> None:
    rag = RAGPipeline()
    conversation = ""

    while True:
        question = input("You: ")
        if question.strip().lower() in {"exit", "quit"}:
            break

        answer = rag.ask(question, conversation)
        print("Bot:", answer)
        conversation += f"\nUSER: {question}"
        conversation += f"\nASSISTANT: {answer}\n"


if __name__ == "__main__":
    main()
