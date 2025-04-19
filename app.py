
import streamlit as st
import pandas as pd
from verify_logic import verify_email

st.set_page_config(page_title="EmailVerifierPro", layout="wide")
st.title("📧 EmailVerifierPro")
st.markdown("Easily verify your email lists with simple steps. No tech skills needed.")

# Step 1: Upload
st.header("Step 1: Upload Your Emails")
upload_type = st.radio("Choose how to upload:", ["CSV File", "Excel File", "Paste Emails"])

if upload_type in ["CSV File", "Excel File"]:
    uploaded_file = st.file_uploader("Upload file here", type=["csv", "xlsx"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        df.columns = ["email"]
        df.drop_duplicates(inplace=True)
        st.session_state.df = df
        st.success(f"{len(df)} emails uploaded.")
else:
    pasted_emails = st.text_area("Paste one email per line")
    if pasted_emails:
        lines = pasted_emails.strip().split("\n")
        df = pd.DataFrame(lines, columns=["email"])
        df.drop_duplicates(inplace=True)
        st.session_state.df = df
        st.success(f"{len(df)} emails pasted.")

# Step 2: Verify
if "df" in st.session_state:
    st.header("Step 2: Email Verification")
    with st.spinner("Verifying emails, please wait..."):
        verified = [verify_email(email) for email in st.session_state.df["email"]]
        verified_df = pd.DataFrame(verified)
        st.session_state.verified_df = verified_df

    st.success("Verification complete!")
    st.dataframe(verified_df)

    # Step 3: Filter + Download
    st.header("Step 3: Download Emails")
    st.subheader("🎯 What Risk Scores Mean (1 = safest, 10 = riskiest):")
    st.markdown("- **1–3**: Very safe and valid\n- **4–6**: Medium risk — may bounce\n- **7–8**: High risk — likely to bounce\n- **9–10**: Invalid or blocked")

    st.download_button("📥 Download All Results", verified_df.to_csv(index=False), file_name="all_results.csv")

    valid_df = verified_df[verified_df["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("✅ Download Valid Emails", valid_df.to_csv(index=False), file_name="valid_emails.csv")

    risky_df = verified_df[verified_df["status"] == "risky"]
    if not risky_df.empty:
        selected = st.multiselect("Select Risk Scores to Download", options=list(range(1, 11)), default=[4,5,6])
        filtered = risky_df[risky_df["risk_score"].isin(selected)]
        if not filtered.empty:
            st.download_button("⚠️ Download Filtered Risky Emails", filtered.to_csv(index=False), file_name="risky_filtered.csv")
else:
    st.info("Upload emails to begin.")
