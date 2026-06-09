from crewai import Crew
from urllib.parse import urlparse

from crew.agents import create_research_agent, create_writer_agent
from crew.tasks import create_research_task, create_writer_task
from crew.tools import WikiRAGTool, WebSearchTool
from crewai_tools import ScrapeWebsiteTool


def create_stan_crew(llm, wiki_url):
    # definindo o dominio
    wiki_name = extract_wiki_name(wiki_url)

    # definindo tools
    tools = [WikiRAGTool(wiki_url=wiki_url), WebSearchTool(), ScrapeWebsiteTool()]

    #definindo agentes
    researcher = create_research_agent(llm, tools)
    writer = create_writer_agent(llm)

    # definindo tarefas
    research_task = create_research_task(researcher, wiki_name)
    writer_task = create_writer_task(writer, research_task)

    return Crew(
        agents=[researcher, writer],
        tasks=[research_task, writer_task],
        verbose=True
    )


def extract_wiki_name(wiki_url):
    domain = urlparse(wiki_url).netloc

    wiki_name = domain.split(".")[0]

    return wiki_name.replace("-", " ")