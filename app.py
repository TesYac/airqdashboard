import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="My Data App",
    page_icon="📊",
    layout="wide"
)

st.title("📊 My Data App")
st.write("Upload or load your data and explore it.")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    st.success("Data loaded successfully!")

    st.subheader("Preview")
    st.dataframe(df.head(100))

    st.subheader("Summary")
    st.write(df.describe())

    st.subheader("Columns")
    selected_columns = st.multiselect(
        "Choose columns to display",
        df.columns.tolist(),
        default=df.columns.tolist()[:5]
    )

    if selected_columns:
        st.dataframe(df[selected_columns])

    st.subheader("Simple Chart")
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if numeric_columns:
        chart_column = st.selectbox("Choose a numeric column", numeric_columns)
        st.line_chart(df[chart_column])
    else:
        st.info("No numeric columns found for charting.")
else:
    st.info("Upload a CSV file to begin.")