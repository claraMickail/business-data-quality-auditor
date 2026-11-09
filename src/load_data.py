
from pathlib import Path
import pandas as pd

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset location
DATA_PATH = BASE_DIR / "data" / "online_retail_II.xlsx"

# Inspect available sheets
excel_file = pd.ExcelFile(DATA_PATH)
print("Available sheets:", excel_file.sheet_names)

# Load a small sample from each sheet
for sheet in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet, nrows=1000)

    print(f"\n--- {sheet} ---")
    print("Sample shape:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five rows:")
    print(df.head())

    print("\nMissing values in sample:")
    print(df.isnull().sum())

    
# Load the complete dataset from both sheets
print("\nLoading complete dataset...")

all_sheets = pd.read_excel(DATA_PATH, sheet_name=None)

df = pd.concat(all_sheets.values(), ignore_index=True)

print("\n--- COMPLETE DATASET SUMMARY ---")

# Total rows and columns
print("Dataset shape:", df.shape)

# Check missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Check duplicate rows
print("\nExact duplicate rows:")
print(df.duplicated().sum())

# Check unusual numerical values
print("\nQuantity statistics:")
print(df["Quantity"].describe())

print("\nPrice statistics:")
print(df["Price"].describe())

# Check data types
print("\nData types:")
print(df.dtypes)