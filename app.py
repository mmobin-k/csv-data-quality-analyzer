
import pandas as pd
import streamlit as st

from data_cleaner import (
    analyze_data,
    clean_data,
    profile_columns,
    validate_column,
)



st.set_page_config(
    page_title="CleanSheet | Data Quality Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("CleanSheet: CSV Data Quality Analyzer")
st.write(
    "Upload a CSV file to detect data quality issues, choose corrections, "
    "preview the results, and download your cleaned dataset."
)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV file to begin.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.warning("This CSV contains no data rows.")
        st.stop()

    if len(df.columns) == 0:
        st.error("No columns were found.")
        st.stop()

    report, issues = analyze_data(df)

    
    st.subheader("Automatic Column Analysis")

    column_profile = profile_columns(df)

    st.dataframe(
    column_profile,
    use_container_width=True,
    hide_index=True,
)

    st.caption(
    "Column types are automatically estimated from the uploaded data. "
    "Review the results before applying type-specific corrections."
)


    st.subheader("1. Original Dataset")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("2. Original Data Quality Report")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", report["total_rows"])
    col2.metric("Columns", report["total_columns"])
    col3.metric("Missing Cells", report["missing_cells"])
    col4.metric("Duplicate Rows", report["duplicate_rows"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Invalid Emails", report["invalid_email_count"])
    col2.metric("Suspicious Ages", report["suspicious_age_count"])
    col3.metric(
        "Columns With Missing Values",
        report["columns_with_missing_values"],
    )

    with st.expander("View detailed findings"):
        if issues["missing_by_column"]:
            st.write("Missing values by column")
            missing_df = pd.DataFrame(
                list(issues["missing_by_column"].items()),
                columns=["Column", "Missing Values"],
            )
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.write("No missing values detected.")

        if issues["duplicate_row_indexes"]:
            st.write("Duplicate rows (original row indexes)")
            st.dataframe(
                df.loc[issues["duplicate_row_indexes"]],
                use_container_width=True,
            )

        if issues["invalid_email_indexes"]:
            st.write("Rows with invalid email formats")
            st.dataframe(
                df.loc[issues["invalid_email_indexes"]],
                use_container_width=True,
            )

        if issues["suspicious_age_indexes"]:
            st.write("Rows with suspicious ages")
            st.dataframe(
                df.loc[issues["suspicious_age_indexes"]],
                use_container_width=True,
            )

    st.subheader("3. Choose Cleaning Options")

    remove_duplicates = st.checkbox(
        "Remove exact duplicate rows",
        value=False,
    )
    trim_whitespace = st.checkbox(
        "Remove leading and trailing whitespace",
        value=True,
    )
    standardize_columns = st.checkbox(
        "Standardize column names",
        value=True,
    )
    standardize_emails = st.checkbox(
        "Convert email addresses to lowercase",
        value=True,
    )

    missing_strategy = st.selectbox(
        "How should missing values be handled?",
        [
            "Leave missing values blank",
            "Fill text with Unknown and numbers with median",
            "Fill numeric columns with median",
            "Fill numeric columns with mean",
        ],
        help=(
            "Mean and median apply to numeric columns. "
            "Choose a strategy that makes sense for your dataset."
        ),
    )

    text_fill_value = st.text_input(
        "Replacement for missing text values",
        value="Unknown",
        help="Used by the option that fills text and numeric columns.",
    )

    invalid_email_action = st.selectbox(
        "What should happen to invalid email addresses?",
        [
            "Keep and flag",
            "Replace invalid emails with blank",
            
        ],
    )

    invalid_age_action = st.selectbox(
        "What should happen to suspicious ages?",
        [
            "Keep and flag",
            "Replace suspicious ages with blank",
            
        ],
        help="Ages below 0 or above 120 are flagged by this demo.",
    )

    cleaned_df = clean_data(
        df,
        remove_duplicates=remove_duplicates,
        trim_whitespace=trim_whitespace,
        standardize_columns=standardize_columns,
        standardize_emails=standardize_emails,
        missing_strategy=missing_strategy,
        text_fill_value=text_fill_value,
        invalid_email_action=invalid_email_action,
        invalid_age_action=invalid_age_action,
    )

    cleaned_report, cleaned_issues = analyze_data(cleaned_df)

    st.subheader("4. Cleaned Dataset Preview")
    st.dataframe(cleaned_df.head(100), use_container_width=True)


    
    st.subheader("5. Custom Validation Rules")

    st.write(
        "Choose a column and the checks you want to run. "
        "Issues are flagged for review; no rows are removed or changed."
    )

    selected_column = st.selectbox(
        "Choose a column to validate",
        options=list(df.columns),
    )

    available_rules = [
        "Flag missing values",
        "Check email format",
        "Check numeric values",
        "Flag negative numbers",
        "Flag zero or negative numbers",
        "Check date values",
        "Flag duplicate values",
        "Check numeric range",
    ]

    selected_rules = st.multiselect(
        "Choose validation rules",
        options=available_rules,
        default=["Flag missing values"],
    )

    min_value = 0.0
    max_value = 100.0

    if "Check numeric range" in selected_rules:
        range_col1, range_col2 = st.columns(2)

        min_value = range_col1.number_input(
            "Minimum allowed value",
            value=0.0,
        )
        max_value = range_col2.number_input(
            "Maximum allowed value",
            value=100.0,
        )

    if (
        "Check numeric range" in selected_rules
        and min_value > max_value
    ):
        st.error("The minimum must not exceed the maximum.")
        validation_results = pd.DataFrame()
    elif selected_rules:
        validation_results = validate_column(
            df,
            selected_column,
            selected_rules,
            min_value=min_value,
            max_value=max_value,
        )
    else:
        validation_results = pd.DataFrame()

    if not selected_rules:
        st.info("Choose at least one validation rule.")
    elif (
        "Check numeric range" in selected_rules
        and min_value > max_value
    ):
        pass
    elif validation_results.empty:
        st.success("No issues were found for the selected rules.")
    else:
        st.warning(
            f"Found {len(validation_results)} potential issue(s). "
            "Review these values before deciding what to do."
        )
        st.dataframe(
            validation_results,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Validation Findings",
            data=validation_results.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="validation_findings.csv",
            mime="text/csv",
        )

    st.subheader("6. Before and After")

    comparison = pd.DataFrame(
        [
            {
                "Metric": "Rows",
                "Before": report["total_rows"],
                "After": len(cleaned_df),
            },
            {
                "Metric": "Missing Cells",
                "Before": report["missing_cells"],
                "After": cleaned_report["missing_cells"],
            },
            {
                "Metric": "Duplicate Rows",
                "Before": report["duplicate_rows"],
                "After": cleaned_report["duplicate_rows"],
            },
            {
                "Metric": "Invalid Emails",
                "Before": report["invalid_email_count"],
                "After": cleaned_report["invalid_email_count"],
            },
            {
                "Metric": "Suspicious Ages",
                "Before": report["suspicious_age_count"],
                "After": cleaned_report["suspicious_age_count"],
            },
        ]
    )

    st.dataframe(comparison, use_container_width=True)

    st.caption(
        "Review the output carefully. Replacing an invalid value with blank "
        "does not recover the correct value, and removing rows reduces the dataset."
    )

    st.subheader("6. Download Results")

    st.download_button(
        "Download Cleaned CSV",
        data=cleaned_df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )

    quality_report = comparison.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Before-and-After Quality Report",
        data=quality_report,
        file_name="data_quality_report.csv",
        mime="text/csv",
    )

except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
    st.error(
        "The file could not be processed. Check that it is a valid CSV "
        "with consistent columns and values."
    )
    st.caption(str(error))
