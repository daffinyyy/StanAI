from bs4 import BeautifulSoup

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    #removendo conteúdo inútil
    for tag in soup(["script", "style", "aside", "table"]):
        tag.decompose()
    for tag in soup.select(".portable-infobox, .navbox, .mw-editsection"):
        tag.decompose()

    paragraphs = soup.find_all("p")

    texts = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)

        if len(text) > 20:  # filtra lixo pequeno
            texts.append(text)

    cleaned_text = "\n\n".join(texts)

    return cleaned_text