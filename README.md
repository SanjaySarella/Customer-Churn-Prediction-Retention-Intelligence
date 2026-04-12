# 📊 Customer Churn Prediction & Retention Intelligence

A comprehensive machine learning pipeline and AI-driven retention system designed to predict customer churn, identify key drivers using SHAP, and generate actionable retention strategies via a LangChain agent.

---

## 🚀 Project Overview

This project transforms raw Telco customer data into actionable business intelligence. It covers the full lifecycle from EDA to model deployment and local interpretability.

### **Key Features**
- **Exploratory Data Analysis**: Identification of high-churn segments (Contract type, Internet Service).
- **Advanced Modeling**: Comparison between Random Forest and XGBoost with AUC scoring.
- **Model Explainability**: Global and individual feature importance using **SHAP**.
- **Retention AI Agent**: LangChain-powered agent that converts model outputs into professional retention briefs.

---

## 📈 Model Performance Dashboard

| Model | AUC Score | Status |
| :--- | :--- | :--- |
| **XGBoost** | **0.8258** | **Winner** |
| Random Forest | 0.8146 | - |

> [!TIP]
> **Top Churn Drivers**: `Contract`, `InternetService`, `Tenure`, `MonthlyCharges`, `TotalCharges`.

---

## 🛠️ Project Structure

```bash
.
├── data/
│   └── telco_churn.csv            # Cleaned Telco dataset
├── notebooks/
│   ├── 01_eda.ipynb               # Visualization & Cleaning
│   ├── 02_modeling.ipynb          # RF & XGBoost Training
│   ├── 03_shap.ipynb              # Model Interpretability
│   └── 04_langchain_agent.ipynb   # AI Retention Strategist
├── outputs/
│   ├── churn_by_segment.png       # EDA Insight
│   ├── shap_summary.png           # Global Feature Importance
│   └── shap_feature_importance.csv# Data for AI Agent
├── requirements.txt               # Project Dependencies
└── README.md                      # Project Dashboard
```

---

## 🤖 AI Retention Agent in Action

Using the insights from the XGBoost model and SHAP values, the integrated **LangChain Agent** performs:
1. **At-Risk Identification**: Prioritizes customers with >80% churn probability.
2. **Strategy Generation**: Recommends specific actions (e.g., "Upgrade to Fiber + Online Security bundle") based on customer profile.
3. **Professional Briefing**: Generates concise reports for retention managers.

---

## 💻 Tech Stack
- **Languages**: Python (Pandas, NumPy)
- **ML/DS**: Scikit-Learn, XGBoost, SHAP
- **AI/LLM**: LangChain, OpenAI, Ollama
- **Visualization**: Matplotlib, Seaborn

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/SanjaySarella/Customer-Churn-Prediction-Retention-Intelligence.git

# Install dependencies
pip install -r requirements.txt
```

---
*Developed for Customer Intelligence and Churn Reduction.*
