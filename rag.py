from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="vectordb",
    embedding_function=embedding_model
)

query = input("Ask a question: ")

results = db.similarity_search(
    query,
    k=3
)

print("\nRetrieved Chunks:\n")

for i, doc in enumerate(results, start=1):
    print(f"\nChunk {i}")
    print("-" * 50)
    print(doc.page_content)