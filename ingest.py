# from langchain_community.document_loaders import PyPDFLoader

# pdf_path = "./data/CompanyPolicy.pdf"

# loader = PyPDFLoader(pdf_path)

# docs = loader.load()

# print(f"Total Pages: {len(docs)}")

# print("\nFirst Page Content:\n")
# print(docs[0].page_content[:500])
# total pages 109
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma



pdf_path = "./data/CompanyPolicy.pdf"

loader = PyPDFLoader(pdf_path)
docs = loader.load()

print(f"Pages Loaded: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)

print(f"\nTotal Chunks: {len(chunks)}")

print("\nFirst Chunk:\n")
print(chunks[0].page_content)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# vector = embedding_model.embed_query(
#     chunks[0].page_content
# )

# print(f"\nEmbedding Length: {len(vector)}")
db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="vectordb"
)

print("Vector Database Created Successfully")
print(f"Stored {len(chunks)} Chunks")