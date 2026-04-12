from langchain_ollama import ChatOllama


def get_llm():
    llm = ChatOllama(
        model="llama3",
        temperature=0
    )
    return llm


def generate_answer(llm, query, context):
    prompt = f"""
        Responda à pergunta com base no contexto abaixo.

        Contexto:
        {context}

        Pergunta: {query}

        Responda em português.
    """

    response = llm.invoke(prompt)

    return response.content