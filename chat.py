from retriever import retrieve_documents
from llm import generate_answer
from prompts import RAG_PROMPT

print("\n========== RAG Chatbot ==========\n")

while True:

    question = input("Ask a question (type 'exit' to quit): ")

    if question.lower() == "exit":
        print("\nGoodbye!")
        break

    # ----------------------------
    # Retrieve Documents
    # ----------------------------

    results = retrieve_documents(question)

    context = ""
    pages = set()

    print("\nRetrieved Pages:")

    for doc, score in results:

        page = doc.metadata.get("page")

        pages.add(page)

        print(f"Page {page} | Score: {score:.4f}")

        context += doc.page_content + "\n\n"

    # ----------------------------
    # Build Prompt
    # ----------------------------

    prompt = RAG_PROMPT.format(context=context, question=question)

    # ----------------------------
    # Generate Answer
    # ----------------------------

    answer = generate_answer(prompt)

    print("\n==============================")
    print("Answer")
    print("==============================\n")

    print(answer)

    print("\nSource Pages:")

    print(sorted(list(pages)))

    print("\n")
