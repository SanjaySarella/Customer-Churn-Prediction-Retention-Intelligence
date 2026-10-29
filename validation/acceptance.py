import sys,json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,brier_score_loss
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.model import get_model,FEATURES
m,df,test,p,report=get_model()
# Reconstruct every holdout score directly from transformed inputs and coefficients.
x=m.named_steps['prepare'].transform(test[FEATURES]);coef=m.named_steps['model']
z=np.asarray(x@coef.coef_.T).ravel()+coef.intercept_[0]
reference=1/(1+np.exp(-z))
assert np.allclose(reference,p,rtol=1e-12,atol=1e-12)
y=test.Churn.eq('Yes').astype(int).to_numpy()
rows=[]
for column in ['Contract','InternetService','PaymentMethod']:
 for group in sorted(test[column].unique()):
  mask=(test[column]==group).to_numpy();yy=y[mask];pp=p[mask]
  rows.append({'field':column,'group':group,'n':len(yy),'observed_churn':float(yy.mean()),'mean_score':float(pp.mean()),'brier':float(brier_score_loss(yy,pp)),'roc_auc':float(roc_auc_score(yy,pp)) if len(np.unique(yy))==2 else None})
result={'independently_reconciled_scores':len(p),'maximum_numeric_difference':float(np.max(np.abs(reference-p))),'subgroups':rows,'scope':'Historical holdout subgroup diagnostics; not external validation or evidence of intervention effectiveness.'}
print(json.dumps(result,indent=2));Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
