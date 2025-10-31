# frontend/app.py
import streamlit as st
import requests

st.set_page_config(page_title="Document Processing Agent", layout="wide")
st.title("📄 Document Processing Agent")
st.write("Upload your invoice (PDF or Image) to extract, validate, and send to ERP automatically.")

uploaded = st.file_uploader("📤 Upload Invoice", type=["pdf", "jpg", "jpeg", "png"])

if uploaded:
    with st.spinner("Processing your invoice..."):
        # Build multipart/form-data correctly:
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
        try:
            response = requests.post("http://127.0.0.1:8000/process-invoice/", files=files, timeout=60)
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            st.success("✅ Invoice Processed Successfully!")
            st.json(result.get("data"))
        else:
            st.error(f"❌ Error: {result.get('detail') or result.get('message')}")
    else:
        st.error(f"Backend error. Status {response.status_code}: {response.text}")
