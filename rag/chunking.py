from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_documents(pages, fandom_url):
    docs = []

    for page in pages:
        title = page["title"]
        text = page["text"]
        url = f"{fandom_url}/wiki/{title.replace(' ', '_')}"

        doc = Document(
            page_content=text,
            metadata={
                "title": title,
                "source": url
            }
        )
        docs.append(doc)
    return docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)
    return chunks