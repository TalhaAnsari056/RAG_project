PDF_PATH = "./data/CompanyPolicy.pdf"

LLM_MODEL = "qwen2.5:3b"
# LLM_MODEL = "qwen2.5:0.5b"
ROUTER_MODEL = "qwen2.5:3b"
VECTOR_DB_PATH = "./vectordb"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# CHUNK_SIZE = 1000
# CHUNK_OVERLAP = 200
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K = 3
SIMILARITY_THRESHOLD = 1.25
# Lower score = better match
# SIMILARITY_THRESHOLD = 1.50
