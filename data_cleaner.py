import re
import pandas as pd


def analyze_data(df):
    """Analyze a DataFrame and return data quality findings."""

    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns_with_missing_values": int(
            df.isna().any(axis=0).sum()
        ),
    }

    missing_by_column = df.isna().sum()

    email_issues = []
    suspicious_ages = []

    for index, row in df.iterrows():

        if "email" in df.columns:
            email = row["email"]

            if pd.notna(email) and str(email).strip():
                email = str(email).strip()

                pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

                if not re.match(pattern, email):
                    email_issues.append(index)

        if "age" in df.columns:
            age = pd.to_numeric(row["age"], errors="coerce")

            if pd.notna(age) and (age < 0 or age > 120):
                suspicious_ages.append(index)

    report["invalid_email_count"] = len(email_issues)
    report["suspicious_age_count"] = len(suspicious_ages)

    missing_details = missing_by_column[
        missing_by_column > 0
    ].to_dict()

    issues = {
        "missing_by_column": missing_details,
        "duplicate_row_indexes": df.index[
            df.duplicated(keep="first")
        ].tolist(),
        "invalid_email_indexes": email_issues,
        "suspicious_age_indexes": suspicious_ages,
    }

    return report, issues


def clean_data(
    df,
    remove_duplicates=False,
    trim_whitespace=True,
    standardize_columns=True,
    standardize_emails=True,
):
    """Apply selected cleaning operations."""

    cleaned = df.copy()

    if standardize_columns:
        cleaned.columns = [
            str(column).strip().lower().replace(" ", "_")
            for column in cleaned.columns
        ]

    if trim_whitespace:
        for column in cleaned.select_dtypes(
            include=["object", "string"]
        ).columns:
            cleaned[column] = cleaned[column].map(
                lambda value: (
                    value.strip()
                    if isinstance(value, str)
                    else value
                )
            )

    if standardize_emails and "email" in cleaned.columns:
        cleaned["email"] = cleaned["email"].map(
            lambda value: (
                value.lower()
                if isinstance(value, str)
                else value
            )
        )

    if remove_duplicates:
        cleaned = cleaned.drop_duplicates().reset_index(
            drop=True
        )

    return cleaned
