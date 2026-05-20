import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report
from typing import Dict, Any, List, Tuple
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "telco_churn.csv")

_model = None
_explainer = None
_feature_cols = None
_X_train = None


def build_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = df.copy()

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)
    df.drop(columns=["customerID"], inplace=True, errors="ignore")

    binary_cols = ["gender", "Partner", "Dependents", "PhoneService",
                   "PaperlessBilling", "Churn"]
    for col in binary_cols:
        if col in df.columns:
            df[col] = LabelEncoder().fit_transform(df[col])

    multi_cols = ["MultipleLines", "InternetService", "OnlineSecurity",
                  "OnlineBackup", "DeviceProtection", "TechSupport",
                  "StreamingTV", "StreamingMovies", "Contract", "PaymentMethod"]
    df = pd.get_dummies(df, columns=multi_cols, drop_first=True)

    X = df.drop(columns=["Churn"])
    y = df["Churn"]
    return X, y


def get_model():
    global _model, _explainer, _feature_cols, _X_train

    if _model is not None:
        return _model, _explainer, _feature_cols

    df = pd.read_csv(DATA_PATH)
    X, y = build_features(df)
    _feature_cols = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    _X_train = X_train

    _model = XGBClassifier(
        n_estimators=100,
        random_state=42,
        eval_metric="logloss",
        verbosity=0
    )
    _model.fit(X_train, y_train)

    _explainer = shap.TreeExplainer(_model)

    auc = roc_auc_score(y_test, _model.predict_proba(X_test)[:, 1])
    print(f"Model loaded — ROC-AUC: {auc:.4f}")

    return _model, _explainer, _feature_cols


def predict(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    model, explainer, feature_cols = get_model()
    df = pd.read_csv(DATA_PATH)
    X_full, _ = build_features(df)

    input_dict = {
        "gender": 1 if customer_data.get("gender") == "Male" else 0,
        "SeniorCitizen": 1 if customer_data.get("senior_citizen") else 0,
        "Partner": 1 if customer_data.get("partner") else 0,
        "Dependents": 1 if customer_data.get("dependents") else 0,
        "tenure": customer_data.get("tenure", 12),
        "PhoneService": 1 if customer_data.get("phone_service") else 0,
        "PaperlessBilling": 1 if customer_data.get("paperless_billing") else 0,
        "MonthlyCharges": customer_data.get("monthly_charges", 65.0),
        "TotalCharges": customer_data.get("monthly_charges", 65.0) * customer_data.get("tenure", 12),
    }

    cat_cols = {
        "MultipleLines": customer_data.get("multiple_lines", "No"),
        "InternetService": customer_data.get("internet_service", "DSL"),
        "OnlineSecurity": customer_data.get("online_security", "No"),
        "OnlineBackup": customer_data.get("online_backup", "No"),
        "DeviceProtection": customer_data.get("device_protection", "No"),
        "TechSupport": customer_data.get("tech_support", "No"),
        "StreamingTV": customer_data.get("streaming_tv", "No"),
        "StreamingMovies": customer_data.get("streaming_movies", "No"),
        "Contract": customer_data.get("contract", "Month-to-month"),
        "PaymentMethod": customer_data.get("payment_method", "Electronic check"),
    }

    for col, val in cat_cols.items():
        for feat in feature_cols:
            if feat.startswith(f"{col}_"):
                input_dict[feat] = 1 if feat == f"{col}_{val}" else 0

    input_df = pd.DataFrame([input_dict])
    for col in feature_cols:
        if col not in input_df.columns:
            input_df[col] = 0
    input_df = input_df[feature_cols]

    churn_prob = float(model.predict_proba(input_df)[0][1])
    risk_level = "HIGH" if churn_prob > 0.7 else "MEDIUM" if churn_prob > 0.4 else "LOW"

    sv = explainer.shap_values(input_df)
    sv_values = sv[0] if isinstance(sv, list) else sv[0]

    drivers = sorted(
        zip(feature_cols, sv_values),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:8]

    shap_data = [
        {"feature": d[0].replace("_", " ")[:30], "value": round(float(d[1]), 4)}
        for d in drivers
    ]

    # Similar at-risk customers
    df_orig = pd.read_csv(DATA_PATH)
    df_orig["TotalCharges"] = pd.to_numeric(df_orig["TotalCharges"], errors="coerce")
    tenure = customer_data.get("tenure", 12)
    monthly = customer_data.get("monthly_charges", 65.0)

    similar = df_orig[
        (df_orig["tenure"].between(max(0, tenure - 6), tenure + 6)) &
        (df_orig["MonthlyCharges"].between(max(0, monthly - 15), monthly + 15)) &
        (df_orig["Churn"] == "Yes")
    ].head(5)[["tenure", "MonthlyCharges", "Contract", "InternetService", "Churn"]]

    return {
        "churn_probability": round(churn_prob, 4),
        "risk_level": risk_level,
        "churn_percentage": round(churn_prob * 100, 1),
        "shap_drivers": shap_data,
        "similar_customers": similar.to_dict("records"),
        "monthly_charges": monthly,
        "tenure": tenure,
    }
