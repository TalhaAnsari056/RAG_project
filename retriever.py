from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama  # Added for Qwen
from langchain_core.prompts import PromptTemplate  # Added for Prompts

from config import *

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL, model_kwargs={"device": "cuda"}
)

db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding_model)

# # Initialize your local router model (qwen2.5:0.5b) for fixing typos
# router_llm = Ollama(model=ROUTER_MODEL, temperature=0.0)

# The prompt instructions for fixing typos strictly
# rewrite_prompt = PromptTemplate.from_template(
#     "You are an automated query cleaner. Fix any typos, spelling errors, or missing spaces "
#     "in the text below so it is clean for semantic document retrieval. "
#     "Respond ONLY with the corrected text string. Do not include notes or commentary.\n\n"
#     "Query: {user_query}\n"
#     "Cleaned Query:"
# )
# rewrite_chain = rewrite_prompt | router_llm


def retrieve_documents(question):

    # 1. Catch the original question and fix spelling mistakes
    # try:
    #     clean_question = rewrite_chain.invoke({"user_query": question}).strip()
    #     print(f"🔄 Typo Fixer -> Original: '{question}' | Fixed: '{clean_question}'")
    # except Exception as e:
    #     print(f"⚠️ Rewrite failed, falling back to original text. Error: {e}")
    #     clean_question = question  # fallback if model fails

    # 2. Query ChromaDB using the FIXED clean_question
    results = db.similarity_search_with_score(question, k=TOP_K)

    # Return BOTH the results and the corrected question
    return results

    # results = db.similarity_search_with_score(question, k=TOP_K)

    # return results


def best_score(results):
    # Because retrieve_documents now returns a tuple (results, clean_question),
    # app.py sends the tuple here. We extract just the results list.
    # results = results_tuple[0]

    if len(results) == 0:
        return 999.0

    return results[0][1]


# def best_score(results):

#     if len(results) == 0:
#         return 999

#     return results[0][1]
