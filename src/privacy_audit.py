import pandas as pd
import hashlib
import hmac
import os


def pseudonymize_customer_ids(df, secret_key):
    """Replace customer IDs with consistent pseudonyms."""

    df = df.copy()

    def create_pseudonym(customer_id):

        # Preserve missing customer IDs
        if pd.isna(customer_id):
            return None

        # Convert customer ID to a consistent string
        customer_id = str(int(customer_id))

        # Generate a pseudonym using a secret key
        hashed_id = hmac.new(
            secret_key.encode("utf-8"),
            customer_id.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return "CUST_" + hashed_id

    # Replace the original customer IDs
    df["Customer ID"] = df["Customer ID"].apply(create_pseudonym)

    return df



# if __name__ == "__main__":

#     # Create a small synthetic test dataset
#     sample_data = pd.DataFrame({
#         "Customer ID": [13085, 17850, 13085, None],
#         "Quantity": [12, 6, 4, 2]
#     })

#     # Generate a temporary key for this test only
#     test_key = os.urandom(32).hex()

#     protected_df = pseudonymize_customer_ids(
#         sample_data,
#         test_key
#     )

#     print("\n--- ORIGINAL DATA ---")
#     print(sample_data.to_string(index=False))

#     print("\n--- PSEUDONYMIZED DATA ---")
#     print(protected_df.to_string(index=False))

#     # Verify repeated customer IDs stay consistent
#     assert protected_df.loc[0, "Customer ID"] == protected_df.loc[2, "Customer ID"]

#     # Verify missing IDs remain missing
#     assert pd.isna(protected_df.loc[3, "Customer ID"])

#     print("\nPrivacy checks passed!")


def detect_pii_columns(df):
    """Identify columns that may contain personal information."""

    pii_keywords = {
        "name": "Name",
        "email": "Email Address",
        "phone": "Phone Number",
        "address": "Physical Address",
        "customer id": "Customer Identifier"
    }

    detected_columns = {}

    for column in df.columns:
        column_lower = column.lower()

        for keyword, pii_type in pii_keywords.items():
            if keyword in column_lower:
                detected_columns[column] = pii_type
                break

    return detected_columns


def mask_pii(df):
    """Mask personal information in identified columns."""

    df = df.copy()

    # Identify columns containing potential PII
    pii_columns = detect_pii_columns(df)

    for column, pii_type in pii_columns.items():

        if pii_type == "Email Address":
            df[column] = df[column].apply(
                lambda value: "[REDACTED_EMAIL]"
                if pd.notna(value) else value
            )

        elif pii_type == "Phone Number":
            df[column] = df[column].apply(
                lambda value: "[REDACTED_PHONE]"
                if pd.notna(value) else value
            )

        elif pii_type == "Name":
            df[column] = df[column].apply(
                lambda value: "[REDACTED_NAME]"
                if pd.notna(value) else value
            )

        elif pii_type == "Physical Address":
            df[column] = df[column].apply(
                lambda value: "[REDACTED_ADDRESS]"
                if pd.notna(value) else value
            )

        elif pii_type == "Customer Identifier":
            df[column] = df[column].apply(
                lambda value: "[REDACTED_ID]"
                if pd.notna(value) else value
            )

    return df


    
if __name__ == "__main__":

    from pathlib import Path
    from dotenv import load_dotenv

    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "online_retail_II.xlsx"

    # Load environment variables from .env
    load_dotenv(BASE_DIR / ".env")

    secret_key = os.getenv("PSEUDONYMIZATION_KEY")

    if not secret_key:
        raise ValueError("PSEUDONYMIZATION_KEY is missing.")

    # Load complete dataset
    print("Loading complete dataset...")

    sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    df = pd.concat(sheets.values(), ignore_index=True)

    # Apply pseudonymization
    protected_df = pseudonymize_customer_ids(df, secret_key)

    print("\n--- PRIVACY AUDIT ---")
    print("Records processed:", len(protected_df))

    print(
        "Missing customer IDs:",
        protected_df["Customer ID"].isna().sum()
    )

    print(
        "Unique pseudonymized customer IDs:",
        protected_df["Customer ID"].nunique()
    )

    # Verify missing values are preserved
    assert (
        df["Customer ID"].isna().sum()
        == protected_df["Customer ID"].isna().sum()
    )

    # Verify quantities are unchanged
    assert df["Quantity"].equals(protected_df["Quantity"])

    # Verify original customer identifiers were replaced
    assert not protected_df["Customer ID"].dropna().astype(str).str.fullmatch(
        r"\d+(\.0)?"
    ).any()

    print("\nFull-dataset privacy checks passed!")


    
    # Test PII column detection using synthetic data
    print("\n--- PII DETECTION TEST ---")

    sample_data = pd.DataFrame({
        "Customer ID": [1001, 1002],
        "Full Name": ["Sarah Johnson", "Michael Brown"],
        "Email": ["sarah@example.com", "michael@example.com"],
        "Phone Number": ["514-555-0101", "514-555-0102"],
        "Purchase Amount": [150, 275]
    })

    detected_pii = detect_pii_columns(sample_data)

    for column, pii_type in detected_pii.items():
        print(f"{column}: {pii_type}")


    
    # Test PII masking
    print("\n--- PII MASKING TEST ---")

    masked_data = mask_pii(sample_data)

    print(masked_data.to_string(index=False))

    # Verify original email addresses were removed
    assert not masked_data["Email"].astype(str).str.contains("@").any()

    # Verify transaction amounts are preserved
    assert masked_data["Purchase Amount"].equals(
        sample_data["Purchase Amount"]
    )

    print("\nPII masking checks passed!")




