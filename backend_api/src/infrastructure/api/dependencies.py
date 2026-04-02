from infrastructure.persistence.agent.vector_repo import PostgresVectorRepo
from infrastructure.external.agent.ollama import OllamaAdapter
from application.use_cases.agent.chat_rag import ChatRAGUseCase
from application.use_cases.agent.ingest_doc import IngestDocUseCase
from application.use_cases.agent.ingest_text import IngestTextUseCase

# Instancias Globales (Singleton)
# Se crean una sola vez al arrancar la app
db_instance = PostgresVectorRepo()
llm_instance = OllamaAdapter()

def get_chat_use_case() -> ChatRAGUseCase:
    """Inyecta DB y LLM al caso de uso de Chat"""
    return ChatRAGUseCase(db=db_instance, llm=llm_instance)

def get_ingest_use_case() -> IngestDocUseCase:
    """Inyecta DB y LLM al caso de uso de Ingesta"""
    return IngestDocUseCase(db=db_instance, llm=llm_instance)

def get_ingest_text_use_case() -> IngestTextUseCase:
    return IngestTextUseCase(db=db_instance, llm=llm_instance)