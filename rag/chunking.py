import re
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_documents(pages, fandom_url):
    docs = []

    for page in pages:
        title = page["title"]
        text = page["text"]
        url = f"{fandom_url}/wiki/{title.replace(' ', '_')}"

        doc = Document(
            page_content=f"# {title}\n\n{text}",
            metadata={
                "title": title,
                "source": url
            }
        )
        docs.append(doc)
    return docs


def split_by_sections(text):
    """
    Divide o texto em seções com base em == Section ==
    """
    pattern = r"(== .*? ==)"
    parts = re.split(pattern, text)

    sections = []
    current_section = "Intro"
    current_text = ""

    for part in parts:
        if re.match(pattern, part):
            if current_text:
                sections.append((current_section, current_text.strip()))
            current_section = part.strip("= ").strip()
            current_text = ""
        else:
            current_text += part

    if current_text:
        sections.append((current_section, current_text.strip()))

    return sections


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=80
    )

    final_chunks = []

    for doc in documents:
        sections = split_by_sections(doc.page_content)

        for section_title, section_text in sections:
            if not section_text.strip():
                continue

            chunks = splitter.split_text(section_text)

            for chunk in chunks:
                final_chunks.append(
                    Document(
                        page_content=f"{doc.metadata['title']}\n{section_title}\n\n{chunk}",
                        metadata={
                            **doc.metadata,
                            "section": section_title
                        }
                    )
                )

    return final_chunks