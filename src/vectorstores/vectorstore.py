from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document


class VectorStore:
    """
    Manage vector store application
    """

    def __init__(self):
        self.embedding = OpenAIEmbeddings()
        self.vectorstore = None
        self.retriever = None

    def create_retriever(self, documents: List[Document]):
        """
        Create vector store from documents
        :return:
        """

        self.vectorstore = FAISS.from_documents(documents, self.embedding)
        self.retriever = self.vectorstore.as_retriever()

    def get_retriever(self):

        """
        Get retriever
        :return:
        """
        if self.retriever is None:
            raise ValueError("retriever not initialized")
        return self.retriever


    def retrieve(self, query:str, k:int=4):
        """
        Get Retriever instance
        :return:
        """

        if self.retriever is None:
            ValueError("Vector store not initialized")
        return self.retriever.invoke(query)