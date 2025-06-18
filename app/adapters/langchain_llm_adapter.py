from app.ports.llm import LLMPort
from app.ports.models import (
    ArticleLinkExtractionInput,
    ArticleLinkExtractionOutput,
    ArticleLinkLLM,
    SummarizePageInput,
    SummarizePageOutput,
)
from typing import List
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain.prompts import PromptTemplate
from enum import Enum

# Prompt reali importati da src.prompts
from app.adapters.prompts import extract_article_links_prompt, summarize_page_prompt


class ModelType(Enum):
    DEEPSEEK = "deepseek-r1:7b"
    LLAMA = "llama3.1:latest"
    GEMMA = "gemma3:12b"
    OPENAI = "gpt-4o-mini"


class LangChainLLMAdapter(LLMPort):
    """
    Adapter concreto per LLM tramite LangChain.
    """

    def __init__(self, model=ModelType.LLAMA):
        if model == ModelType.OPENAI:
            self.llm = ChatOpenAI(model_name=model.value, temperature=0)
        else:
            self.llm = OllamaLLM(model=model.value, temperature=0)

    def extract_article_links(
        self, data: ArticleLinkExtractionInput
    ) -> ArticleLinkExtractionOutput:
        link_list_parser = PydanticOutputParser(
            pydantic_object=ArticleLinkExtractionOutput
        )
        prompt = PromptTemplate(
            template=extract_article_links_prompt,
            input_variables=["summary"],
            partial_variables={
                "format_instructions": link_list_parser.get_format_instructions()
            },
        )
        chain = prompt | self.llm | link_list_parser
        try:
            result = chain.invoke({"summary": data.markdown})
            return result
        except Exception as e:
            print(f"Errore durante l'estrazione dei link agli articoli: {e}")
            return ArticleLinkExtractionOutput(links=[])

    def summarize_page(self, data: SummarizePageInput) -> SummarizePageOutput:
        prompt = PromptTemplate(
            template=summarize_page_prompt,
            input_variables=["page_representation"],
        )
        chain = prompt | self.llm | StrOutputParser()
        try:
            summary = chain.invoke({"page_representation": data.page_representation})
            return SummarizePageOutput(summary_markdown=summary)
        except Exception as e:
            print(f"Errore durante la generazione del riassunto: {e}")
            return SummarizePageOutput(summary_markdown="")
