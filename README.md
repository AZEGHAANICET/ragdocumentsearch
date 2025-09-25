# RagDocumentSearch — RAG minimaliste, élégant et efficace

Un moteur de recherche de documents basé sur RAG (Retrieval Augmented Generation) avec une UI Streamlit. Le système ingère des pages web et des PDF locaux, indexe les chunks dans FAISS, puis orchestre un workflow LangGraph pour récupérer le contexte pertinent et générer une réponse via un LLM OpenAI.

> Points forts
- Simplicité d’architecture et code lisible
- Ingestion URL et dossier `data/` (PDF)
- Vectorisation FAISS + OpenAI Embeddings
- Orchestration via LangGraph (nœuds Retrieve → Respond)
- UI Streamlit ergonomique et réactive

---

## Prérequis
- **Python** 3.10+
- **Clé API OpenAI** dans `OPENAI_API_KEY`
- **Windows PowerShell** (les commandes fonctionnent aussi sur macOS/Linux)

---

## Installation (Windows/PowerShell)

```powershell
# 1) Cloner le projet
git clone <votre-repo> ragdocumentsearchproject
cd ragdocumentsearchproject

# 2) Créer l’environnement virtuel
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Installer les dépendances
pip install -r requirements.txt

# 4) Variables d’environnement
# Option A: créer un fichier .env à la racine
# .env
# OPENAI_API_KEY=sk-...

# Option B: exporter dans la session PowerShell
$Env:OPENAI_API_KEY = "sk-..."
```

---

## Lancer l’application

```powershell
streamlit run streamlit_app.py
```

L’interface s’ouvre dans votre navigateur. Posez une question pour interroger les documents chargés.

---

## Structure du projet

```
ragdocumentsearchproject/
  data/                     # PDF d’exemple et sources
  src/
    config/config.py        # Config (modèle LLM, chunking, URLs par défaut)
    document_ingestion/
      document_processor.py # Chargement & split des documents
    vectorstores/vectorstore.py  # Embeddings + FAISS retriever
    state/rag_state.py      # État typé du workflow RAG
    graph_builder/graph_builder.py # Construction du graphe LangGraph
    nodes/
      nodes.py              # Nœuds RAG (retrieval + réponse LLM)
      reactnode.py          # (Variante agent ReAct + outils)
  streamlit_app.py          # UI et wiring bout-en-bout
  requirements.txt
```

---

## Configuration

Le fichier `src/config/config.py` centralise les réglages:
- **LLM_MODEL** par défaut: `openai:gpt-4o`
- **CHUNK_SIZE**, **CHUNK_OVERLAP** pour le découpage
- **DEFAULT_URLS** pour l’ingestion web initiale

Le LLM est instancié via LangChain `init_chat_model` et récupère la clé depuis `OPENAI_API_KEY`.

---

## Flux de bout en bout (Mermaid vertical)

```mermaid
flowchart TB
    A[UI Streamlit\nstreamlit_app.py] --> B[Init LLM & Config\nConfig.get_llm()]
    A --> C[Initialize RAG\ninitialize_rag()]
    C --> D[Ingestion\nDocumentProcessor.process_url(URLs)]
    D --> E[Split en chunks\nRecursiveCharacterTextSplitter]
    E --> F[Vectorisation\nOpenAIEmbeddings]
    F --> G[Indexation FAISS\nVectorStore.create_retriever]
    G --> H[Build Graph\nGraphBuilder.build()]
    H --> I[StateGraph(RAGState)\nNodes: retriever → responder]

    subgraph Query Flow
        J[Question utilisateur] --> K[Retriever.invoke(query)\nFAISS]
        K --> L[Concat contexte]
        L --> M[LLM.invoke(prompt)\nAnswer]
        M --> N[Résultat + docs sources]
    end

    A -. on submit .-> J
    I --> J
```

---

## Architecture des composants (Mermaid vertical)

```mermaid
flowchart TB
    subgraph Ingestion
        DP[DocumentProcessor\nload_from_url / pdf_dir / text\nsplit_documents]
    end

    subgraph VectorStore
        VS[VectorStore\nOpenAIEmbeddings + FAISS\n.as_retriever()]
    end

    subgraph Workflow
        GB[GraphBuilder\nStateGraph<RAGState>]
        RN[RAGNode\nretriever_docs / generate_answer]
        RS[RAGState\nquery, retrieved_docs, answer]
    end

    subgraph UI
        ST[Streamlit App\ninitialize_rag, forms, history]
    end

    ST --> DP
    DP --> VS
    VS --> GB
    GB --> RN
    RN --> RS
    RS --> ST
```

---

## Détails techniques

- **Ingestion**: `WebBaseLoader`, `PyPDFDirectoryLoader`, `TextLoader`
- **Découpage**: `RecursiveCharacterTextSplitter` (via `CHUNK_SIZE`, `CHUNK_OVERLAP`)
- **Indexation**: `FAISS.from_documents` + `OpenAIEmbeddings`
- **Récupération**: `retriever.invoke(query)`
- **Génération**: `llm.invoke(prompt)` avec un prompt contextuel minimaliste
- **Orchestration**: `langgraph.StateGraph` avec nœuds `retriever` → `responder`

Note: `nodes/reactnode.py` expose une variante agentique ReAct (`create_react_agent`) avec des Tools (`retriever`, `Wikipedia`).

---

## Personnaliser les sources

- **URLs**: modifier `DEFAULT_URLS` dans `src/config/config.py`
- **PDF**: déposer vos fichiers dans `data/` (chargés automatiquement)
- **Textes**: support via `TextLoader` (adapter si besoin)

---

## Conseils qualité & performance

- Ajuster `CHUNK_SIZE`/`CHUNK_OVERLAP` selon la granularité souhaitée
- Limiter la taille des PDF ou filtrer par pertinence
- Cache Streamlit déjà activé (`@st.cache_resource`)
- Surveiller les coûts OpenAI (embeddings + LLM)

---

## Dépannage rapide

- Erreur « retriever not initialized »: vérifier l’appel à `create_retriever`
- Clé API: s’assurer que `OPENAI_API_KEY` est bien défini
- Ingestion: vérifier l’accès réseau et le dossier `data/`

---

## Licence
MIT (adapter si besoin)

---

<p align="center">
  <img src="https://media.tenor.com/4Zx3f6G7W9gAAAAC/anime-stars.gif" alt="anime sparkle" width="480"/>
</p>
