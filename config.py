import os

from dotenv import load_dotenv

load_dotenv()
CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

RULES_FILE = 'data/rules.txt'
CHUNK_SIZE = 250
CHUNK_OVERLAP = 20

VECTOR_DB_PATH = 'db/vectors.db'
VECTOR_COLLECTION_NAME = 'rules'
TOP_K = 2
MAX_ITERATION= 1
MAX_MEMORY_SIZE = 1
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")