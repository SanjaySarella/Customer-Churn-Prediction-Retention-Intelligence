import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

load_dotenv()

from backend.model import predict, get_model
from backend.agent import run_churn_agent
from backend.quality import validate_input

# OpenTelemetry setup
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("churn-app")

app = FastAPI(
    title="Customer Churn Intelligence API",
    description="XGBoost + SHAP + LangGraph retention intelligence",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomerInput(BaseModel):
    gender: str = "Male"
    senior_citizen: bool = False
    partner: bool = False
    dependents: bool = False
    tenure: int = Field(12, ge=0, le=72)
    phone_service: bool = True
    multiple_lines: str = "No"
    internet_service: str = "DSL"
    online_security: str = "No"
    online_backup: str = "No"
    device_protection: str = "No"
    tech_support: str = "No"
    streaming_tv: str = "No"
    streaming_movies: str = "No"
    contract: str = "Month-to-month"
    paperless_billing: bool = True
    payment_method: str = "Electronic check"
    monthly_charges: float = Field(65.0, gt=0)


class PredictionResponse(BaseModel):
    churn_probability: float
    churn_percentage: float
    risk_level: str
    shap_drivers: list
    similar_customers: list
    retention_brief: Optional[dict]
    ragas_score: Optional[float]
    data_quality: dict


@app.on_event("startup")
async def startup_event():
    print("Loading model on startup...")
    get_model()
    print("Model ready.")


@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(customer: CustomerInput):
    with tracer.start_as_current_span("predict_churn"):

        customer_dict = customer.dict()

        # Data quality validation
        quality = validate_input(customer_dict)
        if not quality["valid"]:
            raise HTTPException(status_code=400, detail=quality["errors"])

        # ML prediction + SHAP
        with tracer.start_as_current_span("ml_inference"):
            prediction = predict(customer_dict)

        # LangGraph agent + RAG
        with tracer.start_as_current_span("agent_pipeline"):
            agent_result = run_churn_agent(customer_dict, prediction)

        return {
            **prediction,
            "retention_brief": agent_result["retention_brief"],
            "ragas_score": agent_result["ragas_score"],
            "data_quality": quality
        }


@app.get("/model-info")
def model_info():
    return {
        "model": "XGBoost Classifier",
        "features": 20,
        "training_records": 7043,
        "explainability": "SHAP TreeExplainer",
        "agent": "LangGraph + LlamaIndex + ChromaDB + Groq",
        "evaluation": "RAGAS-inspired scoring",
        "observability": "OpenTelemetry"
    }


# Serve compiled React frontend — must be mounted AFTER all API routes
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
