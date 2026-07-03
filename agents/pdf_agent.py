from retriever import retrieve_documents
from llm import generate_answer
from prompts import RAG_PROMPT


def pdf_response(results, clean_question):

    # results = retrieve_documents(question)
    # 1. Unpack both the results and the clean_question from retriever.py
    # results = retrieve_documents(clean_question)

    context = ""

    pages = []

    scores = []

    chunks = []

    for doc, score in results:

        # context += doc.page_content + "\n\n"
        context += doc.page_content[:500] + "\n\n"
        # Safely pull the standard "page" key created in ingest.py
        page_num = doc.metadata.get("page")

        # Only append to list if it's a valid page number to keep things clean
        if page_num:
            pages.append(page_num)

        scores.append(round(score, 4))

        chunks.append(
            {
                "page": page_num,
                "score": round(score, 4),
                "text": doc.page_content[:300],
            }
        )

    prompt = RAG_PROMPT.format(context=context, question=clean_question)

    answer = generate_answer(prompt)

    if answer.lower().startswith("i could not"):

        pages = []
        scores = []
        chunks = []

    confidence = 0

    best_dist = 999

    if scores:
        best_dist = scores[0]

    if best_dist <= 0.40:
        confidence = 99
    elif best_dist <= 0.70:
        confidence = 95
    elif best_dist <= 0.95:
        confidence = 88
    elif best_dist <= 1.15:
        confidence = 78
    elif best_dist <= 1.30:
        confidence = 60
    else:
        confidence = 45
        # confidence = round(max(0, (2 - scores[0]) / 2) * 100)

    return {
        "answer": answer,
        "pages": sorted(list(set(pages))),
        "scores": scores,
        "chunks": chunks,
        "confidence": confidence,
        "best_score": best_dist,
    }
