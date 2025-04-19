
import streamlit as st
import pandas as pd
import datetime
import random
from verify_logic import verify_email

st.set_page_config(page_title="EmailVerifierPro", layout="wide")
st.title("📬 EmailVerifierPro")
st.markdown("Verify, filter, and download email lists with smart risk scoring (1 = safest, 10 = riskiest)")

# Session setup
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

# Upload UI
st.subheader("📤 Upload Email List")
upload_method = st.radio("Select method", ["CSV", "Excel", "Paste Emails"])

if upload_method in ["CSV", "Excel"]:
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            if "email" not in df.columns[0].lower():
                st.error("❌ First column must contain emails")
            else:
                df.columns = ["email"]
                df.drop_duplicates(inplace=True)
                st.session_state.uploaded_df = df
                st.success(f"✅ {len(df)} emails uploaded")
        except Exception as e:
            st.error(f"Upload failed: {e}")
else:
    pasted = st.text_area("Paste emails here (one per line):")
    if pasted:
        emails = pasted.strip().split("\n")
        df = pd.DataFrame(emails, columns=["email"])
        df.drop_duplicates(inplace=True)
        st.session_state.uploaded_df = df
        st.success(f"✅ {len(df)} emails pasted")

# Risk Score Legend
st.subheader("🎯 Risk Score Meaning (1–10)")
st.markdown("""
| Score | Meaning |
|-------|-----------------------------|
| 1     | ✅ Very Safe                |
| 2–3   | ✅ Low Risk                 |
| 4–6   | ⚠️ Medium Risk              |
| 7–8   | ❌ High Risk                |
| 9–10  | ⛔ Invalid / Very Risky     |
""")

# If emails are uploaded
if st.session_state.uploaded_df is not None:
    st.subheader("🔍 Verifying Emails...")

    results = []
    for email in st.session_state.uploaded_df["email"]:
        results.append(verify_email(email))
    results_df = pd.DataFrame(results)

    st.success("✅ Verification complete")
    st.dataframe(results_df)

    # Download All
    st.download_button("⬇️ Download All Results", results_df.to_csv(index=False), file_name="all_emails.csv")

    # Valid Only
    valid_df = results_df[results_df["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("⬇️ Download Valid Emails", valid_df.to_csv(index=False), file_name="valid_emails.csv")

    # Risky Filter
    risky_df = results_df[results_df["status"] == "risky"]
    if not risky_df.empty:
        st.subheader("🎯 Download Risky Emails by Score")
        selected_scores = st.multiselect("Select risk scores (1–10)", options=list(range(1, 11)), default=[4, 5, 6])
        filtered = risky_df[risky_df["risk_score"].isin(selected_scores)]
        if not filtered.empty:
            st.download_button(f"⬇️ Download Risky (Score: {selected_scores})", filtered.to_csv(index=False), file_name="filtered_risky_emails.csv")
        else:
            st.info("No risky emails match selected scores.")
else:
    st.info("Upload or paste emails above to begin.")
