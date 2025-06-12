import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Excel Report Viewer", layout="wide")
st.title("📊 Excel Report from SharePoint")

# Pre-filled direct download link
shared_link = st.text_input(
    "Excel download link",
    "https://impelsysinc-my.sharepoint.com/:x:/g/personal/anandu_m_medlern_com/Edy6v_ixZWdHj4OYIs3ZtDgBWZTJAOeZKXNIFgiiGBzqJw?download=1"
)

if st.button("Load Excel"):
    try:
        response = requests.get(shared_link)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content))

        st.success("File loaded successfully!")
        st.subheader("📄 Data Preview")
        st.dataframe(df)

        if st.checkbox("Show summary statistics"):
            st.subheader("📊 Summary Statistics")
            st.write(df.describe())

        if st.checkbox("Show numeric chart"):
            st.subheader("📈 Numeric Columns")
            st.bar_chart(df.select_dtypes(include='number'))
    except Exception as e:
        st.error(f"Failed to load file: {e}")
