# from langchain_community.document_loaders import PyPDFLoader

# pdf_path = "./data/CompanyPolicy.pdf"

# loader = PyPDFLoader(pdf_path)

# docs = loader.load()

# print(f"Total Pages: {len(docs)}")

# print("\nFirst Page Content:\n")
# print(docs[0].page_content[:500])
# total pages 109
import os
import sys

# Tell Windows where your Tesseract OCR installation lives
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Tesseract-OCR"

# Explicitly bind the command path for the internal unstructured library
try:
    import unstructured_pytesseract

    unstructured_pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
except ImportError:
    pass

from langchain_community.document_loaders import UnstructuredPDFLoader

# from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


from config import *

pdf_path = PDF_PATH
print(f"Starting OCR parsing for: {pdf_path} (This can take a few minutes)...")

# 'hi_res' strategy uses OCR automatically to read text from inside images/diagrams
loader = UnstructuredPDFLoader(pdf_path, strategy="hi_res")
# loader = PyPDFLoader(pdf_path)
docs = loader.load()

print(f"Pages Loaded: {len(docs)}")

# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200
# )

# chunks = splitter.split_documents(docs)

# print(f"\nTotal Chunks: {len(chunks)}")

# print("\nFirst Chunk:\n")
# print(chunks[0].page_content)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
)

chunks = splitter.split_documents(docs)

print("\nMetadata of first 5 chunks:\n")

for chunk in chunks[:5]:
    print(chunk.metadata)

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# vector = embedding_model.embed_query(
#     chunks[0].page_content
# )

# print(f"\nEmbedding Length: {len(vector)}")
db = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=VECTOR_DB_PATH,
    collection_metadata={"hnsw:space": "cosine"},
)

print("Vector Database Created Successfully with Image OCR Text!")
print(f"Stored {len(chunks)} Chunks")
