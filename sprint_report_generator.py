import streamlit as st
import pandas as pd
import requests
from io import BytesIO

st.set_page_config(page_title="Shared Excel Report", layout="wide")
st.title("📊 Report from Shared OneDrive/SharePoint Excel")

# Input the shared link
shared_link = st.text_input(
    "https://impelsysinc-my.sharepoint.com/:x:/g/personal/anandu_m_medlern_com/Edy6v_ixZWdHj4OYIs3ZtDgBalxe6J2ZD5f6I3pWqK9O3A?e=O1RZXS&nav=MTVfezVFNDJCRDIzLTMzMzUtNDkzMC1BMjFDLTREMDYzNURGODg4N30", 
    "https://impelsysinc-my.sharepoint.com/:x:/g/personal/…?e=EjqRGl"
)

def get_direct_download_link(shared_link: str) -> str:
    """
    Converts a share link into a direct download URL.
    """
    # Replace '?e=' parameters with '?download=1'
    if '?e=' in shared_link:
        return shared_link.split('?e=')[0] + '?download=1'
    return shared_link

if st.button("Load Report"):
    dl_url = get_direct_download_link(shared_link)
    st.write("✅ Using download URL:", dl_url)
    resp = requests.get(dl_url)
    if resp.status_code == 200:
        df = pd.read_excel(BytesIO(resp.content))
        st.success("✔️ File loaded successfully!")
        st.subheader("Preview")
        st.dataframe(df)

        if st.checkbox("Show summary"):
            st.subheader("Summary statistics")
            st.table(df.describe())

        if st.checkbox("Show chart of numeric columns"):
            st.bar_chart(df.select_dtypes("number"))
    else:
        st.error(f"⚠️ Failed to download file (status code {resp.status_code})")
