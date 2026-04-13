from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def create_vector_db(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3"
    )

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="./chroma_db"
    )
    return db


def load_vector_db():
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3"
    )

    db = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    return db
