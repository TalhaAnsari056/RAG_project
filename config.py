PDF_PATH = "./data/CompanyPolicy.pdf"

LLM_MODEL = "qwen3:8b"
# LLM_MODEL = "qwen2.5:0.5b"
ROUTER_MODEL = "qwen2.5:0.5b"
VECTOR_DB_PATH = "./vectordb"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 5
SIMILARITY_THRESHOLD = 0.60
# Lower score = better match
# SIMILARITY_THRESHOLD = 1.50
