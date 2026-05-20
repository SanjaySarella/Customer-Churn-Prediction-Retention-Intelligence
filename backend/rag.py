import os
import chromadb
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

_collection = None

def build_knowledge_base():
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.EphemeralClient()
    _collection = client.get_or_create_collection("churn_knowledge")

    docs = [
        "Customer churn in telecom is driven by contract type, monthly charges, and tenure. Month-to-month customers are 3x more likely to churn. Customers with charges above $70 and tenure below 12 months are highest risk. Retention strategies include contract upgrades, bundle offers, and proactive outreach within 6 months.",
        "Retention best practices: HIGH risk customers need immediate outreach. Effective offers include 20% discount for 12-month upgrade, free service add-ons, loyalty rewards. Cost to retain is $50-150 vs $300-500 to acquire new.",
        "SHAP explainability: top features are monthly charges relative to usage, short tenure, month-to-month contracts, absence of value-add services. When tenure dominates the customer is new. When charges dominate the customer perceives poor value.",
        "Service patterns: customers without online security or tech support churn more. Fiber optic customers have higher price sensitivity. Electronic check payment correlates with higher churn due to lower switching costs.",
    ]

    _collection.add(
        documents=docs,
        ids=[f"doc_{i}" for i in range(len(docs))]
    )
    return _collection


def retrieve_retention_strategy(query: str) -> str:
    collection = build_knowledge_base()
    results = collection.query(query_texts=[query], n_results=2)
    return "\n".join(results["documents"][0])
