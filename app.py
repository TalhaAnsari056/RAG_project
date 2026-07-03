import time
import json
from flask import Flask, render_template, request, jsonify

from retriever import retrieve_documents, best_score
from agents.scope_agent import scope_response
from agents.pdf_agent import pdf_response
from agents.greeting_agent import greeting_response

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from config import SIMILARITY_THRESHOLD, ROUTER_MODEL

app = Flask(__name__)

# Initialize your local router model (qwen2.5:0.5b)
router_llm = Ollama(model=ROUTER_MODEL, temperature=0.0)

# 1. Update the Prompt Template (No more JSON!)
# Prompt 1: Strict Classification (Returns ONLY one word)
intent_prompt = PromptTemplate.from_template(
    "You are a routing assistant. Classify the user query into exactly ONE of these categories:\n"
    "- GREETING: Casual hello, hi, how are you, thanks, good morning.\n"
    "- PDF_POLICY: Questions about company rules, leaves, insurance, hr policies.\n"
    "- OUT_OF_SCOPE: Random topics (cooking, coding, sports, history).\n\n"
    "Respond with ONLY the category name. Do not include any other text.\n\n"
    "Query: {user_query}\n"
    "Category:"
)

# Prompt 2: Strict Typo Fixer
typo_prompt = PromptTemplate.from_template(
    "You are a text correction assistant. Fix any spelling mistakes or typos in this query "
    "so it is ready for semantic search. Respond with ONLY the corrected text.\n\n"
    "Query: {user_query}\n"
    "Corrected Query:"
)

