import os

from langchain_ollama import ChatOllama


def get_llm():
    return ChatOllama(
        model=os.environ.get("OLLAMA_MODEL", "qwen2:7b"),
        temperature=0.1,
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    )


def generate_answer(llm, query, context):
    prompt = f"""
        Você é um assistente que responde perguntas com base em uma wiki.

        REGRAS IMPORTANTES:
        - Use APENAS as informações do contexto abaixo.
        - Se o nome aparecer no contexto, você DEVE considerá-lo válido.
        - NUNCA diga que algo não existe se estiver presente no texto.
        - Se a pergunta for "o que é X", procure uma frase que defina X.
        - Se não encontrar a resposta, diga que não sabe.

        Contexto:
        {context}

        Pergunta: {query}

        Responda em português de forma clara e objetiva.
    """

    response = llm.invoke(prompt)
    return response.content
