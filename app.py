# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)


# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/chat", methods=["POST"])
# def chat():

#     data = request.get_json()

#     question = data["question"]

#     print(f"\nUser Asked: {question}")

#     return jsonify({"answer": f"You asked: {question}"})


# if __name__ == "__main__":
#     app.run(debug=True)
import time
from flask import Flask, render_template, request, jsonify
from retriever import retrieve_documents
from llm import generate_answer
from prompts import RAG_PROMPT

# from config import SIMILARITY_THRESHOLD

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    total_start = time.perf_counter()

    data = request.get_json()

    question = data["question"]

    # -----------------------------
    # Retrieval
    # -----------------------------

    retrieval_start = time.perf_counter()

    results = retrieve_documents(question)

    retrieval_end = time.perf_counter()

    context = ""

    pages = []

    scores = []

    for doc, score in results:

        context += doc.page_content + "\n\n"

        pages.append(doc.metadata.get("page"))

        scores.append(round(score, 4))

    # -----------------------------
    # Prompt
    # -----------------------------

    prompt_start = time.perf_counter()

    prompt = RAG_PROMPT.format(context=context, question=question)

    prompt_end = time.perf_counter()

    # -----------------------------
    # LLM
    # -----------------------------

    llm_start = time.perf_counter()

    answer = generate_answer(prompt)

    llm_end = time.perf_counter()

    # -----------------------------

    if answer.lower().startswith("i could not find"):

        pages = []

        scores = []

    total_end = time.perf_counter()

    return jsonify(
        {
            "answer": answer,
            "pages": sorted(list(set(pages))),
            "scores": scores,
            "runtime": {
                "retrieval": round(retrieval_end - retrieval_start, 3),
                "prompt": round(prompt_end - prompt_start, 3),
                "llm": round(llm_end - llm_start, 3),
                "total": round(total_end - total_start, 3),
            },
        }
    )


# @app.route("/chat", methods=["POST"])
# def chat():

#     data = request.get_json()

#     question = data["question"]

#     # -----------------------------
#     # Retrieve Documents
#     # -----------------------------

#     results = retrieve_documents(question)

#     # filtered_results = []

#     # for doc, score in results:

#     #     if score < SIMILARITY_THRESHOLD:

#     #         filtered_results.append((doc, score))

#     # -----------------------------
#     # No Relevant Chunks Found
#     # -----------------------------

#     # if len(filtered_results) == 0:

#     #     return jsonify(
#     #         {
#     #             "answer": "I could not find this information in the provided document.",
#     #             "pages": [],
#     #             "scores": [],
#     #         }
#     #     )

#     # -----------------------------
#     # Build Context
#     # -----------------------------

#     context = ""

#     pages = []

#     scores = []

#     # for doc, score in filtered_results:

#     #     context += doc.page_content + "\n\n"

#     #     pages.append(doc.metadata.get("page"))

#     #     scores.append(round(score, 4))

#     for doc, score in results:

#         context += doc.page_content + "\n\n"

#         pages.append(doc.metadata.get("page"))
#         scores.append(round(score, 4))

#     # -----------------------------
#     # Prompt
#     # -----------------------------

#     prompt = RAG_PROMPT.format(context=context, question=question)

#     # -----------------------------
#     # Generate Answer
#     # -----------------------------

#     answer = generate_answer(prompt)

#     if answer.lower().startswith("i could not find"):

#         pages = []

#         scores = []

#     return jsonify(
#         {"answer": answer, "pages": sorted(list(set(pages))), "scores": scores}
#     )

#     # return jsonify(
#     #     {"answer": answer, "pages": sorted(list(set(pages))), "scores": scores}
#     # )


if __name__ == "__main__":
    app.run(debug=True)
