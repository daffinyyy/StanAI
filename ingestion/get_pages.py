import requests

from rag.wiki_paths import normalize_wiki_base_url


def get_all_pages(fandom_url):
    """
    Retorna:
    - lista de títulos
    - lista de URLs
    - total de páginas
    """

    fandom_url = normalize_wiki_base_url(fandom_url)
    api_url = fandom_url.rstrip("/") + "/api.php"

    titles = []

    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": "max",
        "apnamespace": 0,
        "format": "json"
    }

    while True:
        response = requests.get(api_url, params=params)
        data = response.json()

        pages = data["query"]["allpages"]

        for page in pages:
            titles.append(page["title"])

        if "continue" in data:
            params["apcontinue"] = data["continue"]["apcontinue"]
        else:
            break

    urls = [
        f"{fandom_url.rstrip('/')}/wiki/{t.replace(' ', '_')}"
        for t in titles
    ]

    return {
        "total": len(titles),
        "titles": titles,
        "urls": urls
    }