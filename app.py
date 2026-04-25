import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import warnings
warnings.filterwarnings("ignore")

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

st.set_page_config(
    page_title="Customer Churn Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("Customer Churn Prediction — Retention Intelligence")
st.markdown("*AI-powered churn prediction and retention strategy for telecom customers*")
st.divider()

# ── Load and preprocess data ──────────────────────────────────────────────────

@st.cache_resource
def load_and_train():
    df = pd.read_csv("data/telco_churn.csv")

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)
    df.drop(columns=["customerID"], inplace=True)

    binary_cols = [
        "gender", "Partner", "Dependents", "PhoneService",
        "PaperlessBilling", "Churn"
    ]
    for col in binary_cols:
        df[col] = LabelEncoder().fit_transform(df[col])

    multi_cols = [
        "MultipleLines", "InternetService", "OnlineSecurity",
        "OnlineBackup", "DeviceProtection", "TechSupport",
        "StreamingTV", "StreamingMovies", "Contract", "PaymentMethod"
    ]
    df = pd.get_dummies(df, columns=multi_cols, drop_first=True)

    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=100,
        random_state=42,
        eval_metric="logloss",
        verbosity=0
    )
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    return model, explainer, X, X_test, y_test, auc, df

model, explainer, X, X_test, y_test, auc, df = load_and_train()

# ── Load LLM ──────────────────────────────────────────────────────────────────

@st.cache_resource
def load_llm():
    groq_key = os.getenv("GROQ_API_KEY", "")
    return ChatGroq(
        api_key=groq_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.3
    )

llm = load_llm()

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.header("Customer Profile")

gender          = st.sidebar.selectbox("Gender", ["Male", "Female"])
senior          = st.sidebar.selectbox("Senior Citizen", ["No", "Yes"])
partner         = st.sidebar.selectbox("Has Partner", ["Yes", "No"])
dependents      = st.sidebar.selectbox("Has Dependents", ["Yes", "No"])
tenure          = st.sidebar.slider("Tenure (months)", 0, 72, 12)
phone_service   = st.sidebar.selectbox("Phone Service", ["Yes", "No"])
multiple_lines  = st.sidebar.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
internet        = st.sidebar.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
online_security = st.sidebar.selectbox("Online Security", ["Yes", "No", "No internet service"])
online_backup   = st.sidebar.selectbox("Online Backup", ["Yes", "No", "No internet service"])
device_protect  = st.sidebar.selectbox("Device Protection", ["Yes", "No", "No internet service"])
tech_support    = st.sidebar.selectbox("Tech Support", ["Yes", "No", "No internet service"])
streaming_tv    = st.sidebar.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
streaming_movies= st.sidebar.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
contract        = st.sidebar.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
paperless       = st.sidebar.selectbox("Paperless Billing", ["Yes", "No"])
payment         = st.sidebar.selectbox("Payment Method", [
    "Electronic check", "Mailed check",
    "Bank transfer (automatic)", "Credit card (automatic)"
])
monthly_charges = st.sidebar.slider("Monthly Charges ($)", 18.0, 120.0, 65.0)
total_charges   = monthly_charges * tenure

