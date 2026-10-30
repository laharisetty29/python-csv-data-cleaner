import io
import warnings

import numpy as np
import pandas as pd
import streamlit as st

# Hide the date-format guessing warning
warnings.filterwarnings("ignore", message="Could not infer format")

st.set_page_config(page_title="Automated CSV Cleaner", layout="wide")
st.title("🧹 Automated CSV Data Cleaner")


# ---------- Helpers ----------
def read_csv_safely(file):
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc, sep=None, engine="python")
        except Exception:
            continue
    raise ValueError("Could not read the file. Check that it is a valid CSV.")


def clean_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def clean_data(df, missing_strategy, remove_outliers, drop_thresh):
    log = {}
    log["rows_before"], log["cols_before"] = df.shape
    log["missing_before"] = int(df.isna().sum().sum())

    df = clean_columns(df.copy())

    # Strip whitespace + convert placeholder text to NaN
    placeholders = ["", "na", "n/a", "nan", "null", "none", "-", "--", "?", "unknown"]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(
            {p: np.nan for p in placeholders + [p.upper() for p in placeholders]}
        )
        df[col] = df[col].replace("nan", np.nan)

    # Drop fully empty rows/columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    # Drop columns with too many missing values
    keep = df.columns[df.isna().mean() <= drop_thresh]
    log["cols_dropped_high_missing"] = [c for c in df.columns if c not in keep]
    df = df[keep]

    # Auto-convert types (numeric, then datetime)
    for col in df.select_dtypes(include="object").columns:
        cleaned = df[col].str.replace(r"[,$₹€£%]", "", regex=True)
        as_num = pd.to_numeric(cleaned, errors="coerce")
        if as_num.notna().sum() >= 0.8 * df[col].notna().sum() and df[col].notna().sum() > 0:
            df[col] = as_num
            continue
        if any(k in col for k in ("date", "time", "dob", "day")):
            as_dt = pd.to_datetime(df[col], errors="coerce")
            if as_dt.notna().sum() >= 0.8 * df[col].notna().sum():
                df[col] = as_dt

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    log["duplicates_removed"] = before - len(df)

    # Handle missing values
    num_cols = df.select_dtypes(include="number").columns
    cat_cols = df.select_dtypes(exclude=["number", "datetime"]).columns
    if missing_strategy == "Fill (median/mode)":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].median())
        for c in cat_cols:
            if df[c].notna().any():
                df[c] = df[c].fillna(df[c].mode().iloc[0])
    elif missing_strategy == "Fill (mean/mode)":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].mean())
        for c in cat_cols:
            if df[c].notna().any():
                df[c] = df[c].fillna(df[c].mode().iloc[0])
    elif missing_strategy == "Drop rows with missing":
        df = df.dropna()

    # Outliers (IQR method)
    if remove_outliers and len(num_cols):
        before = len(df)
        for c in num_cols:
            q1, q3 = df[c].quantile([0.25, 0.75])
            iqr = q3 - q1
            df = df[((df[c] >= q1 - 1.5 * iqr) & (df[c] <= q3 + 1.5 * iqr)) | df[c].isna()]
        log["outliers_removed"] = before - len(df)

    df = df.reset_index(drop=True)
    log["rows_after"], log["cols_after"] = df.shape
    log["missing_after"] = int(df.isna().sum().sum())
    return df, log


# ---------- Sidebar options ----------
st.sidebar.header("Cleaning Options")
missing_strategy = st.sidebar.selectbox(
    "Missing values",
    ["Fill (median/mode)", "Fill (mean/mode)", "Drop rows with missing", "Leave as is"],
)
drop_thresh = st.sidebar.slider("Drop columns with missing % above", 0.1, 1.0, 0.6, 0.05)
remove_outliers = st.sidebar.checkbox("Remove outliers (IQR)", value=False)

# ---------- Main ----------
uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded:
    try:
        raw = read_csv_safely(uploaded)
    except Exception as e:
        st.error(str(e))
        st.stop()

    try:
        cleaned, log = clean_data(raw, missing_strategy, remove_outliers, drop_thresh)
    except Exception as e:
        st.error(f"Cleaning failed: {e}")
        st.stop()

    csv_bytes = cleaned.to_csv(index=False).encode("utf-8")

    # Download button at the TOP, right after upload
    st.success("File cleaned successfully!")
    st.download_button(
        "⬇️ Download Cleaned CSV",
        data=csv_bytes,
        file_name="cleaned_data.csv",
        mime="text/csv",
        key="download_top",
    )

    st.subheader("Original Data")
    st.dataframe(raw.head(20), width="stretch")

    st.subheader("Cleaned Data")
    st.dataframe(cleaned.head(20), width="stretch")

    st.subheader("Cleaning Report")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", log["rows_after"], log["rows_after"] - log["rows_before"])
    c2.metric("Columns", log["cols_after"], log["cols_after"] - log["cols_before"])
    c3.metric("Missing values", log["missing_after"], log["missing_after"] - log["missing_before"])
    c4.metric("Duplicates removed", log["duplicates_removed"])

    if log.get("cols_dropped_high_missing"):
        st.info(f"Dropped columns (too many missing): {log['cols_dropped_high_missing']}")
    if "outliers_removed" in log:
        st.info(f"Outlier rows removed: {log['outliers_removed']}")

    with st.expander("Column data types after cleaning"):
        st.write(cleaned.dtypes.astype(str))

    # Second download button at the bottom
    st.download_button(
        "⬇️ Download Cleaned CSV",
        data=csv_bytes,
        file_name="cleaned_data.csv",
        mime="text/csv",
        key="download_bottom",
    )