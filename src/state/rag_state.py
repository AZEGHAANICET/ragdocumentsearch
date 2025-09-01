from typing import List
from pydantic import BaseModel
from langchain.schema import Document


class RAGState(BaseModel):
    """
    State object for RAG workflow
    """
    query: str
    retrieved_docs: List[Document] = []
    answer: str=""