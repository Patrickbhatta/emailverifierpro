
import streamlit as st
import pandas as pd
import re
from verify_logic import verify_email

st.set_page_config(page_title="EmailVerifierPro", layout="wide")

# Apply gradient background + icon styling
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
h1, h2, h3, .stMarkdown {
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

st.title("📩 EmailVerifierPro")
st.markdown("Turn raw email lists into 💡 insights with clean verification and real-time risk scoring.")

st.header("📤 Step 1: Upload Email List")
upload_method = st.radio("Upload type", ["Upload CSV or Excel", "Paste Emails"])

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
    st.session_state.email_column = None

if upload_method == "Upload CSV or Excel":
    file = st.file_uploader("Upload your file", type=["csv", "xlsx"])
    if file:
        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
            st.session_state.uploaded_df = df

            email_col = None
            for col in df.columns:
                sample = df[col].astype(str).dropna().head(50).tolist()
                hits = sum([1 for v in sample if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", v)])
                if hits >= len(sample) * 0.5:
                    email_col = col
                    break

            if email_col:
                st.session_state.email_column = email_col
                st.success(f"✅ Detected email column: '{email_col}'")
            else:
                st.warning("⚠️ No email column detected, please select manually.")
                st.session_state.email_column = df.columns[0]

            st.markdown("### 👁️ Preview Data (highlighted = selected email column)")
            def highlight(x): return ['background-color: lightgreen' if x.name == st.session_state.email_column else '' for _ in x]
            st.dataframe(df.head(10).style.apply(highlight, axis=0))

            selected = st.selectbox("🎯 Confirm or select email column:", options=df.columns, index=df.columns.get_loc(st.session_state.email_column))
            st.session_state.email_column = selected

        except Exception as e:
            st.error(f"❌ Upload error: {e}")
else:
    pasted = st.text_area("Paste emails (one per line):")
    if pasted:
        rows = [line.strip() for line in pasted.split("\n") if line.strip()]
        df = pd.DataFrame(rows, columns=["email"])
        st.session_state.uploaded_df = df
        st.session_state.email_column = "email"
        st.success(f"✅ Pasted {len(df)} emails.")

if st.session_state.uploaded_df is not None and st.session_state.email_column:
    st.header("🔍 Step 2: Verify Emails")
    st.info("This may take a few seconds...")

    results = []
    for email in st.session_state.uploaded_df[st.session_state.email_column].dropna():
        results.append(verify_email(email))
    df_verified = pd.DataFrame(results)
    st.success("🎉 Verification complete!")

    with st.expander("📄 View Full Verification Results"):
        st.dataframe(df_verified)

    st.header("🎯 Step 3: Filter & Download")

    st.download_button("⬇️ Download All Results", df_verified.to_csv(index=False), file_name="all_results.csv")

    valid_df = df_verified[df_verified["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("✅ Download Valid Only", valid_df.to_csv(index=False), file_name="valid_emails.csv")

    risky_df = df_verified[df_verified["status"] == "risky"]
    if not risky_df.empty:
        st.subheader("⚠️ Risky Emails Filter")

        # Move risk score legend inside here
        st.markdown("#### 🧠 Risk Score Meaning")
        st.markdown("""
| Score | Meaning |
|-------|-----------------------------|
| 1     | ✅ Very Safe                |
| 2–3   | ✅ Low Risk                 |
| 4–6   | ⚠️ Medium Risk              |
| 7–8   | ❌ High Risk                |
| 9–10  | ⛔ Invalid / Very Risky     |
""")

        selected = st.multiselect("Select risk scores to download", options=list(range(1, 11)), default=[4,5,6])
        filtered = risky_df[risky_df["risk_score"].isin(selected)]
        if not filtered.empty:
            st.download_button(f"⬇️ Download Risky (Score: {selected})", filtered.to_csv(index=False), file_name="risky_filtered.csv")
        else:
            st.info("No risky emails with selected scores.")
else:
    st.info("⬆️ Upload or paste to begin.")
