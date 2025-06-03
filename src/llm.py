from src.models import Link, LinkList, PageRepresentation, PageContent
from src.prompts import filter_links_prompt, summarize_page_prompt
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List


class ModelType(Enum):
    DEEPSEEK = "deepseek-r1:7b"
    LLAMA = "gemma3:12b"
    OPENAI = "gpt-4o-mini"


class LLM:
    def __init__(self, model=ModelType.LLAMA):
        """
        Inizializza il modello LLM (OpenAI o Ollama) in base al tipo richiesto.
        """
        print(f"Using {model.value}")
        if model == ModelType.OPENAI:
            print("openai")
            self.llm = ChatOpenAI(model_name=model.value, temperature=0)
        else:
            self.llm = OllamaLLM(model=model.value, temperature=0)

    def filter_links_by_topics(self, links: List[Link], topics: List[str]) -> LinkList:
        """
        Filtra i link in base alla pertinenza rispetto a una lista di topic usando un LLM.
        """
        link_list_parser = PydanticOutputParser(pydantic_object=LinkList)
        prompt = PromptTemplate(
            template=filter_links_prompt,
            input_variables=["links", "topics"],
            partial_variables={
                "format_instructions": link_list_parser.get_format_instructions()
            },
        )
        chain = prompt | self.llm | link_list_parser
        try:
            link_list = chain.invoke({"links": links, "topics": topics})
            return link_list
        except Exception as e:
            print(f"Errore durante il filtraggio dei link: {e}")
            return LinkList(links=[])

    def summarize_page(self, page: PageRepresentation) -> PageContent:
        """
        Genera un riassunto markdown a partire dalla rappresentazione compatta della pagina.
        """
        from langchain_core.output_parsers import StrOutputParser

        prompt = PromptTemplate(
            template=summarize_page_prompt,
            input_variables=["page_representation"]
        )
        chain = prompt | self.llm | StrOutputParser()
        try:
            summary = chain.invoke({"page_representation": page.page_representation})
            return PageContent(link=page.link, title=page.title, content=summary)
        except Exception as e:
            print(f"Errore durante la generazione del riassunto: {e}")
            return PageContent(link=page.link, title=page.title, content="")
