import pandas as pd
import streamlit as st

from data_cleaner import analyze_data, clean_data


st.set_page_config(
    page_title="CleanSheet | Data Quality Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("CleanSheet: CSV Data Quality Analyzer")

st.write(
    "Upload a CSV file to identify data quality issues, "
    "review the findings, and download a cleaned dataset."
)

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"],
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.warning(
                "This CSV file contains no data rows."
            )
            st.stop()

        if len(df.columns) == 0:
            st.error(
                "No columns were found in this file."
            )
            st.stop()

        st.subheader("Original Dataset")

        st.dataframe(
            df.head(100),
            use_container_width=True,
        )

        report, issues = analyze_data(df)

        st.subheader("Data Quality Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Rows",
            report["total_rows"],
        )

        col2.metric(
            "Total Columns",
            report["total_columns"],
        )

        col3.metric(
            "Missing Cells",
            report["missing_cells"],
        )

        col4.metric(
            "Duplicate Rows",
            report["duplicate_rows"],
        )

        st.subheader("Detailed Findings")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Invalid Emails",
            report["invalid_email_count"],
        )

        col2.metric(
            "Suspicious Ages",
            report["suspicious_age_count"],
        )

        col3.metric(
            "Columns With Missing Values",
            report["columns_with_missing_values"],
        )

        if issues["missing_by_column"]:
            st.write("Missing values by column")

            missing_df = pd.DataFrame(
                list(issues["missing_by_column"].items()),
                columns=["Column", "Missing Values"],
            )

            st.dataframe(
                missing_df,
                use_container_width=True,
            )

        if issues["duplicate_row_indexes"]:
            st.write("Potential duplicate rows")

            duplicate_df = df.loc[
                issues["duplicate_row_indexes"]
            ]

            st.dataframe(
                duplicate_df,
                use_container_width=True,
            )

        if issues["invalid_email_indexes"]:
            st.write("Rows with invalid email formats")

            email_df = df.loc[
                issues["invalid_email_indexes"]
            ]

            st.dataframe(
                email_df,
                use_container_width=True,
            )

        if issues["suspicious_age_indexes"]:
            st.write("Rows with suspicious ages")

            age_df = df.loc[
                issues["suspicious_age_indexes"]
            ]

            st.dataframe(
                age_df,
                use_container_width=True,
            )

        st.subheader("Clean Your Dataset")

        remove_duplicates = st.checkbox(
            "Remove exact duplicate rows",
            value=True,
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

        cleaned_df = clean_data(
            df,
            remove_duplicates=remove_duplicates,
            trim_whitespace=trim_whitespace,
            standardize_columns=standardize_columns,
            standardize_emails=standardize_emails,
        )

        st.subheader("Cleaned Dataset Preview")

        st.dataframe(
            cleaned_df.head(100),
            use_container_width=True,
        )

        st.write(
            f"Original rows: {len(df)} | "
            f"Cleaned rows: {len(cleaned_df)}"
        )

        csv_data = cleaned_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv",
        )

        report_data = pd.DataFrame(
            [
                {
                    "Metric": "Total Rows",
                    "Value": report["total_rows"],
                },
                {
                    "Metric": "Total Columns",
                    "Value": report["total_columns"],
                },
                {
                    "Metric": "Missing Cells",
                    "Value": report["missing_cells"],
                },
                {
                    "Metric": "Duplicate Rows",
                    "Value": report["duplicate_rows"],
                },
                {
                    "Metric": "Invalid Emails",
                    "Value": report["invalid_email_count"],
                },
                {
                    "Metric": "Suspicious Ages",
                    "Value": report["suspicious_age_count"],
                },
            ]
        )

        st.download_button(
            label="Download Quality Report",
            data=report_data.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="data_quality_report.csv",
            mime="text/csv",
        )

    except (
        pd.errors.ParserError,
        UnicodeDecodeError,
        ValueError,
    ):
        st.error(
            "The file could not be processed. "
            "Please check that it is a valid CSV file."
        )

    except Exception as error:
        st.error(
            "An unexpected error occurred while "
            "processing the file."
        )
        st.exception(error)

else:
    st.info(
        "Upload a CSV file to begin analyzing your data."
    )
