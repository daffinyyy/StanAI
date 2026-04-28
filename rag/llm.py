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

        REGRAS OBRIGATÓRIAS:
        - Use SOMENTE informações presentes no contexto.
        - NÃO use conhecimento externo.
        - Se a resposta NÃO estiver no contexto, responda EXATAMENTE:
        "Não encontrei essa informação na wiki fornecida."


        - NÃO adicione nenhuma informação extra. 
        - NÃO dê sugestões, exemplos ou alternativas fora do contexto.
        - É melhor falar que não encontrou a resposta do que sugerir uma fora do contexto fornecido

        Contexto:
        {context}

        Pergunta: {query}

        Resposta (em português):
    """

    response = llm.invoke(prompt)
    return response.content
