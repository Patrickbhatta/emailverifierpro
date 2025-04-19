
import streamlit as st
import pandas as pd
import re
from datetime import datetime
from verify_logic import verify_email

st.set_page_config(page_title="EmailVerifierPro", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] > .main {
  background: linear-gradient(135deg, #4c6ef5, #d0bfff);
  background-attachment: fixed;
}
section.main > div {
  background-color: rgba(255, 255, 255, 0.04);
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
}
.stButton > button:hover {
  background-color: #845ef7;
}
</style>
""", unsafe_allow_html=True)

st.title("📩 EmailVerifierPro")
st.markdown("Upload, detect, confirm — and verify email lists with smart filters.")

st.header("📤 Step 1: Upload Email List")
upload_method = st.radio("Upload method:", ["Upload CSV or Excel", "Paste Emails"])

if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
    st.session_state.email_column = None
    st.session_state.verified_df = None
    st.session_state.download_history = []
    st.session_state.column_confirmed = False

if upload_method == "Upload CSV or Excel":
    file = st.file_uploader("Upload your file", type=["csv", "xlsx"])
    if file:
        df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
        st.session_state.uploaded_df = df

        email_col = None
        for col in df.columns:
            sample = df[col].astype(str).dropna().head(50).tolist()
            hits = sum([1 for v in sample if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", v)])
            if hits >= len(sample) * 0.5:
                email_col = col
                break
        st.session_state.email_column = email_col if email_col else df.columns[0]

        st.markdown("### 👁️ Data Preview")
        def highlight(x): return ['background-color: lightgreen' if x.name == st.session_state.email_column else '' for _ in x]
        st.dataframe(df.head(10).style.apply(highlight, axis=0))

        st.markdown("🚦 **We auto-selected the column below, but feel free to choose another before continuing.**")
        selected = st.selectbox("Select email column to use:", options=df.columns, index=df.columns.get_loc(st.session_state.email_column))
        st.session_state.email_column = selected

        if st.button("✅ Confirm Column Selection"):
            st.session_state.column_confirmed = True
            st.success(f"Column '{selected}' confirmed for verification ✅")

elif upload_method == "Paste Emails":
    pasted = st.text_area("Paste emails (one per line):")
    if pasted:
        rows = [line.strip() for line in pasted.split("\n") if line.strip()]
        df = pd.DataFrame(rows, columns=["email"])
        st.session_state.uploaded_df = df
        st.session_state.email_column = "email"
        st.session_state.column_confirmed = True
        st.success(f"✅ {len(df)} emails loaded from paste")

if st.session_state.uploaded_df is not None and st.session_state.email_column and st.session_state.column_confirmed:
    if st.button("🚀 Start Verification"):
        results = []
        for email in st.session_state.uploaded_df[st.session_state.email_column].dropna():
            results.append(verify_email(email))
        df_verified = pd.DataFrame(results)
        st.session_state.verified_df = df_verified
        st.success("🎉 Verification completed!")

if st.session_state.verified_df is not None:
    st.header("📊 Step 2: View & Download")
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    with st.expander("📄 Full Verified Data"):
        st.dataframe(st.session_state.verified_df)

    st.download_button("⬇️ Download All", st.session_state.verified_df.to_csv(index=False), file_name=f"all_results_{now_str}.csv")
    st.session_state.download_history.append(f"all_results_{now_str}.csv")

    valid_df = st.session_state.verified_df[st.session_state.verified_df["status"] == "valid"]
    if not valid_df.empty:
        st.download_button("✅ Download Valid", valid_df.to_csv(index=False), file_name=f"valid_emails_{now_str}.csv")
        st.session_state.download_history.append(f"valid_emails_{now_str}.csv")

    risky_df = st.session_state.verified_df[st.session_state.verified_df["status"] == "risky"]
    if not risky_df.empty:
        st.subheader("⚠️ Risky Email Filters")
        st.markdown("""
| Score | Meaning |
|-------|-----------------------------|
| 1     | ✅ Very Safe                |
| 2–3   | ✅ Low Risk                 |
| 4–6   | ⚠️ Medium Risk              |
| 7–8   | ❌ High Risk                |
| 9–10  | ⛔ Invalid / Very Risky     |
""")

        selected = st.multiselect("Select scores to download", list(range(1, 11)), default=[4, 5, 6])
        filtered = risky_df[risky_df["risk_score"].isin(selected)]
        if not filtered.empty:
            file = f"risky_score_{'_'.join(map(str, selected))}_{now_str}.csv"
            st.download_button(f"⬇️ Download Risky (Score: {selected})", filtered.to_csv(index=False), file_name=file)
            st.session_state.download_history.append(file)

if st.session_state.download_history:
    st.sidebar.subheader("📁 Recent Downloads")
    for item in reversed(st.session_state.download_history[-5:]):
        st.sidebar.markdown(f"✅ {item}")
