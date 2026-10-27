# CleanSheet: CSV Data Quality Analyzer

CleanSheet is a Python application that helps users identify common data quality issues and prepare cleaner CSV datasets for analysis.

## Project Overview

Poor data quality can affect reporting, analytics, and business decisions. CleanSheet provides a simple interface for inspecting datasets, identifying potential issues, and applying selected cleaning operations.

## Features

- Upload and preview CSV files.
- Detect missing values and duplicate rows.
- Identify potentially invalid email formats.
- Flag suspicious age values.
- Standardize column names and text formatting.
- Convert email addresses to lowercase.
- Download cleaned datasets.
- Export data quality reports.

## Technologies Used

- Python
- pandas
- Streamlit

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/csv-data-quality-analyzer.git
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Navigate to the project directory

```bash
cd csv-data-quality-analyzer
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

### 5. Upload a CSV file

Open the local application in your browser and upload a CSV file to analyze its data quality.

## Sample Dataset

The `sample_data` folder contains synthetic customer records designed to demonstrate missing values, duplicate records, invalid email formats, and suspicious age values.

## Future Improvements

- Support Excel file uploads.
- Allow users to select columns for duplicate detection.
- Add configurable validation rules.
- Provide more detailed data quality reports.
- Add automated tests.
- Improve error handling for malformed and unusually large files.

## Limitations

The email validation feature checks basic formatting only. Suspicious values are flagged for review rather than automatically corrected.

The application is intended as a data preparation aid. Users should review cleaning decisions before using the output for business or analytical purposes.

## Author

Developed as a portfolio project to demonstrate Python programming, data cleaning, data validation, and application development skills.
