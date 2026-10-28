from pathlib import Path
from typing import Literal
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,ConfigDict
from backend.model import get_model, profile_score, review_queue
app = FastAPI(title='Customer Churn Analysis',version='3.0.0')
class CustomerInput(BaseModel):
    model_config = ConfigDict(extra='forbid',allow_inf_nan=False)
    tenure:int=Field(12,ge=0,le=72)
    monthly_charges:float=Field(65,ge=18.25,le=118.75)
    contract:Literal['Month-to-month','One year','Two year']='Month-to-month'
    internet_service:Literal['DSL','Fiber optic','No']='DSL'
    payment_method:Literal['Electronic check','Mailed check','Bank transfer (automatic)','Credit card (automatic)']='Electronic check'
class ReviewInput(BaseModel):
    model_config = ConfigDict(extra='forbid',allow_inf_nan=False)
    threshold:float=Field(.5,ge=0,le=1)
@app.get('/health')
def health():
    return {'status':'ok','version':'3.0.0'}
@app.get('/model-info')
def info():
    return get_model()[4]
@app.post('/predict')
def predict(data:CustomerInput):
    return profile_score(**data.model_dump())
@app.post('/review')
def review(data:ReviewInput):
    return review_queue(data.threshold)
static=Path(__file__).resolve().parents[1]/'static'
if static.exists():
    app.mount('/',StaticFiles(directory=static,html=True),name='frontend')
