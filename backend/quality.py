import pandas as pd
import numpy as np
from typing import Dict, Any

def validate_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Great Expectations-style validation on incoming
    customer data before inference.
    """
    errors = []
    warnings = []

    # tenure must be 0-72
    if not (0 <= data.get("tenure", -1) <= 72):
        errors.append("tenure must be between 0 and 72 months")

    # monthly charges must be positive
    if data.get("monthly_charges", 0) <= 0:
        errors.append("monthly_charges must be greater than 0")

    # total charges consistency
    tenure = data.get("tenure", 0)
    monthly = data.get("monthly_charges", 0)
    total = data.get("total_charges", 0)
    if tenure > 0 and total < monthly:
        warnings.append("total_charges seems low relative to tenure and monthly_charges")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate the training dataset."""
    results = {}

    # Check completeness
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    results["missing_values"] = missing[missing > 0].to_dict()

    # Check duplicates
    results["duplicate_rows"] = int(df.duplicated().sum())

    # Check class balance
    if "Churn" in df.columns:
        churn_rate = df["Churn"].mean()
        results["churn_rate"] = round(float(churn_rate), 4)
        if churn_rate < 0.05 or churn_rate > 0.95:
            results["class_imbalance_warning"] = True

    # Check numeric ranges
    if "MonthlyCharges" in df.columns:
        results["monthly_charges_range"] = {
            "min": float(df["MonthlyCharges"].min()),
            "max": float(df["MonthlyCharges"].max()),
            "mean": float(df["MonthlyCharges"].mean())
        }

    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)
    results["passed"] = len(results.get("missing_values", {})) == 0

    return results
