import streamlit as st
from pathlib import Path
import sys
from src.document_ingestion.document_processor import DocumentProcessor
import time

from src.config.config import Config
from src.graph_builder.graph_builder import GraphBuilder
from src.vectorstores.vectorstore import VectorStore

# Ajoute le dossier courant au sys.path si nécessaire pour les imports locaux
sys.path.append(str(Path(__file__).parent))

# Configuration de la page Streamlit
st.set_page_config(
    page_title="📚 RagDocumentSearch",
    page_icon="🔍",
    layout="centered",
)

# Style pour les boutons
st.markdown("""
<style>
.stButton > button {
    width: 100%;
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """
    Initialize the Streamlit session state for the RAG system.
    """
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "history" not in st.session_state:
        st.session_state.history = []


@st.cache_resource
def initialize_rag():
    """
    Initialize the RAG system.

    Returns:
        graph_builder (GraphBuilder): The RAG graph builder instance.
        num_documents (int): Number of documents processed.
    """
    try:
        llm = Config.get_llm()

        # Initialisation du traitement des documents
        doc_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        vector_store = VectorStore()

        urls = Config.DEFAULT_URLS
        documents = doc_processor.process_url(urls)
        vector_store.create_retriever(documents=documents)

        graph_builder = GraphBuilder(
            retriever=vector_store.get_retriever(),
            llm=llm
        )
        graph_builder.build()
        return graph_builder, len(documents)
    except Exception as e:
        st.error(f"Failed to initialize RAG.\n{e}")
        return None, 0
def main():
    """
    Main application
    :return:
    """
    init_session_state()

    st.title("🔍 RAG Document Search")
    st.markdown("Ask questions about the loaded documents")


    if not st.session_state.initialized:
        with st.spinner("Loading System..."):
            rag_system, num_chunks = initialize_rag()
            if rag_system:
                st.session_state.rag_system = rag_system
                st.session_state.initialized = True
                st.success(f"✅ System ready! ({num_chunks} document chunks loaded)")
            st.markdown("----------------------------------------------------")


    with st.form("search_form"):
        question = st.text_input("Enter your question:", placeholder="What would you like to search?")
        submit = st.form_submit_button("🔍 Search")

    if submit and question:
        if st.session_state.rag_system:
            with st.spinner("Searching..."):
                start_time = time.time()

                result = st.session_state.rag_system.run(question)

                elapsed_time = time.time() - start_time

                st.session_state.history.append(
                    {
                        "question": question,
                        "answer": result["answer"],
                        "elapsed_time": elapsed_time,
                    }
                )

                st.markdown("### 💡 Answer")
                st.success(result["answer"])

                with st.expander("📄 Source Documents"):
                    for i, doc in enumerate(result['retrieved_docs'], 1):
                        st.text_area(
                            f"Document {i}",
                            doc.page_content[:300] + "...",
                            height=100,
                            disabled=True
                        )

                st.caption(f"⏱️ Response time: {elapsed_time:.2f} seconds")

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 📜 Recent Searches")

        for item in reversed(st.session_state.history[-3:]):  # Show last 3
            with st.container():
                st.markdown(f"**Q:** {item['question']}")
                st.markdown(f"**A:** {item['answer'][:200]}...")
                st.caption(f"Time: {item.get('time', 0):.2f}s")
                st.markdown("")


if __name__ == "__main__":
    main()