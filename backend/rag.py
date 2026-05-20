import os
from typing import List, Dict, Any
from chromadb import Client
import chromadb
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.llms.groq import Groq
from llama_index.core.embeddings import resolve_embed_model

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

_index = None
_query_engine = None


def build_knowledge_base() -> VectorStoreIndex:
    global _index, _query_engine

    if _index is not None:
        return _index

    Settings.llm = Groq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    )
    Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

    chroma_client = chromadb.EphemeralClient()
    chroma_collection = chroma_client.get_or_create_collection("churn_knowledge")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = [
        Document(text="""
            Customer churn in telecom is primarily driven by contract type,
            monthly charges, and tenure. Month-to-month contract customers
            are 3x more likely to churn than two-year contract customers.
            Customers with monthly charges above $70 and tenure below 12 months
            represent the highest risk segment. Effective retention strategies
            include contract upgrades, service bundle offers, and proactive
            outreach within the first 6 months of service.
        """),
        Document(text="""
            Retention intervention best practices: customers flagged as HIGH risk
            (churn probability above 70%) should receive immediate outreach.
            Effective offers include: 20% discount for 12-month contract upgrade,
            free service add-ons (online security, tech support), loyalty rewards
            for tenure milestones. Average cost to retain a customer is $50-150,
            compared to $300-500 to acquire a new one.
        """),
        Document(text="""
            SHAP explainability in churn models: the most impactful features
            are typically lag indicators of dissatisfaction — high monthly charges
            relative to usage, short tenure, month-to-month contracts, and absence
            of value-add services. When tenure is the top driver, the customer
            is new and has not yet committed. When monthly charges dominate,
            the customer perceives poor value for money.
        """),
        Document(text="""
            Service usage patterns and churn correlation: customers without
            online security or tech support are significantly more likely to churn.
            Fiber optic internet customers churn at higher rates than DSL customers
            due to higher price sensitivity. Electronic check payment method
            correlates with higher churn — these customers have lower switching costs.
        """),
    ]

    _index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    _query_engine = _index.as_query_engine(similarity_top_k=2)

    return _index


def retrieve_retention_strategy(query: str) -> str:
    build_knowledge_base()
    response = _query_engine.query(query)
    return str(response)
