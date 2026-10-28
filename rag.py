from config import TOP_K
from rag_steps.document import load_documents, clean, chunk_documents, attach_metadata, embed_and_index
from rag_steps.retrieval import get_vector_store, get_vector_counts, retrieve


def prepare_rag():
    indexed_records = get_vector_store()

    if get_vector_counts() == 0:
        documents = load_documents()
        clean_docs = clean(documents)
        chunks = chunk_documents(clean_docs)
        chunk_records = attach_metadata(chunks)
        indexed_records = embed_and_index(chunk_records)

    return indexed_records


def search_rules_in_rag(indexed, query):
    return retrieve(indexed, query, TOP_K)
