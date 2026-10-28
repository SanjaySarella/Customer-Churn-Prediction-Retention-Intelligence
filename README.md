# Customer Churn Analysis

A historical telecom study by Sanjay Sarella. Three outputs: profile score with observed segment context, independent holdout evaluation, and a threshold-based review workload simulation.

## Model and evidence

The model is a logistic regression baseline with five declared inputs: tenure, monthly charges, contract, internet service and payment method. Demographics, fabricated total charges, unsolicited discounts, AI quality percentages and claimed savings are excluded from the supported runtime.

7,043 unique customer records are split into 5,634 training and 1,409 test records using a stratified 80/20 split and seed 42. Numeric imputation/scaling and categorical encoding are fitted inside a pipeline on training data only. Model settings are fixed, not selected using holdout results. The app reports ROC-AUC, average precision, Brier score, log loss and five-bin calibration evidence. Its comparison is a constant training-churn-rate baseline. This is historical internal validation, not external or future-period validation.

Observed local results: ROC-AUC 0.8323; average precision 0.6267; Brier score 0.1424 versus 0.1950 baseline; log loss 0.4303 versus 0.5787 baseline. Reproduce using the exact dependency versions and data fingerprint before comparing releases. No claim is made that this model outperforms the retired XGBoost model, which was not re-evaluated under this new protocol.

Profile scores are estimates, not individual certainty. Same-contract/internet segment rates are descriptive, not causal explanations. The dataset supplies no reliable prediction horizon or intervention outcome. Review thresholds are explored on held-out historical records for illustration; choosing a policy after inspecting these results requires fresh independent evaluation. Customer IDs are not displayed in the review list.

## Run and test

```sh
python -m pip install -r backend/requirements.txt pytest httpx
cd frontend
npm ci --legacy-peer-deps
npm run build
cd ..
cp -r frontend/build static
python -m uvicorn backend.main:app --port 8080
```

`python -m pytest tests -q` verifies split isolation, train-only preprocessing, deterministic scores, segment reconciliation, threshold endpoints and API rejection of invalid or undeclared inputs. Historical agent modules, notebooks and figures are retained for provenance only, not used by the supported runtime. The old Streamlit entry point is retired.

## Deployment boundary

Candidate implementation, not deployed. Preserve the existing `churn-intelligence-app` Cloud Run service and URL. Confirm its project, region, configuration and rollback revision before staging. Container and live-browser verification remain required; cloud deployment access is not available in the current environment.
