"""Reproducible five-feature baseline; no intervention or savings claims."""
from functools import lru_cache
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss, precision_score, recall_score
from sklearn.calibration import calibration_curve

DATA = Path(__file__).resolve().parents[1] / 'data/telco_churn.csv'
NUM = ['tenure','MonthlyCharges']
CAT = ['Contract','InternetService','PaymentMethod']
FEATURES = NUM + CAT

def build_pipeline():
    return Pipeline([('prepare',ColumnTransformer([
        ('numeric',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUM),
        ('category',OneHotEncoder(handle_unknown='error'),CAT)])),
        ('model',LogisticRegression(C=1.0,max_iter=2000,random_state=42))])

@lru_cache(maxsize=1)
def get_model():
    df = pd.read_csv(DATA)
    if df.customerID.isna().any() or df.customerID.duplicated().any():
        raise ValueError('Customer identifiers must be complete and unique.')
    if not df.Churn.isin(['Yes','No']).all():
        raise ValueError('Unexpected churn labels.')
    if df[FEATURES].isna().any().any() or not np.isfinite(df[NUM]).all().all():
        raise ValueError('Missing or nonfinite model inputs in source data.')
    train, test = train_test_split(df,test_size=.2,stratify=df.Churn,random_state=42)
    model = build_pipeline()
    model.fit(train[FEATURES],train.Churn.eq('Yes').astype(int))
    y = test.Churn.eq('Yes').astype(int).to_numpy()
    p = model.predict_proba(test[FEATURES])[:,1]
    base = np.full(len(test),train.Churn.eq('Yes').mean())
    selected_70 = p >= .70
    frac, mean = calibration_curve(y,p,n_bins=5,strategy='quantile')
    report = {'model':'Logistic regression, five declared inputs', 'dataset_rows':len(df),
              'training_rows':len(train),'test_rows':len(test), 'split':'Stratified 80/20 random split, seed 42. Historical internal validation, not a future-time or external validation.',
              'roc_auc':float(roc_auc_score(y,p)), 'average_precision':float(average_precision_score(y,p)),
              'brier_score':float(brier_score_loss(y,p)), 'baseline_brier':float(brier_score_loss(y,base)),
              'log_loss':float(log_loss(y,p)), 'baseline_log_loss':float(log_loss(y,base)),
              'test_churn_rate':float(y.mean()),
              'quality':{'duplicate_customer_ids':int(df.customerID.duplicated().sum()),
                         'missing_model_inputs':int(df[FEATURES].isna().sum().sum()),
                         'unexpected_target_labels':int((~df.Churn.isin(['Yes','No'])).sum())},
              'capacity_example':{'threshold':.70,'selected':int(selected_70.sum()),
                                  'total':len(test),
                                  'precision':float(precision_score(y,selected_70,zero_division=0)),
                                  'recall':float(recall_score(y,selected_70,zero_division=0))},
              'calibration':[{'mean_score':float(a),'observed_churn':float(b)} for a,b in zip(mean,frac)],
              'sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),
              'limitations':'Scores are historical model estimates, not individual certainty. Dataset has no future observation window or intervention outcomes. Changing an input does not establish a causal effect or savings.'}
    return model, df, test, p, report

def profile_score(tenure,monthly_charges,contract,internet_service,payment_method):
    model,df,_,_,_ = get_model()
    row = pd.DataFrame([{'tenure':tenure,'MonthlyCharges':monthly_charges,'Contract':contract,
                         'InternetService':internet_service,'PaymentMethod':payment_method}])
    score = float(model.predict_proba(row[FEATURES])[0,1])
    # Report observed historical segment; never call this an individual explanation.
    segment = df.loc[(df.Contract==contract)&(df.InternetService==internet_service)]
    return {'score':score,'inputs':row.iloc[0].to_dict(), 'segment_count':len(segment),
            'segment_churn_rate':float(segment.Churn.eq('Yes').mean()) if len(segment) else None,
            'interpretation':'Review score only. Segment rates are descriptive and do not explain why this individual would churn. No discount or revenue-saved recommendation is inferred.'}

def review_queue(threshold):
    _,_,test,p,_ = get_model()
    y = test.Churn.eq('Yes').astype(int).to_numpy()
    selected = p >= threshold
    rows = test[FEATURES+['Churn']].copy()
    # Anonymous display identifiers; retain source IDs only in local split verification.
    rows['Review ID'] = ['holdout-'+str(i+1) for i in range(len(rows))]
    rows['Score'] = p
    return {'threshold':threshold,'selected':int(selected.sum()),'total':len(test),
            'precision':float(precision_score(y,selected,zero_division=0)) if selected.any() else None,
            'recall':float(recall_score(y,selected,zero_division=0)),
            'rows':rows.loc[selected].sort_values('Score',ascending=False).to_dict('records'),
            'note':'Historical holdout simulation. Actual outcomes are shown for evaluation only and are never model inputs. Threshold exploration on this holdout is illustrative; a chosen policy needs new independent evaluation.'}
