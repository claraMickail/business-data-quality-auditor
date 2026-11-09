# Business Data Quality & Privacy Auditor

A Python-based data quality auditing tool designed to review large-scale business datasets, identify inconsistencies and anomalies, protect sensitive customer information, and generate structured quality assurance reports.

## Project Overview

Accurate, consistent, and privacy-conscious data is essential for reliable business analysis and AI applications.

This project implements an automated auditing workflow using Python and Pandas to assess the quality of over **1 million retail transaction records** from the UCI Online Retail II dataset.

The system identifies potential data quality issues, investigates unusual transactions using business-specific rules, and applies PII detection, masking, and customer identifier pseudonymization.

Rather than automatically removing suspicious records, the workflow flags them for further review to distinguish potential errors from legitimate business activities.

## Key Features

### 1. Data Quality Validation

Automated checks identify:

- Missing customer IDs and product descriptions
- Exact duplicate transaction records
- Negative and zero transaction quantities
- Negative and zero prices
- Unexpected negative quantities
- Cancellation invoices with inconsistent quantity values

### 2. Context-Aware Anomaly Detection

Applies business-specific rules to distinguish potentially legitimate transactions from anomalies requiring investigation.

For example:

- Identifies cancellation invoices using the documented `C` prefix.
- Flags negative quantities without cancellation indicators.
- Recognizes bad-debt adjustments based on transaction descriptions and stock codes.
- Preserves unusual records for investigation rather than automatically deleting them.

### 3. PII Detection and Privacy Protection

Includes privacy-focused functionality to:

- Identify potentially sensitive columns, including customer IDs, names, emails, phone numbers, and addresses.
- Pseudonymize customer identifiers using keyed HMAC-SHA256 hashing.
- Preserve consistent pseudonyms across transactions from the same customer.
- Redact sensitive values in identified columns.
- Preserve missing values and non-sensitive transaction information.

PII column detection is based on column names, and email, phone number, name, and address masking is demonstrated using synthetic test data.

**Privacy limitation:** Pseudonymization does not guarantee anonymity, and the current PII detection functionality does not identify sensitive information embedded in arbitrary text fields.

### 4. Automated Quality Assurance Reporting

Generates a structured JSON report containing:

- Total records analyzed
- Records requiring further review
- Individual data quality issue counts
- Overall review rate
- Informational counts for cancellations and accounting adjustments

### 5. Automated Testing

Uses pytest to verify missing-value detection, duplicate identification, transaction classification, pseudonymization, and PII masking.

All **5 automated tests passed** in the current implementation.

## Audit Results

The completed audit of the Online Retail II dataset produced the following findings:

| Metric | Result |
|---|---:|
| Total records analyzed | 1,067,371 |
| Records requiring review | 269,556 |
| Review rate | 25.25% |
| Missing customer IDs | 243,007 |
| Missing product descriptions | 4,382 |
| Exact duplicate rows | 34,335 |
| Negative quantities without cancellation prefix | 3,457 |
| Zero-price transactions | 6,202 |
| Cancellation quantity mismatches | 1 |
| Unexplained negative prices | 0 |

**Important:** These categories overlap. Records requiring review are not necessarily confirmed errors.

### Key Findings

**Missing customer information:** Approximately 22.8% of records lack customer identifiers, potentially limiting customer-level analysis.

**Duplicate records:** 34,335 exact duplicate rows were detected. These require contextual review before removal because identical invoice line items may represent legitimate transactions.

**Unusual quantities:** All 3,457 negative-quantity records without cancellation indicators also have zero prices, suggesting possible inventory adjustments or other non-sales activity requiring further investigation.

**Accounting adjustments:** Six records were identified as bad-debt adjustments, including five negative-price entries and one positive-price entry. These should be distinguished from ordinary product sales.

**Cancellation inconsistency:** One cancellation invoice contained a positive quantity and was flagged for manual review.

## Recommendations

Based on the audit findings:

1. Investigate missing customer identifiers and determine whether those records remain suitable for transaction-level analysis.
2. Review exact duplicates before deciding whether to retain or remove them.
3. Distinguish sales, cancellations, accounting adjustments, and potential inventory movements when calculating business metrics.
4. Establish documented validation rules and exception-handling procedures.
5. Apply data minimization and pseudonymization where customer-level identifiers are not required.

## Technologies Used

- **Python:** Data processing and audit automation
- **Pandas:** Dataset analysis and validation
- **NumPy:** Numerical processing
- **OpenPyXL:** Excel data loading
- **HMAC-SHA256:** Customer identifier pseudonymization
- **python-dotenv:** Local secret-key configuration
- **pytest:** Automated testing
- **JSON:** Structured audit reporting

## Project Structure

```text
business-data-quality-auditor/
├── data/
│   └── online_retail_II.xlsx
├── src/
│   ├── load_data.py
│   ├── validate_data.py
│   ├── privacy_audit.py
│   └── generate_report.py
├── tests/
│   └── test_validation.py
├── reports/
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Usage

Clone the repository:

```bash
git clone https://github.com/claraMickail/business-data-quality-auditor.git
cd business-data-quality-auditor
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Run Data Validation

```powershell
python src/validate_data.py
```

### Generate Quality Assurance Report

```powershell
python src/generate_report.py
```

The output is saved locally to:

```text
reports/quality_report.json
```

### Run Privacy Audit

Create a `.env` file containing a locally generated secret key:

```text
PSEUDONYMIZATION_KEY=your_secret_key_here
```

Generate a secure random key with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Then run:

```powershell
python src/privacy_audit.py
```

**Never commit the `.env` file or disclose the secret key.**

### Run Automated Tests

```powershell
python -m pytest tests/test_validation.py -v
```

## Dataset

This project uses the [Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) from the UCI Machine Learning Repository, containing 1,067,371 retail transaction records.

The original dataset is not included in this repository to minimize unnecessary redistribution of customer identifiers.

To reproduce the analysis, download `online_retail_II.xlsx` from UCI and place it in the `data/` folder.

Citation: Chen, D. (2012). Online Retail II. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

License: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Limitations

- Flagged records are not necessarily erroneous and may require business-context verification.
- Duplicate detection identifies identical rows but cannot establish whether they represent accidental duplicates.
- The current PII detection method relies on column names and may miss sensitive information in unstructured text.
- Pseudonymization reduces direct identifier exposure but does not guarantee anonymity.
- The workflow demonstrates data quality assurance practices but does not establish compliance with a particular privacy regulation.

## Project Purpose

This project demonstrates practical experience in large-scale business data review, data quality validation, anomaly investigation, privacy-conscious processing, automated testing, and structured reporting.

It is intended as a portfolio project showcasing reproducible and responsible data analysis workflows.
