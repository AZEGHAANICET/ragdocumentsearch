from typing import List

from src.state.rag_state import RAGState


class RAGNode:
    def __init__(self, retriever, llm):

        """
        Initialisation RAG Node
        :param retriever:
        :param llm:
        """

        self.retriever = retriever
        self.llm = llm

    def retriever_docs(self, state: RAGState) -> RAGState:
        """
        Retrieve RAG docs
        :param state:
        :return:
        """
        docs = self.retriever.invoke(state.query)
        return RAGState(
            query=state.query,
            retrieved_docs=docs,
        )

    def generate_answer(self, state: RAGState) -> RAGState:


        context = "\n\n".join(doc.page_content for doc in state.retrieved_docs)


        prompt = f"""
        Answer the following question based on the context.
        Context: {context}
        
        Question:
        {state.query}
        """

        response = self.llm.invoke(prompt)


        return RAGState(
            query=state.query,
            retrieved_docs=state.retrieved_docs,
            answer=response.content,
        )