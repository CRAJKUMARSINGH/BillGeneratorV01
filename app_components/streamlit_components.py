"""
Reusable Streamlit UI components for BillGeneratorV01.
These components are purely presentational and call into existing repo functions.
"""

from functools import partial
from pathlib import Path
import streamlit as st

def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:16px;">
          <img src="branding/logo_small.png" height="48" style="border-radius:6px" />
          <div>
            <h2 style="margin:0">{title}</h2>
            <div style="color:#6b7280;margin-top:2px">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def file_uploader(label="Upload input file", key="input_file"):
    uploaded = st.file_uploader(label, type=["xlsx", "xls", "csv"], key=key)
    return uploaded

def run_button(label="Generate Bills"):
    col1, col2 = st.columns([1,4])
    with col1:
        return st.button(label)

def status_message(text: str, level: str = "info"):
    if level == "info":
        st.info(text)
    elif level == "success":
        st.success(text)
    elif level == "error":
        st.error(text)
    else:
        st.write(text)

def outputs_list(output_dir="output"):
    p = Path(output_dir)
    if not p.exists():
        st.write("No outputs yet.")
        return []
    files = sorted([str(x) for x in p.glob("*")])
    for f in files:
        st.markdown(f"- {Path(f).name} — <a href='{f}'>download</a>", unsafe_allow_html=True)
    return files