intent_chain = intent_prompt | router_llm
typo_chain = typo_prompt | router_llm


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    total_start = time.perf_counter()
    data = request.get_json()
    question = data["question"]

    # # -------------------------
    # # Step 1 : Retrieval
    # # -------------------------

    embedding_start = time.perf_counter()

    # results = retrieve_documents(question)
    # Unpack both the search results and the typo-fixed question
    results = retrieve_documents(question)

    embedding_end = time.perf_counter()

    retrieval_start = embedding_start
    retrieval_end = embedding_end

    score = best_score(results)

    print("\n==========================")
    print("QUESTION :", question)
    print("BEST SCORE :", score)
    print("==========================")

    # ----------------------------------------------------
    # FIX: Robust Router Block (Cleans Markdown and Extra Text)
    # ----------------------------------------------------
    # ----------------------------------------------------
    # FIXED: Two-Step Independent Routing (With Database Override)
    # ----------------------------------------------------
    # # Step A: Get the Intent Category from the LLM
    # raw_intent = intent_chain.invoke({"user_query": question}).strip().upper()
    # print(f"🤖 RAW INTENT OUTPUT: '{raw_intent}'")

    # # Map the output using simple keyword matching
    # if "GREETING" in raw_intent:
    #     llm_route = "GREETING"
    # elif "PDF_POLICY" in raw_intent or "POLICY" in raw_intent:
    #     llm_route = "PDF_POLICY"
    # else:
    #     llm_route = "OUT_OF_SCOPE"

    # # 🔥 FIX: Smarter Database Override Check
    # # ONLY apply the override if the LLM didn't explicitly flag it as OUT_OF_SCOPE.
    # # This allows general knowledge questions to flow naturally to the Scope Guard!
    # if llm_route != "OUT_OF_SCOPE" and llm_route != "GREETING":
    #     if score <= 0.85:
    #         print(
    #             f"🎯 DATABASE OVERRIDE: Strong match found ({score:.4f}). Forcing PDF_POLICY route."
    #         )
    #         llm_route = "PDF_POLICY"

    # # Step B: Get the Cleaned Query (Only if it's a policy question)
    # if llm_route == "PDF_POLICY":
    #     clean_question = typo_chain.invoke({"user_query": question}).strip()
    # else:
    #     clean_question = question

    # print(
    #     f"✅ Route Finalized -> Route: {llm_route} | Clean Query: '{clean_question}'"
    # )

    # Step A: Get the Intent Category from the LLM
    try:
        raw_intent = intent_chain.invoke({"user_query": question}).strip().upper()
        print(f"🤖 RAW INTENT OUTPUT: '{raw_intent}'")

        # Map the output using simple keyword matching
        if "GREETING" in raw_intent:
            llm_route = "GREETING"
        elif "PDF_POLICY" in raw_intent or "POLICY" in raw_intent:
            llm_route = "PDF_POLICY"
        else:
            llm_route = "OUT_OF_SCOPE"

        # 🔥 CRITICAL OVERRIDE: If ChromaDB finds a strong match, it MUST be a policy question!
        # If score is very good (e.g., less than 0.85), ignore the LLM and force PDF_POLICY
        if score <= 0.85 and llm_route != "GREETING":
            print(
                f"🎯 DATABASE OVERRIDE: Strong match found ({score:.4f}). Forcing PDF_POLICY route."
            )
            llm_route = "PDF_POLICY"

        # Step B: Get the Cleaned Query (Only if it's a policy question)
        if llm_route == "PDF_POLICY":
            clean_question = typo_chain.invoke({"user_query": question}).strip()
        else:
            clean_question = question

        print(
            f"✅ Route Finalized -> Route: {llm_route} | Clean Query: '{clean_question}'"
        )

    except Exception as e:
        print(f"⚠️ Router failed, running manual string override. Error: {e}")
        # HARD CODED CONTEXT FALLBACK (Safety Net)
        q_lower = question.lower().strip()
        if any(
            g in q_lower
            for g in ["hi", "hello", "hey", "how are you", "good morning", "thanks"]
        ):
            llm_route = "GREETING"
            clean_question = question
        else:
            llm_route = "PDF_POLICY"
            clean_question = question

    # # ----------------------------------------------------
    # # NEW: Router Block (Executes exactly where your UI 'Router' box is)
    # # ----------------------------------------------------
    # try:
    #     router_output = router_chain.invoke({"user_query": question}).strip()
    #     router_json = json.loads(router_output)
    #     clean_question = router_json.get("cleaned_query", question)
    #     llm_route = router_json.get("route", "PDF_POLICY")
    #     print(
    #         f"🤖 Router Model Decision -> Route: {llm_route} | Fixed: '{clean_question}'"
    #     )
    # except Exception as e:
    #     print(f"⚠️ Router failed, falling back to basic checks. Error: {e}")
    #     clean_question = question
    #     llm_route = "PDF_POLICY"

    # # -------------------------
    # # Step 2 : PDF Route
    # # -------------------------

    # if score <= SIMILARITY_THRESHOLD:

    #     llm_start = time.perf_counter()

    #     result = pdf_response(question)

    #     llm_end = time.perf_counter()

    #     total_end = time.perf_counter()
    #     best = score if score is not None else 999
    #     return jsonify(
    #         {
    #             "agent": "PDF RAG Agent",
    #             "answer": result["answer"],
    #             "pages": result["pages"],
    #             "scores": result["scores"],
    #             "best_score": best,
    #             "confidence": result["confidence"],
    #             "chunks": result["chunks"],
    #             "runtime": {
    #                 "embedding": round(embedding_end - embedding_start, 3),
    #                 "retrieval": round(retrieval_end - retrieval_start, 3),
    #                 "llm": round(llm_end - llm_start, 3),
    #                 "total": round(total_end - total_start, 3),
    #             },
    #             "pipeline": [
    #                 "Question",
    #                 "Embedding",
    #                 "Vector Search",
    #                 "Similarity Check",
    #                 "Router",
    #                 "PDF Agent",
    #                 "LLM",
    #                 "Final Answer",
    #             ],
    #         }
    #     )

    # # -------------------------
    # # Step 3 : Greeting
    # # -------------------------
    # q = clean_question.lower().strip()

    # greetings = [
    #     "hi",
    #     "hello",
    #     "hey",
    #     "good morning",
    #     "good afternoon",
    #     "good evening",
    #     "thanks",
    #     "thank you",
    #     "bye",
    #     "how are you",
    # ]

    # if q in greetings:
    #     total_end = time.perf_counter()
    #     return jsonify(
    #         {
    #             "agent": "Greeting Agent",
    #             "answer": greeting_response(),
    #             "pages": [],
    #             "scores": [],
    #             "best_score": score,
    #             "chunks": [],
    #             "confidence": 100,
    #             "runtime": {
    #                 "embedding": round(embedding_end - embedding_start, 3),
    #                 "retrieval": round(retrieval_end - retrieval_start, 3),
    #                 "llm": 0,
    #                 "total": round(total_end - total_start, 3),
    #             },
    #             "pipeline": [
    #                 "Question",
    #                 "Embedding",
    #                 "Vector Search",
    #                 "Similarity Check",
    #                 "Router",
    #                 "Greeting Agent",
    #                 "Final Answer",
    #             ],
    #         }
    #     )

    # # -------------------------
    # # Step 4 : Unknown
    # # -------------------------
    # total_end = time.perf_counter()
    # return jsonify(
    #     {
    #         "agent": "Scope Guard",
    #         "answer": scope_response(),
    #         "pages": [],
    #         "scores": [],
    #         "best_score": score,
    #         "chunks": [],
    #         "confidence": 100,
    #         "runtime": {
    #             "embedding": round(embedding_end - embedding_start, 3),
    #             "retrieval": round(retrieval_end - retrieval_start, 3),
    #             "llm": 0,
    #             "total": round(total_end - total_start, 3),
    #         },
    #         "pipeline": [
    #             "Question",
    #             "Embedding",
    #             "Vector Search",
    #             "Similarity Check",
    #             "Router",
    #             "Scope Agent",
    #             "Final Answer",
    #         ],
    #     }
    # )
    # # -------------------------
    # # Step 1 : Retrieval & Classification
    # # -------------------------
    # embedding_start = time.perf_counter()

    # # We now unpack THREE values: results list, clean question, and the LLM classified intent
    # results, clean_question, intent = retrieve_documents(question)

    # embedding_end = time.perf_counter()
    # retrieval_start = embedding_start
    # retrieval_end = embedding_end

    # score = best_score(results)

    # print("\n==========================")
    # print("QUESTION   :", question)
    # print("CLASSIFIED :", intent)
    # print("BEST SCORE :", score)
    # print("==========================")

    # -------------------------
    # Step 2 : PDF Route (Triggered by LLM Intent classification)
    # -------------------------
    if llm_route == "PDF_POLICY" and score <= SIMILARITY_THRESHOLD:
        llm_start = time.perf_counter()
        result = pdf_response(
            results, clean_question
        )  # If needed, you can switch this to pass clean_question
        llm_end = time.perf_counter()
        total_end = time.perf_counter()

        # best = score if score is not None else 999
        return jsonify(
            {
                "agent": "PDF RAG Agent",
                "answer": result["answer"],
                "pages": result["pages"],
                "scores": result["scores"],
                "best_score": score,
                "confidence": result["confidence"],
                "chunks": result["chunks"],
                # "cleaned_query": clean_question,  # <--- ADD THIS LINE
                # "intent": intent,  # <--- ADD THIS LINE
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
    # Step 3 : Greeting Route
    # -------------------------
    if llm_route == "GREETING":
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
    # Step 4 : Unknown / Out of Scope Route
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
