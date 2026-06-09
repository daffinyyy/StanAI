from crewai import Agent

def create_research_agent(llm, tools):
    return Agent(
        role="Pesquisador de Conteúdo",
        goal=(
            "Encontrar informações relevantes em wikis, fóruns, "
            "sites de notícias e outras fontes."
        ),
        backstory=(
            "Especialista em coletar informações de múltiplas fontes de cultura pop, "
            "como jogos, séries, personagens, lore, mecânicas e eventos."
        ),
        tools=tools,
        llm=llm,
        verbose=True
    )


def create_writer_agent(llm):
    return Agent(
        role="Redator Técnico",
        goal=(
            "Produzir respostas claras e corretas utilizando "
            "apenas as informações fornecidas pela pesquisa."
        ),
        backstory=(
            "Você recebe informações coletadas por outro agente "
            "e transforma essas informações em uma resposta final "
            "bem escrita, organizada e amigável."
        ),
        llm=llm,
        verbose=True
    )