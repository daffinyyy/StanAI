from bs4 import BeautifulSoup

def clean_html(html, page_title=""):
    soup = BeautifulSoup(html, "html.parser")

    #oq esta sendo jogado fora
    for tag in soup(["script", "style", "aside"]):
        tag.decompose()
    for tag in soup.select(".navbox, .mw-editsection, .reference"):
        tag.decompose()

    content = soup.find("div", class_="mw-parser-output")
    if not content:
        return ""

    texts = []

    #oq esta sendo coletado
    #titulo da pagina
    if page_title:
        texts.append(f"# {page_title}\n")

    #infoboxes
    infobox = soup.select_one(".portable-infobox")
    if infobox:
        texts.append("== Infobox ==")

        for row in infobox.select(".pi-item"):
            label = row.select_one(".pi-data-label")
            value = row.select_one(".pi-data-value")

            if label and value:
                l = label.get_text(" ", strip=True)
                v = value.get_text(" ", strip=True)

                if l and v:
                    texts.append(f"{l}: {v}")

        infobox.decompose()

    for element in content.children:
        #titulos
        if element.name in ["h2", "h3"]:
            title = element.get_text(" ", strip=True)
            if title:
                texts.append(f"\n== {title} ==\n")

        #paragrafos
        elif element.name == "p":
            text = element.get_text(" ", strip=True)
            if len(text) > 30:
                texts.append(text)

        #listas
        elif element.name in ["ul", "ol"]:
            for li in element.find_all("li", recursive=False):
                item = li.get_text(" ", strip=True)
                if item:
                    texts.append(f"- {item}") #remove referencias

        # tabelas
        elif element.name == "table":
            header = None
            for row in element.find_all("tr"):
                cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
                cols = [c for c in cols if c]

                if not cols:
                    continue

                # detecta header
                if row.find("th") and header is None:
                    header = " | ".join(cols)
                    continue

                if len(cols) == 1:
                    texts.append(cols[0])
                else:
                    row_text = " | ".join(cols)

                    if header:
                        texts.append(f"{header}\n{row_text}")
                    else:
                        texts.append(row_text)


    cleaned_text = "\n\n".join(texts)

    return cleaned_text