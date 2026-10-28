from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import RULES_FILE, CHUNK_SIZE, CHUNK_OVERLAP
from logger import log
from rag_steps.retrieval import get_vector_store


def load_documents():
    log("load_documents")
    file = open(RULES_FILE, "r", encoding="utf-8")
    text = file.read()
    file.close()

    document = Document(
        page_content=text,
        metadata={"source": RULES_FILE}
    )

    return [document]


def clean(documents: list[Document]):
    log("cleaning")
    cleaned_documents = []

    for doc in documents:
        text = doc.page_content
        text = text.replace("\r\n", "\n")
        text = text.strip()

        while "  " in text:
            text = text.replace("  ", " ")

        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")

        clean_doc = Document(
            page_content=text,
            metadata=doc.metadata
        )

        cleaned_documents.append(clean_doc)

    return cleaned_documents


def chunk_documents(clean_docs: list[Document]):
    log("chunk_documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = text_splitter.split_documents(clean_docs)
    return chunks


def attach_metadata(chunks: list[Document]):
    log("attach_metadata")
    chunk_records = []

    for index, chunk in enumerate(chunks):
        chunk.metadata['id'] = index + 1
        chunk.metadata['source'] = RULES_FILE
        chunk_records.append(chunk)

    return chunk_records


def embed_and_index(chunk_records):
    log("embed_and_index")
    indexed_records = get_vector_store()
    indexed_records.add_documents(chunk_records)
    return indexed_records
