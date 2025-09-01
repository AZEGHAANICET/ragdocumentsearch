from langgraph.graph import StateGraph, END

from src.nodes.nodes import RAGNode
from src.state.rag_state import RAGState


class GraphBuilder:
    """
    Builds and manages the Langgraph workflow
    """
    def __init__(self, retriever, llm):
        self.nodes = RAGNode(retriever, llm)
        self.graph = None

    def build(self):

        builder = StateGraph(RAGState)

        #Create nodes
        builder.add_node("retriever", self.nodes.retriever_docs)
        builder.add_node("responder", self.nodes.generate_answer)

        # Set entry point

        builder.set_entry_point("retriever")

        #Add edges
        builder.add_edge("retriever", "responder")
        builder.add_edge("responder", END)

        self.graph = builder.compile()
        return self.graph

    def run(self, question):

        if self.graph is None:
            self.build()
        initial_state = RAGState(query=question)
        return self.graph.invoke(initial_state)