import time
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import *
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)
db = Chroma(
    persist_directory=VECTOR_DB_PATH,
    embedding_function=embedding_model
)

while True:

    query = input("\nAsk a question (type 'exit' to quit): ")

    if query.lower() == "exit":
        print("\nGoodbye!")
        # start = time.time()
        break
    results = db.similarity_search_with_score(
        query,
        k=TOP_K
    )
    # end = time.time()
    print("\nRetrieved Chunks:\n")

    for i, (doc, score) in enumerate(results, start=1):

        print("=" * 80)

        print(f"Result #{i}")

        print(f"Similarity Score : {score:.4f}")

        print(f"Page Number      : {doc.metadata.get('page')}")

        print(f"Source           : {doc.metadata.get('source')}")
        # print(f"\nRetrieval Time: {end-start:.3f} seconds")
        print("\nRetrieved Text\n")

        print(doc.page_content)

        print("\n")