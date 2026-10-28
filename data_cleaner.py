
import re
import pandas as pd


def normalize_column_name(column):
    return str(column).strip().lower().replace(" ", "_")


def find_column(df, target):
    target = normalize_column_name(target)
    for column in df.columns:
        if normalize_column_name(column) == target:
            return column
    return None


def prepare_data(df):
    prepared = df.copy()

    for column in prepared.select_dtypes(include=["object", "string"]).columns:
        prepared[column] = prepared[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        prepared[column] = prepared[column].replace("", pd.NA)

    return prepared


def analyze_data(df):
    prepared = prepare_data(df)

    email_column = find_column(prepared, "email")
    age_column = find_column(prepared, "age")

    missing_by_column = prepared.isna().sum()
    duplicate_indexes = prepared.index[
        prepared.duplicated(keep="first")
    ].tolist()

    invalid_email_indexes = []
    if email_column is not None:
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        for index, value in prepared[email_column].items():
            if pd.notna(value) and not re.match(pattern, str(value)):
                invalid_email_indexes.append(index)

    suspicious_age_indexes = []
    if age_column is not None:
        ages = pd.to_numeric(prepared[age_column], errors="coerce")
        suspicious_age_indexes = ages.index[
            ages.notna() & ((ages < 0) | (ages > 120))
        ].tolist()

    report = {
        "total_rows": len(prepared),
        "total_columns": len(prepared.columns),
        "missing_cells": int(missing_by_column.sum()),
        "duplicate_rows": int(prepared.duplicated().sum()),
        "columns_with_missing_values": int(
            prepared.isna().any(axis=0).sum()
        ),
        "invalid_email_count": len(invalid_email_indexes),
        "suspicious_age_count": len(suspicious_age_indexes),
    }

    issues = {
        "missing_by_column": missing_by_column[
            missing_by_column > 0
        ].to_dict(),
        "duplicate_row_indexes": duplicate_indexes,
        "invalid_email_indexes": invalid_email_indexes,
        "suspicious_age_indexes": suspicious_age_indexes,
    }

    return report, issues


def clean_data(
    df,
    remove_duplicates=False,
    trim_whitespace=True,
    standardize_columns=True,
    standardize_emails=True,
    missing_strategy="Leave missing values blank",
    text_fill_value="Unknown",
    invalid_email_action="Keep and flag",
    invalid_age_action="Keep and flag",
):
    cleaned = df.copy()

    if standardize_columns:
        cleaned.columns = [
            normalize_column_name(column)
            for column in cleaned.columns
        ]

    if trim_whitespace:
        for column in cleaned.select_dtypes(
            include=["object", "string"]
        ).columns:
            cleaned[column] = cleaned[column].map(
                lambda value: value.strip()
                if isinstance(value, str)
                else value
            )

    for column in cleaned.select_dtypes(
        include=["object", "string"]
    ).columns:
        cleaned[column] = cleaned[column].replace("", pd.NA)

    email_column = find_column(cleaned, "email")
    age_column = find_column(cleaned, "age")

    if standardize_emails and email_column is not None:
        cleaned[email_column] = cleaned[email_column].map(
            lambda value: value.lower()
            if isinstance(value, str)
            else value
        )

    if remove_duplicates:
        cleaned = cleaned.drop_duplicates().copy()

    # Handle missing values using the selected strategy.
    if missing_strategy == "Fill text with Unknown and numbers with median":
        for column in cleaned.columns:
            if pd.api.types.is_numeric_dtype(cleaned[column]):
                if cleaned[column].notna().any():
                    cleaned[column] = cleaned[column].fillna(
                        cleaned[column].median()
                    )
            else:
                cleaned[column] = cleaned[column].fillna(text_fill_value)

    elif missing_strategy == "Fill numeric columns with median":
        for column in cleaned.select_dtypes(
            include="number"
        ).columns:
            if cleaned[column].notna().any():
                cleaned[column] = cleaned[column].fillna(
                    cleaned[column].median()
                )

    elif missing_strategy == "Fill numeric columns with mean":
        for column in cleaned.select_dtypes(
            include="number"
        ).columns:
            if cleaned[column].notna().any():
                cleaned[column] = cleaned[column].fillna(
                    cleaned[column].mean()
                )

    elif missing_strategy == "Remove rows with missing values":
        cleaned = cleaned.dropna().copy()

    # Correct or remove invalid email records.
    if email_column is not None and email_column in cleaned.columns:
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        invalid_emails = cleaned[email_column].notna() & ~cleaned[
            email_column
        ].astype(str).str.match(email_pattern)

        if invalid_email_action == "Replace invalid emails with blank":
            cleaned.loc[invalid_emails, email_column] = pd.NA
        elif invalid_email_action == "Remove rows with invalid emails":
            cleaned = cleaned.loc[~invalid_emails].copy()

    # Correct or remove suspicious ages.
    if age_column is not None and age_column in cleaned.columns:
        numeric_ages = pd.to_numeric(
            cleaned[age_column], errors="coerce"
        )
        invalid_ages = numeric_ages.notna() & (
            (numeric_ages < 0) | (numeric_ages > 120)
        )

        if invalid_age_action == "Replace suspicious ages with blank":
            cleaned.loc[invalid_ages, age_column] = pd.NA
        elif invalid_age_action == "Remove rows with suspicious ages":
            cleaned = cleaned.loc[~invalid_ages].copy()

    return cleaned.reset_index(drop=True)

def profile_columns(df):
    """Summarize every column without requiring preset column names."""
    profiles = []

    for column in df.columns:
        series = df[column]
        non_missing = series.dropna()

        detected_type = "Text"

        if non_missing.empty:
            detected_type = "Empty"
        elif pd.api.types.is_bool_dtype(series):
            detected_type = "Boolean"
        elif pd.api.types.is_numeric_dtype(series):
            detected_type = "Numeric"
        else:
            values = non_missing.astype(str).str.strip()

            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

            if values.str.match(email_pattern).all():
                detected_type = "Email"
            elif pd.to_datetime(
                values, errors="coerce"
            ).notna().mean() >= 0.8:
                detected_type = "Date"
            elif pd.to_numeric(
                values, errors="coerce"
            ).notna().mean() >= 0.8:
                detected_type = "Numeric-like"

        examples = ", ".join(
            non_missing.astype(str).head(3).tolist()
        )

        profiles.append({
            "Column": str(column),
            "Detected Type": detected_type,
            "Missing Values": int(series.isna().sum()),
            "Unique Values": int(series.nunique()),
            "Example Values": examples,
        })

    return pd.DataFrame(profiles)

def validate_column(
    df,
    column,
    rules,
    min_value=None,
    max_value=None,
):
    """Flag data-quality issues without deleting or changing rows."""
    findings = []
    values = df[column]

    def add_findings(mask, rule_name, explanation):
        for index in df.index[mask.fillna(False)]:
            findings.append({
                "CSV Row": index + 2,
                "Column": str(column),
                "Value": str(values.loc[index]),
                "Issue": rule_name,
                "Details": explanation,
            })

    for rule in rules:
        if rule == "Flag missing values":
            mask = values.isna() | values.astype("string").str.strip().eq("")
            add_findings(
                mask,
                rule,
                "This cell has no value.",
            )

        elif rule == "Check email format":
            email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            text = values.astype("string").str.strip()
            mask = (
                values.notna()
                & ~text.str.match(email_pattern, na=False)
            )
            add_findings(
                mask,
                rule,
                "The value does not match a basic email format.",
            )

        elif rule == "Check numeric values":
            numeric = pd.to_numeric(values, errors="coerce")
            mask = values.notna() & numeric.isna()
            add_findings(
                mask,
                rule,
                "The value cannot be interpreted as a number.",
            )

        elif rule == "Flag negative numbers":
            numeric = pd.to_numeric(values, errors="coerce")
            mask = numeric.notna() & numeric.lt(0)
            add_findings(
                mask,
                rule,
                "The number is below zero.",
            )

        elif rule == "Flag zero or negative numbers":
            numeric = pd.to_numeric(values, errors="coerce")
            mask = numeric.notna() & numeric.le(0)
            add_findings(
                mask,
                rule,
                "The number is zero or below zero.",
            )

        elif rule == "Check date values":
            parsed = pd.to_datetime(values, errors="coerce")
            mask = values.notna() & parsed.isna()
            add_findings(
                mask,
                rule,
                "The value could not be interpreted as a date.",
            )

        elif rule == "Flag duplicate values":
            mask = values.notna() & values.duplicated(keep=False)
            add_findings(
                mask,
                rule,
                "This value appears more than once in the column.",
            )

        elif rule == "Check numeric range":
            numeric = pd.to_numeric(values, errors="coerce")
            mask = numeric.notna() & (
                numeric.lt(min_value) | numeric.gt(max_value)
            )
            add_findings(
                mask,
                rule,
                f"The value is outside {min_value} to {max_value}.",
            )

    return pd.DataFrame(
        findings,
        columns=[
            "CSV Row",
            "Column",
            "Value",
            "Issue",
            "Details",
        ],
    )
