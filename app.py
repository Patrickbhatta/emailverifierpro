import streamlit as st
import pandas as pd
import datetime

# Streamlit page setup
st.set_page_config(page_title="EmailVerifierPro", layout="wide")

st.title("🚀 EmailVerifierPro")
st.markdown("Clean your email list in seconds — verify, score, and download.")

# Session state to hold uploaded data
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# Sidebar for file upload
st.sidebar.header("Upload Email List")
upload_method = st.sidebar.radio("Upload Method", ["CSV", "Excel", "Paste Emails"])

# File upload
if upload_method in ["CSV", "Excel"]:
    uploaded_file = st.sidebar.file_uploader("Upload your file", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            if "email" not in df.columns[0].lower():
                st.error("First column must be labeled as 'email'")
            else:
                df.columns = ["email"]
                df.drop_duplicates(inplace=True)
                st.session_state.uploaded_df = df
                st.success(f"{len(df)} emails uploaded successfully!")
        except Exception as e:
            st.error(f"Failed to read file: {e}")
else:
    pasted_data = st.sidebar.text_area("Paste emails (one per line)")
    if pasted_data:
        lines = pasted_data.strip().split("\n")
        df = pd.DataFrame(lines, columns=["email"])
        df.drop_duplicates(inplace=True)
        st.session_state.uploaded_df = df
        st.success(f"{len(df)} emails pasted successfully!")

# Display uploaded emails
if st.session_state.uploaded_df is not None:
    st.subheader("📬 Uploaded Emails")
    st.dataframe(st.session_state.uploaded_df)

    # Basic verification placeholder
    st.subheader("🛠️ Verification Results (Mock Preview)")
    verified_df = st.session_state.uploaded_df.copy()
    verified_df["status"] = ["valid", "risky", "invalid"] * (len(verified_df) // 3 + 1)
    verified_df = verified_df.head(len(st.session_state.uploaded_df))
    st.dataframe(verified_df)

    # Downloads
    st.download_button(
        "⬇️ Download All Results",
        verified_df.to_csv(index=False),
        file_name=f"email_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
    )
else:
    st.info("Upload or paste emails to get started.")
