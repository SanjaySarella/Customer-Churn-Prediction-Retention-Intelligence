import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.model import get_model,build_pipeline,profile_score,review_queue,FEATURES
client=TestClient(app)

def test_split_and_training_preprocessing():
    model,df,test,p,report=get_model()
    train=df.drop(test.index)
    assert set(train.customerID).isdisjoint(test.customerID)
    assert report['training_rows']+report['test_rows']==len(df)
    scaler=model.named_steps['prepare'].named_transformers_['numeric'].named_steps['scale']
    assert scaler.mean_==pytest.approx(train[['tenure','MonthlyCharges']].mean().to_numpy())
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()

def test_transform_does_not_refit():
    model,df,_,_,_=get_model()
    original=model.named_steps['prepare'].named_transformers_['numeric'].named_steps['impute'].statistics_.copy()
    weird=df[FEATURES].iloc[:2].copy();weird['MonthlyCharges']=999999
    model.predict_proba(weird)
    assert np.array_equal(original,model.named_steps['prepare'].named_transformers_['numeric'].named_steps['impute'].statistics_)

def test_score_reproducibility_and_segment():
    a=profile_score(12,65,'Month-to-month','DSL','Electronic check')
    b=profile_score(12,65,'Month-to-month','DSL','Electronic check')
    assert a==b
    _,df,_,_,_=get_model()
    segment=df[(df.Contract=='Month-to-month')&(df.InternetService=='DSL')]
    assert a['segment_count']==len(segment)
    assert a['segment_churn_rate']==pytest.approx(segment.Churn.eq('Yes').mean())

def test_threshold_endpoints():
    all_rows=review_queue(0);none=review_queue(1)
    assert all_rows['selected']==all_rows['total'] and all_rows['recall']==1
    assert none['selected']==0 and none['precision'] is None
    assert review_queue(.3)['selected']>=review_queue(.7)['selected']

def test_input_rejection():
    for body in [{'tenure':-1},{'tenure':1.5},{'monthly_charges':1},{'contract':'unknown'}, {'online_security':'Yes','internet_service':'No'}]:
        assert client.post('/predict',json=body).status_code==422
    assert client.post('/review',json={'threshold':1.1}).status_code==422
    assert client.post('/predict',json={}).status_code==200

def test_model_info_and_queue():
    assert client.get('/model-info').json()['test_rows']==1409
    r=client.post('/review',json={'threshold':.5})
    assert r.status_code==200
    assert all(x['Score']>=.5 for x in r.json()['rows'])
