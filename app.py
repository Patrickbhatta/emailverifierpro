import streamlit as st
import pandas as pd
import datetime
import random

# Setup
st.set_page_config(page_title="EmailVerifierPro", layout="wide")
st.title("🚀 EmailVerifierPro")
st.caption("Verify and clean your email lists in one place.")

# Session State
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# Upload Section
st.subheader("📤 Upload Your Emails")
upload_method = st.radio("Choose upload method:", ["CSV", "Excel", "Paste Emails"])

if upload_method in ["CSV", "Excel"]:
    uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx"])
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
            st.error(f"Error reading file: {e}")
else:
    pasted = st.text_area("Paste emails (one per line):")
    if pasted:
        lines = pasted.strip().split("\n")
        df = pd.DataFrame(lines, columns=["email"])
        df.drop_duplicates(inplace=True)
        st.session_state.uploaded_df = df
        st.success(f"{len(df)} emails pasted successfully!")

# Display + Mock Verification
if st.session_state.uploaded_df is not None:
    st.divider()
    st.subheader("📬 Uploaded Emails")
    st.dataframe(st.session_state.uploaded_df)

    st.subheader("🧠 Mock Email Verification Preview")

    df = st.session_state.uploaded_df.copy()
    statuses = ["valid", "risky", "invalid"]
    df["status"] = [statuses[i % 3] for i in range(len(df))]
    df["risk_score"] = df["status"].apply(lambda x: 0 if x == "valid" else (random.randint(1, 49) if x == "risky" else 100))

    st.dataframe(df)

    st.divider()
    st.subheader("⬇️ Download Options")

    st.download_button("Download All Results", df.to_csv(index=False), file_name="all_results.csv")

    valid_df = df[df["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("Download Only Valid Emails", valid_df.to_csv(index=False), file_name="valid_emails.csv")

    risky_df = df[df["status"] == "risky"]
    if not risky_df.empty:
        selected_score = st.slider("Select max risk score to include in download", min_value=1, max_value=49, value=25)
        filtered_risky = risky_df[risky_df["risk_score"] <= selected_score]
        if not filtered_risky.empty:
            st.download_button(f"Download Risky Emails (Score ≤ {selected_score})", filtered_risky.to_csv(index=False), file_name="risky_emails_filtered.csv")
        else:
            st.info("No risky emails found below the selected score.")
else:
    st.info("Upload or paste emails to get started.")
