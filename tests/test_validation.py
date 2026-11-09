import pandas as pd

from src.validate_data import (
    check_missing_values,
    check_duplicates,
    check_transaction_values,
)

from src.privacy_audit import (
    pseudonymize_customer_ids,
    detect_pii_columns,
    mask_pii,
)


def test_missing_values():
    df = pd.DataFrame({
        "Customer ID": [1001, None],
        "Description": ["Product A", None]
    })

    result = check_missing_values(df)

    assert result["missing_customer_id"].tolist() == [False, True]
    assert result["missing_description"].tolist() == [False, True]


def test_duplicates():
    df = pd.DataFrame({
        "Invoice": ["100", "100", "101"],
        "StockCode": ["A", "A", "B"],
        "Description": ["Item A", "Item A", "Item B"],
        "Quantity": [2, 2, 1],
        "InvoiceDate": pd.to_datetime([
            "2026-01-01", "2026-01-01", "2026-01-02"
        ]),
        "Price": [10.0, 10.0, 5.0],
        "Customer ID": [1001, 1001, 1002],
        "Country": ["UK", "UK", "UK"]
    })

    result = check_duplicates(df)

    assert result["is_duplicate"].tolist() == [False, True, False]


def test_transaction_classification():
    df = pd.DataFrame({
        "Invoice": ["100", "C101", "A102"],
        "StockCode": ["A", "B", "B"],
        "Description": ["Product", "Product", "Adjust bad debt"],
        "Quantity": [2, -1, 1],
        "Price": [10.0, 10.0, -50.0]
    })

    result = check_transaction_values(df)

    assert result["is_cancellation"].tolist() == [False, True, False]
    assert result["negative_quantity"].tolist() == [False, True, False]
    assert result["is_bad_debt_adjustment"].tolist() == [False, False, True]
    assert result["unexplained_negative_price"].sum() == 0


def test_pseudonymization():
    df = pd.DataFrame({
        "Customer ID": [13085, 17850, 13085, None]
    })

    result = pseudonymize_customer_ids(df, "test-secret-key")

    assert result.loc[0, "Customer ID"] == result.loc[2, "Customer ID"]
    assert result.loc[0, "Customer ID"] != result.loc[1, "Customer ID"]
    assert pd.isna(result.loc[3, "Customer ID"])
    assert result.loc[0, "Customer ID"] != 13085


def test_pii_detection_and_masking():
    df = pd.DataFrame({
        "Full Name": ["Sarah Johnson"],
        "Email": ["sarah@example.com"],
        "Phone Number": ["514-555-0101"],
        "Purchase Amount": [150]
    })

    detected = detect_pii_columns(df)

    assert detected["Full Name"] == "Name"
    assert detected["Email"] == "Email Address"
    assert detected["Phone Number"] == "Phone Number"

    masked = mask_pii(df)

    assert masked.loc[0, "Full Name"] == "[REDACTED_NAME]"
    assert masked.loc[0, "Email"] == "[REDACTED_EMAIL]"
    assert masked.loc[0, "Phone Number"] == "[REDACTED_PHONE]"
    assert masked.loc[0, "Purchase Amount"] == 150
