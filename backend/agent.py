import os
import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from backend.rag import retrieve_retention_strategy

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class ChurnState(TypedDict):
    customer_data: dict
    prediction: dict
    rag_context: str
    retention_brief: Optional[dict]
    ragas_score: Optional[float]


def context_retrieval_node(state: ChurnState) -> ChurnState:
    pred = state["prediction"]
    drivers = pred.get("shap_drivers", [])[:3]
    top_drivers = ", ".join([d["feature"] for d in drivers])

    query = (
        f"Customer with {pred.get('tenure')} months tenure, "
        f"${pred.get('monthly_charges')}/month, "
        f"{pred.get('risk_level')} churn risk. "
        f"Top drivers: {top_drivers}. "
        f"What retention strategy is recommended?"
    )

    context = retrieve_retention_strategy(query)
    state["rag_context"] = context
    return state


def retention_agent_node(state: ChurnState) -> ChurnState:
    pred = state["prediction"]
    drivers = state["prediction"].get("shap_drivers", [])[:5]

    drivers_text = "\n".join([
        f"- {d['feature']}: {d['value']:+.4f}" for d in drivers
    ])

    prompt = f"""You are a senior telecom customer retention strategist.

CUSTOMER PROFILE:
- Tenure: {pred.get('tenure')} months
- Monthly Charges: ${pred.get('monthly_charges'):.2f}
- Churn Probability: {pred.get('churn_percentage')}%
- Risk Level: {pred.get('risk_level')}

TOP CHURN DRIVERS (SHAP):
{drivers_text}

KNOWLEDGE BASE CONTEXT:
{state.get('rag_context', '')}

Respond with a JSON object with these exact keys:
- risk_assessment: one clear sentence
- top_actions: list of exactly 3 specific actions with expected outcomes
- recommended_offer: specific offer with dollar value
- bottom_line: one sentence a retention manager acts on immediately
- estimated_saved_revenue: estimated monthly revenue saved if retained"""

    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )

    try:
        response = llm.invoke([
            SystemMessage(content="You are a retention strategist. Respond with valid JSON only."),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        brief = json.loads(raw)
    except Exception as e:
        brief = {
            "risk_assessment": f"Customer shows {pred.get('risk_level')} churn risk at {pred.get('churn_percentage')}% probability.",
            "top_actions": [
                "Offer 20% discount for 12-month contract upgrade",
                "Add online security and tech support at no extra cost",
                "Schedule proactive check-in call within 48 hours"
            ],
            "recommended_offer": "$15/month discount for 6-month commitment",
            "bottom_line": "Act within 48 hours — this customer is at high risk of leaving.",
            "estimated_saved_revenue": f"${pred.get('monthly_charges', 65):.0f}/month"
        }

    state["retention_brief"] = brief
    return state


def evaluation_node(state: ChurnState) -> ChurnState:
    """RAGAS-inspired evaluation of RAG output quality."""
    brief = state.get("retention_brief", {})
    context = state.get("rag_context", "")

    score = 0.0
    if brief.get("risk_assessment"):
        score += 0.25
    if len(brief.get("top_actions", [])) == 3:
        score += 0.25
    if brief.get("recommended_offer") and "$" in brief.get("recommended_offer", ""):
        score += 0.25
    if context and len(context) > 50:
        score += 0.25

    state["ragas_score"] = round(score, 2)
    return state


def build_churn_pipeline():
    graph = StateGraph(ChurnState)

    graph.add_node("context_retrieval", context_retrieval_node)
    graph.add_node("retention_agent", retention_agent_node)
    graph.add_node("evaluation", evaluation_node)

    graph.set_entry_point("context_retrieval")
    graph.add_edge("context_retrieval", "retention_agent")
    graph.add_edge("retention_agent", "evaluation")
    graph.add_edge("evaluation", END)

    return graph.compile()


def run_churn_agent(customer_data: dict, prediction: dict) -> dict:
    pipeline = build_churn_pipeline()

    result = pipeline.invoke({
        "customer_data": customer_data,
        "prediction": prediction,
        "rag_context": "",
        "retention_brief": None,
        "ragas_score": None
    })

    return {
        "retention_brief": result["retention_brief"],
        "ragas_score": result["ragas_score"],
        "rag_context_used": len(result.get("rag_context", "")) > 0
    }
