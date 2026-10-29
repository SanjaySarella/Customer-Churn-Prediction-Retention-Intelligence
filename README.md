# Customer Churn Decision Analysis

An evidence-bounded analytics case study that scores a customer profile, compares it with an observed peer segment, evaluates a transparent model on held-out data, and translates score thresholds into measurable review workload.

## Dataset

The application uses 7,043 telecom customer records. Five declared operational inputs are used: tenure, monthly charges, contract, internet service, and payment method. Customer IDs are checked for uniqueness, model inputs are checked for missing values, and target labels are validated before training.

## Workflow

1. Validate identifiers, inputs, and churn labels.
2. Create a stratified 80/20 train-holdout split with a fixed seed.
3. Fit preprocessing and logistic regression on the training partition only.
4. Evaluate ROC-AUC, average precision, Brier score, log loss, and calibration on 1,409 held-out records.
5. Compare probability quality with a constant-rate baseline.
6. Explore how a threshold changes review volume, precision, and recall.

## Decision supported

The project supports a review-capacity decision: how many customer profiles would be selected at a chosen score threshold, and what historical precision-recall tradeoff did that threshold produce? It does not claim that changing a customer attribute causes churn, prescribe a retention offer, or estimate recovered revenue.

## Validation

The model achieved a holdout ROC-AUC of approximately 0.832 and average precision of approximately 0.627. Preprocessing is fitted only on the training partition. Tests verify split separation, preprocessing state, repeatable scores, peer-segment reconciliation, threshold endpoints, input rejection, and data-quality outputs.

## Tools

Python, pandas, scikit-learn, FastAPI, React, pytest, Docker, Google Cloud Run. The portable SQL preparation and quality checks are documented in `sql/analysis.sql`.

## Run locally

```bash
pip install -r requirements.txt
pytest -q
python validation/acceptance.py
```

## Live application

https://churn-intelligence-app-646m5mi6fq-uc.a.run.app/
