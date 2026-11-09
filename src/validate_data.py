import pandas as pd

def check_missing_values(df):
    """Flag missing customer IDs and descriptions."""

    df = df.copy()

    df["missing_customer_id"] = df["Customer ID"].isna()
    df["missing_description"] = df["Description"].isna()

    return df


def check_duplicates(df):
    """Flag exact duplicate transaction records."""

    df = df.copy()

    # Compare the original transaction columns
    original_columns = [
        "Invoice", "StockCode", "Description",
        "Quantity", "InvoiceDate", "Price",
        "Customer ID", "Country"
    ]

    df["is_duplicate"] = df.duplicated(
        subset=original_columns,
        keep="first"
    )

    return df


def check_transaction_values(df):
    """Flag unusual transaction values and identify cancellations."""

    df = df.copy()

    # Identify cancelled invoices (invoice numbers starting with C)
    df["is_cancellation"] = (
        df["Invoice"].astype(str).str.upper().str.startswith("C")
    )

    # Identify unusual quantities
    df["negative_quantity"] = df["Quantity"] < 0
    df["zero_quantity"] = df["Quantity"] == 0

    # Identify unusual prices
    df["negative_price"] = df["Price"] < 0
    df["zero_price"] = df["Price"] == 0

    # Flag negative quantities without a cancellation invoice
    df["unexpected_negative_quantity"] = (
        df["negative_quantity"] & ~df["is_cancellation"]
    )

    # Flag cancellations with positive quantities
    df["cancellation_quantity_mismatch"] = (
        df["is_cancellation"] & (df["Quantity"] > 0)
    )

    # Identify known bad-debt accounting adjustments
    df["is_bad_debt_adjustment"] = (
        df["StockCode"].astype(str).str.upper().eq("B")
        & df["Description"].fillna("").str.contains(
            "Adjust bad debt", case=False, regex=False
        )
    )

    # Flag negative prices that are not identified bad-debt adjustments
    df["unexplained_negative_price"] = (
        df["negative_price"] & ~df["is_bad_debt_adjustment"]
    )

    return df




# # Initial test for validation function
# if __name__ == "__main__":

#     sample_data = pd.DataFrame({
#         "Customer ID": [13085, None, 17850],
#         "Description": ["Christmas Lights", "White Lantern", None]
#     })

#     result = check_missing_values(sample_data)

#     print(result)


if __name__ == "__main__":

    from pathlib import Path

    # Locate our Excel dataset
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_PATH = BASE_DIR / "data" / "online_retail_II.xlsx"

    # Load both sheets and combine them
    print("Loading dataset...")

    all_sheets = pd.read_excel(DATA_PATH, sheet_name=None)
    df = pd.concat(all_sheets.values(), ignore_index=True)

    # Apply our missing-value validation function
    validated_df = check_missing_values(df)

    validated_df = check_duplicates(validated_df)
    validated_df = check_transaction_values(validated_df)

    # Summarize the flagged records
    print("\n--- MISSING VALUE VALIDATION ---")
    print("Total records:", len(validated_df))

    print("Missing Customer IDs:",
          validated_df["missing_customer_id"].sum())

    print("Missing Descriptions:",
          validated_df["missing_description"].sum())

    # Count rows with at least one missing field
    flagged_rows = (
        validated_df["missing_customer_id"]
        | validated_df["missing_description"]
    )

    print("Records flagged:", flagged_rows.sum())

    # Summarize duplicate records
    print("\n--- DUPLICATE VALIDATION ---")

    print("Exact duplicate rows:",
        validated_df["is_duplicate"].sum())

    print("\nSample duplicate records:")
    print(
        validated_df.loc[
            validated_df["is_duplicate"],
            ["Invoice", "StockCode", "Quantity", "Price"]
        ].head(5).to_string(index=False)
    )

    
    # Summarize transaction value validation
    print("\n--- TRANSACTION VALUE VALIDATION ---")

    checks = [
        "is_cancellation",
        "negative_quantity",
        "zero_quantity",
        "negative_price",
        "zero_price",
        "unexpected_negative_quantity",
        "cancellation_quantity_mismatch",
        "is_bad_debt_adjustment",
        "unexplained_negative_price"
    ]

    for check in checks:
        print(f"{check}: {validated_df[check].sum()}")

    # Show examples requiring further investigation
    print("\nSample suspicious transactions:")

    suspicious = (
        validated_df["unexpected_negative_quantity"]
        | validated_df["unexplained_negative_price"]
        | validated_df["cancellation_quantity_mismatch"]
    )

    print(
        validated_df.loc[
            suspicious,
            ["Invoice", "StockCode", "Quantity", "Price",
             "is_cancellation", "unexpected_negative_quantity",
             "negative_price", "cancellation_quantity_mismatch"]
        ].head(10).to_string(index=False)
    )

    
    # Investigate relationships between unusual values
    print("\n--- ANOMALY INVESTIGATION ---")

    print(
        "Negative quantities with zero prices:",
        (validated_df["negative_quantity"]
         & validated_df["zero_price"]).sum()
    )

    print(
        "Unexpected negative quantities with zero prices:",
        (validated_df["unexpected_negative_quantity"]
         & validated_df["zero_price"]).sum()
    )

    # Inspect all negative-price records
    print("\nNegative-price transactions:")
    print(
        validated_df.loc[
            validated_df["negative_price"],
            ["Invoice", "StockCode", "Description",
             "Quantity", "Price", "Customer ID"]
        ].to_string(index=False)
    )

    # Inspect cancellation quantity mismatches
    print("\nCancellation quantity mismatches:")
    print(
        validated_df.loc[
            validated_df["cancellation_quantity_mismatch"],
            ["Invoice", "StockCode", "Description",
             "Quantity", "Price", "Customer ID"]
        ].to_string(index=False)
    )

    print("\n--- REFINED CLASSIFICATION ---")

    print("Bad-debt adjustments:",
          validated_df["is_bad_debt_adjustment"].sum())

    print("Unexplained negative prices:",
          validated_df["unexplained_negative_price"].sum())


    print("\n--- BAD DEBT INVESTIGATION ---")

    print(
        validated_df.loc[
            validated_df["is_bad_debt_adjustment"],
            ["Invoice", "StockCode", "Description", "Quantity", "Price"]
        ].to_string(index=False)
    )



