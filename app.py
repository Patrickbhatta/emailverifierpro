
import streamlit as st
import pandas as pd
from verify_logic import verify_email

st.set_page_config(page_title="EmailVerifierPro", layout="wide")
st.markdown("""
<style>
body {
  background: linear-gradient(135deg, #4c6ef5, #d0bfff);
  color: white;
}
section.main > div {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 2rem;
    border-radius: 10px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.1);
}
h1, h2, h3 {
  color: white;
}
.stButton > button {
    background-color: #5f3dc4;
    color: white;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #845ef7;
}
</style>
""", unsafe_allow_html=True)

st.title("✨ EmailVerifierPro")
st.markdown("Smart, beautiful email verification — built for creators and teams who care about quality.")

st.header("📤 Step 1: Upload Your Emails")
upload_method = st.radio("Choose input method", ["Upload CSV or Excel", "Paste Manually"])
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if upload_method == "Upload CSV or Excel":
    file = st.file_uploader("Upload .csv or .xlsx file", type=["csv", "xlsx"])
    if file:
        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
            df.columns = ["email"]
            df.drop_duplicates(inplace=True)
            st.session_state.uploaded_df = df
            st.success(f"✅ Uploaded {len(df)} unique emails.")
        except Exception as e:
            st.error(f"❌ Error: {e}")
else:
    pasted = st.text_area("Paste emails below (one per line):")
    if pasted:
        lines = [line.strip() for line in pasted.split("\n") if line.strip()]
        df = pd.DataFrame(lines, columns=["email"])
        df.drop_duplicates(inplace=True)
        st.session_state.uploaded_df = df
        st.success(f"✅ Pasted {len(df)} unique emails.")

if st.session_state.uploaded_df is not None:
    st.header("🔍 Step 2: Email Verification")
    st.info("This may take a few seconds depending on number of emails...")

    results = []
    for email in st.session_state.uploaded_df["email"]:
        results.append(verify_email(email))
    df_verified = pd.DataFrame(results)
    st.success("🎉 Verification complete!")

    with st.expander("📄 View Verified Emails"):
        st.dataframe(df_verified)

    st.markdown("### 🎯 Risk Score Guide (1–10)")
    st.markdown("""
| Score | Meaning |
|-------|-----------------------------|
| 1     | ✅ Very Safe                |
| 2–3   | ✅ Low Risk                 |
| 4–6   | ⚠️ Medium Risk              |
| 7–8   | ❌ High Risk                |
| 9–10  | ⛔ Invalid / Very Risky     |
""")

    st.header("🎯 Step 3: Filter & Download")
    st.download_button("⬇️ Download All Results", df_verified.to_csv(index=False), file_name="all_results.csv")

    valid_df = df_verified[df_verified["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("⬇️ Download Valid Only", valid_df.to_csv(index=False), file_name="valid_emails.csv")

    risky_df = df_verified[df_verified["status"] == "risky"]
    if not risky_df.empty:
        selected = st.multiselect("Select Risk Scores to Download", options=list(range(1, 11)), default=[4,5,6])
        filtered = risky_df[risky_df["risk_score"].isin(selected)]
        if not filtered.empty:
            st.download_button(f"⬇️ Download Risky (Score {selected})", filtered.to_csv(index=False), file_name="risky_filtered.csv")
        else:
            st.info("No risky emails found with selected scores.")
else:
    st.info("⬆️ Upload or paste emails to start.")
