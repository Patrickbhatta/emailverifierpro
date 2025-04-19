
import streamlit as st
import pandas as pd
import re
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
st.markdown("Smart email verification with clear column detection and smooth filtering.")

st.header("📤 Step 1: Upload Your Emails")
upload_method = st.radio("Choose input method", ["Upload CSV or Excel", "Paste Manually"])

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
    st.session_state.email_column = None

if upload_method == "Upload CSV or Excel":
    file = st.file_uploader("Upload .csv or .xlsx file", type=["csv", "xlsx"])
    if file:
        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
            st.session_state.uploaded_df = df

            # Detect email-like column
            email_col = None
            for col in df.columns:
                sample = df[col].astype(str).dropna().head(50).tolist()
                email_hits = sum([1 for val in sample if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", val)])
                if email_hits >= len(sample) * 0.5:
                    email_col = col
                    break

            if email_col:
                st.session_state.email_column = email_col
                st.success(f"✅ Detected email column: '{email_col}'")
            else:
                st.warning("⚠️ Couldn't detect email column automatically. Please select manually.")
                st.session_state.email_column = df.columns[0]

            # Show preview
            st.markdown("### 👀 Data Preview (highlighted column will be verified)")
            def highlight_col(x):
                return ['background-color: lightgreen' if x.name == st.session_state.email_column else '' for _ in x]

            st.dataframe(df.head(10).style.apply(highlight_col, axis=0))

            selected = st.selectbox("📝 Confirm or select email column:", options=df.columns, index=df.columns.get_loc(st.session_state.email_column))
            st.session_state.email_column = selected

        except Exception as e:
            st.error(f"❌ Error: {e}")

else:
    pasted = st.text_area("Paste emails below (one per line):")
    if pasted:
        emails = [line.strip() for line in pasted.split("\n") if line.strip()]
        df = pd.DataFrame(emails, columns=["email"])
        st.session_state.uploaded_df = df
        st.session_state.email_column = "email"
        st.success(f"✅ Pasted {len(df)} unique emails.")

if st.session_state.uploaded_df is not None and st.session_state.email_column:
    st.header("🔍 Step 2: Verify Emails")
    st.info("Processing...")

    results = []
    for email in st.session_state.uploaded_df[st.session_state.email_column].dropna():
        results.append(verify_email(email))
    df_verified = pd.DataFrame(results)
    st.success("🎉 Verification complete!")

    with st.expander("📄 View Results"):
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
        selected = st.multiselect("Select Risk Scores", options=list(range(1, 11)), default=[4,5,6])
        filtered = risky_df[risky_df["risk_score"].isin(selected)]
        if not filtered.empty:
            st.download_button(f"⬇️ Download Risky (Score {selected})", filtered.to_csv(index=False), file_name="risky_filtered.csv")
        else:
            st.info("No risky emails found with selected scores.")
else:
    st.info("⬆️ Upload or paste emails to get started.")
