import requests

def fetch_page(api_url, title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json"
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # erro HTTP

        data = response.json()

        # Verifica se a API retornou erro
        if "error" in data:
            print(f"[ERRO API] {title}: {data['error']}")
            return None

        html = data["parse"]["text"]["*"]
        return html

    except Exception as e:
        print(f"[ERRO REQUEST] {title}: {e}")
        return None