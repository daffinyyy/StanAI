from crewai import Task

def create_research_task(agent, wiki_name):
    return Task(
        description=f"""
        Você é um pesquisador especializado em:

        {wiki_name}

        Todas as perguntas devem ser interpretadas
        dentro desse universo.

        IMPORTANTE:
        - Assuma que o usuário está falando sobre {wiki_name}.
        - Consulte primeiro a wiki.
        - Se não encontrar a resposta, pesquise na web mantendo o contexto de {wiki_name}.
        - Utilize ScrapeWebsiteTool na URL encontrada.
        - Nunca assuma que o usuário está falando de outro jogo ou franquia.

        Pergunta:
        {{question}}
        """,
        expected_output="""
        Resumo completo da pesquisa contendo
        fatos encontrados e fontes utilizadas.
        """,
        agent=agent
    )


def create_writer_task(agent, research_task):
    return Task(
        description="""
        Responda a pergunta abaixo utilizando
        exclusivamente o resultado da pesquisa.

        Pergunta:
        {question}
        """,
        expected_output="""
        Resposta final em português.
        """,
        agent=agent,
        context=[research_task]
    )