# 🧹 Automated CSV Data Cleaner

A web app built with **Python, Pandas and Streamlit** that cleans messy CSV files automatically. Upload a CSV, review the before/after comparison, and download the cleaned file in one click.

🔗 **Live Demo:** [https://lahari-csv-cleaner.streamlit.app](https://python-csv-data-cleaner-knmpxrpxjyfcjkth3fp2u2.streamlit.app/)

## Features

- Auto-detects file encoding and delimiter
- Standardizes column names (lowercase, underscores)
- Trims whitespace and converts placeholders (`N/A`, `null`, `-`, `?`) to missing values
- Removes fully empty rows and columns
- Drops columns with too many missing values (adjustable threshold)
- Converts text like `$1,200` or `45%` to numbers, and date-like columns to datetime
- Removes duplicate rows
- Handles missing values: fill with median/mean/mode, drop rows, or leave as is
- Optional outlier removal using the IQR method
- Cleaning report showing rows, columns, missing values and duplicates before and after
- Download the cleaned data as a CSV

## Tech Stack

- Python
- Pandas
- NumPy
- Streamlit

## Installation

```bash
git clone https://github.com/laharisetty29/python-csv-data-cleaner.git
cd python-csv-data-cleaner
pip install -r requirements.txt
```

## Run the App

```bash
python -m streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## How to Use

1. Upload a CSV file using the **Browse files** button.
2. Choose cleaning options in the left sidebar.
3. Review the original and cleaned data and the cleaning report.
4. Click **Download Cleaned CSV**.

## Project Structure

```
python-csv-data-cleaner/
├── app.py
├── requirements.txt
└── README.md
```

## Future Improvements

- Excel (`.xlsx`) file support
- Missing-values chart per column
- Downloadable cleaning report
- Column-level cleaning controls

## Author

**Lahari**
GitHub: [laharisetty29](https://github.com/laharisetty29)
LinkedIn: [linkedin.com/in/laharigadamsetty](https://linkedin.com/in/laharigadamsetty)
