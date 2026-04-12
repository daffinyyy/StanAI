from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


def create_vector_db(chunks):
    # cria embeddings
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    # cria banco vetorial
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./chroma_db"
    )
    return db


def load_vector_db():
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    return db


def search(db, query, k=3):
    retriever = db.as_retriever(search_kwargs={"k": k})
    results = retriever.invoke(query)

    return results