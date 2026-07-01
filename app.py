import time

from flask import Flask, render_template, request, jsonify

from retriever import retrieve_documents, best_score
from agents.scope_agent import scope_response
from agents.pdf_agent import pdf_response
from agents.greeting_agent import greeting_response


from config import SIMILARITY_THRESHOLD

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    total_start = time.perf_counter()

    data = request.get_json()

    question = data["question"]

    # -------------------------
    # Step 1 : Retrieval
    # -------------------------

    embedding_start = time.perf_counter()

    # results = retrieve_documents(question)
    # Unpack both the search results and the typo-fixed question
    results, clean_question = retrieve_documents(question)

    embedding_end = time.perf_counter()

    retrieval_start = embedding_start
    retrieval_end = embedding_end

    score = best_score(results)

    print("\n==========================")
    print("QUESTION :", question)
    print("BEST SCORE :", score)
    print("==========================")

    # -------------------------
    # Step 2 : PDF Route
    # -------------------------

    if score <= SIMILARITY_THRESHOLD:

        llm_start = time.perf_counter()

        result = pdf_response(question)

        llm_end = time.perf_counter()

        total_end = time.perf_counter()
        best = score if score is not None else 999
        return jsonify(
            {
                "agent": "PDF RAG Agent",
                "answer": result["answer"],
                "pages": result["pages"],
                "scores": result["scores"],
                "best_score": best,
                "confidence": result["confidence"],
                "chunks": result["chunks"],
                "runtime": {
                    "embedding": round(embedding_end - embedding_start, 3),
                    "retrieval": round(retrieval_end - retrieval_start, 3),
                    "llm": round(llm_end - llm_start, 3),
                    "total": round(total_end - total_start, 3),
                },
                "pipeline": [
                    "Question",
                    "Embedding",
                    "Vector Search",
                    "Similarity Check",
                    "Router",
                    "PDF Agent",
                    "LLM",
                    "Final Answer",
                ],
            }
        )

    # -------------------------
    # Step 3 : Greeting
    # -------------------------
    q = question.lower().strip()

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "thanks",
        "thank you",
        "bye",
        "how are you",
    ]

    if q in greetings:
        total_end = time.perf_counter()
        return jsonify(
            {
                "agent": "Greeting Agent",
                "answer": greeting_response(),
                "pages": [],
                "scores": [],
                "best_score": score,
                "chunks": [],
                "confidence": 100,
                "runtime": {
                    "embedding": round(embedding_end - embedding_start, 3),
                    "retrieval": round(retrieval_end - retrieval_start, 3),
                    "llm": 0,
                    "total": round(total_end - total_start, 3),
                },
                "pipeline": [
                    "Question",
                    "Embedding",
                    "Vector Search",
                    "Similarity Check",
                    "Router",
                    "Greeting Agent",
                    "Final Answer",
                ],
            }
        )

    # -------------------------
    # Step 4 : Unknown
    # -------------------------
    total_end = time.perf_counter()
    return jsonify(
        {
            "agent": "Scope Guard",
            "answer": scope_response(),
            "pages": [],
            "scores": [],
            "best_score": score,
            "chunks": [],
            "confidence": 100,
            "runtime": {
                "embedding": round(embedding_end - embedding_start, 3),
                "retrieval": round(retrieval_end - retrieval_start, 3),
                "llm": 0,
                "total": round(total_end - total_start, 3),
            },
            "pipeline": [
                "Question",
                "Embedding",
                "Vector Search",
                "Similarity Check",
                "Router",
                "Scope Agent",
                "Final Answer",
            ],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
