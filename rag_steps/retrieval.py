from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from openai import OpenAI

from config import EMBEDDING_MODEL, VECTOR_DB_PATH, VECTOR_COLLECTION_NAME, OPEN_API_KEY
from logger import log

client = OpenAI(base_url="https://api.gapgpt.app/v1", api_key=OPEN_API_KEY)
def retrieve(indexed_records, retrieval_query, top_k):
    log("retrieve")
    retriever = indexed_records.as_retriever(
        search_kwargs={"k": top_k},
    )
    retrieved_chunks = retriever.invoke(retrieval_query)
    return retrieved_chunks

class GapGPTEmbeddings(Embeddings):

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

def get_vector_store():
    log("get_vector_store")

    embeddings =GapGPTEmbeddings()

    vector_store = Chroma(
        collection_name=VECTOR_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PATH,
        collection_metadata={"hnsw:space": "cosine"}
    )

    return vector_store


def get_vector_counts():
    log("get_vector_counts")
    vector_store = get_vector_store()
    return vector_store._collection.count()