run_button = st.sidebar.button("Run Churn Analysis", type="primary", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────────────────────

if run_button:

    # Build input row matching training columns
    input_dict = {
        "gender"          : 1 if gender == "Male" else 0,
        "SeniorCitizen"   : 1 if senior == "Yes" else 0,
        "Partner"         : 1 if partner == "Yes" else 0,
        "Dependents"      : 1 if dependents == "Yes" else 0,
        "tenure"          : tenure,
        "PhoneService"    : 1 if phone_service == "Yes" else 0,
        "PaperlessBilling": 1 if paperless == "Yes" else 0,
        "MonthlyCharges"  : monthly_charges,
        "TotalCharges"    : total_charges,
    }

    # One-hot encode categorical columns to match training
    cat_cols = {
        "MultipleLines"   : multiple_lines,
        "InternetService" : internet,
        "OnlineSecurity"  : online_security,
        "OnlineBackup"    : online_backup,
        "DeviceProtection": device_protect,
        "TechSupport"     : tech_support,
        "StreamingTV"     : streaming_tv,
        "StreamingMovies" : streaming_movies,
        "Contract"        : contract,
        "PaymentMethod"   : payment
    }

    for col, val in cat_cols.items():
        for cat_val in df.columns:
            prefix = f"{col}_"
            if cat_val.startswith(prefix):
                input_dict[cat_val] = 1 if cat_val == f"{col}_{val}" else 0

    input_df = pd.DataFrame([input_dict])
    for col in X.columns:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[X.columns]

    # Predict
    churn_prob  = model.predict_proba(input_df)[0][1]
    churn_label = "High Risk" if churn_prob > 0.7 else \
                  "Medium Risk" if churn_prob > 0.4 else "Low Risk"
    risk_color  = "🔴" if churn_prob > 0.7 else \
                  "🟡" if churn_prob > 0.4 else "🟢"

    # SHAP for this customer
    sv          = explainer.shap_values(input_df)
    sv_values   = sv[0] if isinstance(sv, list) else sv[0]
    drivers     = sorted(
        zip(X.columns, sv_values),
        key=lambda x: abs(x[1]), reverse=True
    )[:6]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Churn Probability", f"{churn_prob:.1%}")
    col2.metric("Risk Level", f"{risk_color} {churn_label}")
    col3.metric("Tenure", f"{tenure} months")
    col4.metric("Monthly Charges", f"${monthly_charges:.2f}")

    st.divider()

    left, right = st.columns(2)

    # ── SHAP chart ─────────────────────────────────────────────────────────────
    with left:
        st.subheader("SHAP Driver Analysis")
        fig, ax = plt.subplots(figsize=(6, 4))
        features_list = [d[0].replace("_", " ")[:25] for d in drivers]
        values_list   = [d[1] for d in drivers]
        colors        = ["#C00000" if v > 0 else "#2E75B6" for v in values_list]
        ax.barh(features_list, values_list, color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("SHAP Value (impact on churn probability)")
        ax.set_title("Top Factors Driving This Prediction")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # ── At-risk customer segment ───────────────────────────────────────────────
    with right:
        st.subheader("Similar At-Risk Customers")
        similar = df[
            (df["tenure"].between(max(0, tenure-6), tenure+6)) &
            (df["MonthlyCharges"].between(
                max(0, monthly_charges-15), monthly_charges+15)
            ) &
            (df["Churn"] == 1)
        ].head(5)

        if not similar.empty:
            st.dataframe(
                similar[["tenure","MonthlyCharges","TotalCharges","Contract_One year","Contract_Two year"]],
                use_container_width=True
            )
        else:
            st.info("No similar churned customers found in this segment.")

    st.divider()

    # ── AI retention brief ────────────────────────────────────────────────────
    st.subheader("AI Retention Strategy Brief")
    with st.spinner("Generating retention strategy..."):
        drivers_text = "\n".join([
            f"- {d[0]}: {d[1]:+.4f}" for d in drivers
        ])
        prompt = f"""You are a senior telecom customer retention strategist.

CUSTOMER PROFILE:
- Tenure: {tenure} months
- Monthly Charges: ${monthly_charges:.2f}
- Contract: {contract}
- Internet Service: {internet}
- Tech Support: {tech_support}
- Churn Probability: {churn_prob:.1%} ({churn_label})

TOP CHURN DRIVERS (SHAP):
{drivers_text}

Write a retention brief with exactly this structure:
RISK ASSESSMENT: [one sentence]
TOP 3 RETENTION ACTIONS:
1. [specific action + expected outcome]
2. [specific action + expected outcome]
3. [specific action + expected outcome]
OFFER RECOMMENDATION: [specific offer with dollar value]
BOTTOM LINE: [one sentence a retention manager would act on immediately]"""

        response = llm.invoke([
            SystemMessage(content="You are a telecom retention strategist. Be specific and actionable."),
            HumanMessage(content=prompt)
        ])
        st.markdown(response.content)

    st.divider()

    # ── Global SHAP summary ───────────────────────────────────────────────────
    st.subheader("Global Feature Importance")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists("outputs/shap_summary.png"):
            st.image("outputs/shap_summary.png", caption="SHAP Summary — All Customers")
        else:
            shap_vals = explainer.shap_values(X_test)
            fig, ax   = plt.subplots(figsize=(8, 5))
            shap.summary_plot(shap_vals, X_test, plot_type="bar",
                              show=False, max_display=10)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    with col2:
        st.metric("Model ROC-AUC", f"{auc:.4f}")
        st.markdown("""
        **Model:** XGBoost Classifier
        **Training data:** 7,043 Telco customers
        **Features:** 20 customer attributes
        **Target:** Churn (Yes/No)
        """)

else:
    st.info("Configure a customer profile in the sidebar and click **Run Churn Analysis**.")
    st.markdown("""
    ### How This Works
    - **Prediction** — XGBoost model trained on 7,043 real Telco customers
    - **Explainability** — SHAP values show which factors drive each individual prediction
    - **Segmentation** — Similar at-risk customers surfaced from historical data
    - **Strategy Agent** — Groq + Llama 3.3-70B generates a specific retention brief
    """)