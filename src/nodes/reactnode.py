from typing import List, Optional
from src.state.rag_state import RAGState

from langchain_core.documents import Document
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun


class RAGNodes:
    """
    Class to manage retrieval-augmented generation (RAG) nodes and tools.

    Attributes:
        retriever: A retriever object used to fetch documents based on a query.
        llm: A language model used for generation.
        _agent: Optional internal agent that can interact with tools.
    """

    def __init__(self, retriever, llm):
        """
        Initialize RAGNodes with a retriever and a language model.

        Args:
            retriever: The retriever used to fetch documents.
            llm: The language model for generating answers.
        """
        self.retriever = retriever
        self.llm = llm
        self._agent = None

    def retrieve_docs(self, state: RAGState) -> RAGState:
        """
        Retrieve documents from the retriever based on the query in the given state.

        Args:
            state (RAGState): The current state containing the user query.

        Returns:
            RAGState: A new RAGState with the retrieved documents added.
        """
        docs = self.retriever.invoke(state.query)
        return RAGState(
            query=state.query,
            retrieved_docs=docs
        )

    def _build_tools(self) -> List[Tool]:
        """
        Build the tools used by the RAG agent.

        Returns:
            List[Tool]: A list of Tool objects for the agent to use.
        """

        def retriever_tool(query: str) -> str:
            """
            Tool function to fetch passages from the indexed vector store.

            Args:
                query (str): The user's query.

            Returns:
                str: A formatted string of retrieved documents or a message if none are found.
            """
            docs: List[Document] = self.retriever.invoke(query)
            if not docs:
                return "No documents found."

            merged = []
            for i, d in enumerate(docs[:8], start=1):
                meta = d.metadata if hasattr(d, "metadata") else {}
                title = meta.get("title") or meta.get("source") or f"doc_{i}"
                merged.append(f"[{i}] {title} \n {d.page_content}")

            return "\n\n".join(merged)

        retriever_tool_obj = Tool(
            name="retriever",
            description="Fetch passage from indexed vectorstore",
            func=retriever_tool
        )

        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=3, lang="en")
        )
        wikipedia_tool = Tool(
            name="Wikipedia",
            description="Search Wikipedia for general knowledge",
            func=wiki.run
        )

        return [retriever_tool_obj, wikipedia_tool]

    def _build_agent(self):
        """
        Build the RAG agent using the tools and a system prompt.

        This agent uses a React-style reasoning loop to decide which tool to call.
        """
        tools = self._build_tools()

        system_prompt = (
            "You are a helpful RAG. "
            "Prefer 'retriever' for user-provided docs; use 'Wikipedia' for general knowledge. "
            "Return only the final useful answer."
        )

        self._agent = create_react_agent(tools=tools, prompt=system_prompt)


    def generate_answer(self, state:RAGState):
        if self.agent is None:
            self._build_agent()
        result = self._agent.invoke({"messages":[HumanMessage(content=state.query)]})
        messages = result.get("messages", [])
        answer:Optional[str]=None
        if messages:
            answer_msg = messages[-1]
            answer = getattr(answer_msg, "content", None)
        return RAGState(
            query=state.query,
            retrieved_docs=state.retrieved_docs,
            answer=answer
        )