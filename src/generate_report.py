
from pathlib import Path
import json
import pandas as pd

from validate_data import (
    check_missing_values,
    check_duplicates,
    check_transaction_values,
)


def generate_quality_report(df):
    """Summarize data quality findings and review requirements."""

    total = len(df)

    # Apply validation functions
    df = check_missing_values(df)
    df = check_duplicates(df)
    df = check_transaction_values(df)

    # Define issues that require review
    review_flags = [
        "missing_customer_id",
        "missing_description",
        "is_duplicate",
        "unexpected_negative_quantity",
        "zero_price",
        "unexplained_negative_price",
        "cancellation_quantity_mismatch",
    ]

    df["requires_review"] = df[review_flags].any(axis=1)

    # Count each issue separately
    issue_counts = {
        flag: int(df[flag].sum())
        for flag in review_flags
    }

    report = {
        "total_records": total,
        "records_requiring_review": int(df["requires_review"].sum()),
        "issue_counts": issue_counts,
        "review_rate_percent": round(
            df["requires_review"].mean() * 100, 2
        ),
        "informational_counts": {
            "cancellation_records": int(df["is_cancellation"].sum()),
            "bad_debt_adjustments": int(
                df["is_bad_debt_adjustment"].sum()
            ),
        },
    }

    return df, report


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "online_retail_II.xlsx"
    REPORTS_DIR = BASE_DIR / "reports"

    REPORTS_DIR.mkdir(exist_ok=True)

    print("Loading dataset...")

    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    df = pd.concat(sheets.values(), ignore_index=True)

    validated_df, report = generate_quality_report(df)

    # Export aggregate report without customer-level records
    report_path = REPORTS_DIR / "quality_report.json"

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n--- DATA QUALITY REPORT ---")
    print(json.dumps(report, indent=4))

    print(f"\nReport saved to: {report_path}")
