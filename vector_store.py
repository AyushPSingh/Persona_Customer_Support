"""
Builds and manages the FAISS vector store for knowledge-base retrieval.
Uses HuggingFace sentence-transformers for embeddings (no API key required).
"""
import os
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from knowledge_base import KB_DOCUMENTS

# Path where the FAISS index is persisted
INDEX_PATH = "faiss_index"

# HuggingFace model used for embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _build_documents() -> List[Document]:
    """Convert KB dicts into LangChain Document objects."""
    docs = []
    for item in KB_DOCUMENTS:
        docs.append(
            Document(
                page_content=item["content"],
                metadata={"title": item["title"], "category": item["category"]},
            )
        )
    return docs


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return an embeddings model instance (cached by LangChain internals)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_or_build_vectorstore() -> FAISS:
    """
    Load the FAISS index from disk if it exists, otherwise build and save it.
    Returns a FAISS retriever-ready object.
    """
    embeddings = get_embeddings()

    if os.path.exists(INDEX_PATH):
        print("[VectorStore] Loading existing FAISS index from disk…")
        vectorstore = FAISS.load_local(
            INDEX_PATH, embeddings, allow_dangerous_deserialization=True
        )
    else:
        print("[VectorStore] Building FAISS index from knowledge base…")
        docs = _build_documents()
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(INDEX_PATH)
        print(f"[VectorStore] Index saved to '{INDEX_PATH}/'")

    return vectorstore


def retrieve(query: str, k: int = 3) -> List[str]:
    """
    Retrieve the top-k most relevant KB snippets for a given query.
    Returns a list of content strings.
    """
    store = load_or_build_vectorstore()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]
