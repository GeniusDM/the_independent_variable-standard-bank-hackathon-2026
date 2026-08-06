"""
retrieval.py
Builds and queries a FAISS vector store over ingested financial documents
(annual reports, SENS announcements, etc.) for RAG-powered briefing generation.
"""
import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

EXTERNAL_DIR = Path(__file__).parents[1] / "data" / "external"
INDEX_PATH = Path(__file__).parents[1] / "data" / "processed" / "faiss_index"


def build_index(docs_dir: Path = EXTERNAL_DIR) -> FAISS:
    loader = DirectoryLoader(str(docs_dir), glob="**/*.txt", loader_cls=TextLoader)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings()
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(INDEX_PATH))
    return store


def load_index() -> FAISS:
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)


def retrieve(query: str, k: int = 5) -> list[str]:
    store = load_index()
    results = store.similarity_search(query, k=k)
    return [r.page_content for r in results]
