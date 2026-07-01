from retriever import retrieve_documents
from llm import generate_answer
from prompts import RAG_PROMPT


def pdf_response(question):

    # results = retrieve_documents(question)
    # 1. Unpack both the results and the clean_question from retriever.py
    results, clean_question = retrieve_documents(question)

    context = ""

    pages = []

    scores = []

    chunks = []

    for doc, score in results:

        context += doc.page_content + "\n\n"

        pages.append(doc.metadata.get("page"))

        scores.append(round(score, 4))

        chunks.append(
            {
                "page": doc.metadata.get("page"),
                "score": round(score, 4),
                "text": doc.page_content[:300],
            }
        )

    prompt = RAG_PROMPT.format(context=context, question=question)

    answer = generate_answer(prompt)

    if answer.lower().startswith("i could not"):

        pages = []
        scores = []
        chunks = []

    confidence = 0

    best = 999

    if scores:
        best = scores[0]

    if best <= 0.60:

        confidence = 99

    elif best <= 0.75:

        confidence = 95

    elif best <= 0.90:

        confidence = 90

    elif best <= 1.10:

        confidence = 82

    elif best <= 1.30:

        confidence = 72

    else:

        confidence = 55
        # confidence = round(max(0, (2 - scores[0]) / 2) * 100)

    return {
        "answer": answer,
        "pages": sorted(list(set(pages))),
        "scores": scores,
        "chunks": chunks,
        "confidence": confidence,
        "best_score": best,
    }
