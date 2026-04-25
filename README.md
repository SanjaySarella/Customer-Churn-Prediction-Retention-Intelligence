# Customer Churn Prediction — Retention Intelligence

**Sanjay Sarella** | M.S. Data Analytics, Oklahoma City University

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Classifier-orange)](https://xgboost.readthedocs.io)
[![SHAP](https://img.shields.io/badge/SHAP-Explainability-green)](https://shap.readthedocs.io)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3--70B-green)](https://console.groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20App-red?logo=streamlit)](https://streamlit.io)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-blue?logo=googlecloud)](https://cloud.google.com)

## Live App
**[Launch App](https://churn-intelligence-app-646m5mi6fq-uc.a.run.app/)**

---

## The Problem

Acquiring a new customer costs 5–7x more than retaining an existing one. In telecom, monthly churn rates of 2–3% compound into significant annual revenue loss — yet most retention efforts are reactive, targeting customers after they have already decided to leave.

This system identifies at-risk customers before they churn and generates a specific retention strategy for each one.

---

## What This Does

An end-to-end churn intelligence system built on 7,043 real Telco customer records. It predicts individual churn probability using XGBoost, explains every prediction at the feature level using SHAP, surfaces similar at-risk customers from historical data, and generates a targeted retention brief via a Groq + Llama 3.3-70B AI agent — all from a single interface.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                 |
│  7,043 Telco customer records                               │
│  20 features: tenure, contract type, charges, services      │
│  Target: Churn (Yes / No)                                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  ML LAYER                                                   |
│  Random Forest vs XGBoost — head-to-head evaluation         |
│  XGBoost selected as winner on ROC-AUC                      │
│  SHAP TreeExplainer → per-customer feature attribution      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  AGENT LAYER                                                │
│  Groq + Llama 3.3-70B                                       │
│  Input: churn probability + SHAP drivers + customer profile │
│  Output: Risk assessment + 3 retention actions + offer      │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Results

| Metric | Value |
|---|---|
| Dataset | 7,043 real Telco customer records |
| Models evaluated | Random Forest vs XGBoost |
| Winner | XGBoost (higher ROC-AUC) |
| Features | 20 customer attributes |
| Churn rate in dataset | ~26% |
| Deployment | GCP Cloud Run — live public URL |
| Total cost | $0 — fully open source |

---

## What Makes This Different

**Head-to-head model evaluation**
Both Random Forest and XGBoost were trained and evaluated on the same data. The winner was selected based on ROC-AUC - not assumed. The modeling notebook documents both results transparently.

**Per-customer SHAP explanations**
Global feature importance tells you what drives churn on average. Per-customer SHAP waterfall charts tell you exactly why this specific customer is at risk — whether it is their contract type, tenure, monthly charges, or lack of tech support. The distinction matters for retention strategy.

**Retention strategy tied to SHAP drivers**
The AI agent does not generate a generic retention script. It reads the actual SHAP values for each customer and builds a strategy around the specific factors driving their churn risk. A customer at risk due to high monthly charges gets a different recommendation than one at risk due to a month-to-month contract.

**Deployed on GCP Cloud Run**
Containerized with Docker and deployed on Google Cloud Run. The app trains the model on first load from the raw dataset - no separate model file required, no external dependencies beyond what is in requirements.txt.

---

## How to Use the App

1. Open the **[live app](https://churn-intelligence-app-646m5mi6fq-uc.a.run.app/)**
2. Configure a customer profile in the sidebar — tenure, contract type, services, charges
3. Click **Run Churn Analysis**
4. The system returns:
   - Churn probability with risk level (High / Medium / Low)
   - SHAP waterfall chart showing the top 6 drivers for this customer
   - Similar at-risk customers from historical data
   - AI-generated retention brief with 3 specific actions and an offer recommendation

---

## Tech Stack

| Category | Tools |
|---|---|
| ML & Explainability | XGBoost · Random Forest · Scikit-learn · SHAP |
| AI Agent | Groq + Llama 3.3-70B · LangChain |
| App | Streamlit |
| Deployment | Docker · GCP Cloud Run |
| Data | Pandas · NumPy · Matplotlib · Seaborn |
| Visualization | Tableau Public · SHAP plots |
| Dev | Python 3.11 · Jupyter · Git |

**100% open source. Zero cost.**

---

## Project Structure

```
Customer-Churn-Prediction-Retention-Intelligence/
├── app.py                        ← Streamlit app — prediction, SHAP, agent
├── data/
│   └── telco_churn.csv           ← 7,043 Telco customer records
├── customer-churn-intelligence/
│   └── notebooks/
│       ├── 01_eda.ipynb          ← Exploratory data analysis
│       ├── 02_modeling.ipynb     ← RF vs XGBoost head-to-head evaluation
│       ├── 03_shap.ipynb         ← SHAP global and per-customer analysis
│       └── 04_langchain_agent.ipynb ← AI retention agent development
├── outputs/                      ← SHAP plots and exports
├── Dockerfile                    ← GCP Cloud Run containerization
├── requirements.txt
└── README.md
```

---

## Tableau Public Dashboard
**[View Live Dashboard](https://public.tableau.com/app/profile/sanjay.sarella/viz/TelecomChurnIntelligenceCustomerRetentionStrategy/TelecomChurnIntelligenceDashboard500KAnnualRevenueatRisk)**

---

## Author

**Sanjay Sarella**
M.S. Data Analytics — Oklahoma City University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Sanjay%20Sarella-blue?logo=linkedin)](https://linkedin.com/in/sanjaysarella)
[![GitHub](https://img.shields.io/badge/GitHub-SanjaySarella-black?logo=github)](https://github.com/SanjaySarella)
