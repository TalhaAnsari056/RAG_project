from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import *

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding_model)


def retrieve_documents(question):

    results = db.similarity_search_with_score(question, k=TOP_K)

    return results
