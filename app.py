import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from engine_wrapper import run_osint_investigation
from reporting.generator import ReportGenerator

load_dotenv()

st.set_page_config(
    page_title="OSINT Intelligence Framework",
    page_icon="Search",
    layout="wide"
)

if "investigation_obj" not in st.session_state:
    st.session_state.investigation_obj = None
if "investigation_json" not in st.session_state:
    st.session_state.investigation_json = None
if "report_path" not in st.session_state:
    st.session_state.report_path = None
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None

st.title("OSINT Intelligence Framework")
st.markdown("Multi-vector Infrastructure & Entity Discovery")

target = st.text_input(
    "Target Entity",
    placeholder="e.g., Company Name, Individual, Domain"
)

st.divider()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    scan_button = st.button(
        "Run Investigation",
        use_container_width=True,
        type="primary"
    )

if scan_button:
    if not target.strip():
        st.error("Please enter a target entity to investigate.")
    else:
        progress_bar = st.progress(0)

        with st.spinner(f"Executing Search-First Discovery for '{target}'..."):
            report_path, investigation = asyncio.run(run_osint_investigation(target))
            st.session_state.report_path = report_path
            st.session_state.investigation_obj = investigation
            st.session_state.investigation_json = investigation.model_dump_json()
            progress_bar.progress(100)

if st.session_state.report_path and os.path.exists(st.session_state.report_path):
    st.success("Intelligence Gathering Complete")

    with open(st.session_state.report_path, "rb") as file:
        markdown_data = file.read()

    report_filename = st.session_state.report_path.split("/")[-1]
    
    report_generator = ReportGenerator()
    
    if st.session_state.get("pdf_path") is None:
        try:
            with st.spinner("Generating PDF report..."):
                pdf_path = report_generator.generate_pdf(st.session_state.investigation_obj)
                st.session_state.pdf_path = pdf_path
        except Exception as e:
            st.warning(f"Could not generate PDF: {str(e)}")
            st.session_state.pdf_path = None
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.download_button(
            label="Download Report (Markdown)",
            data=markdown_data,
            file_name=report_filename,
            mime="text/markdown",
            use_container_width=True
        )
    
    with col2:
        if st.session_state.get("pdf_path") and os.path.exists(st.session_state.pdf_path):
            with open(st.session_state.pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            
            pdf_filename = st.session_state.pdf_path.split("/")[-1]
            st.download_button(
                label="Download Report (PDF)",
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.button("PDF unavailable", disabled=True, use_container_width=True)
    
    with col3:
        if st.button("Clear Results", use_container_width=True):
            st.session_state.report_path = None
            st.session_state.investigation_obj = None
            st.session_state.investigation_json = None
            st.session_state.pdf_path = None
            st.rerun()

    st.divider()

    with st.expander("Report Preview", expanded=True):
        st.markdown(markdown_data.decode("utf-8"))

else:
    if st.session_state.report_path is None:
        st.info("Enter a target entity and click 'Run Investigation' to begin.")

st.divider()

with st.sidebar:
    st.header("About")
    st.markdown("""
    OSINT Intelligence Framework

    A production-grade Open-Source Intelligence engine combining:

    - Social discovery (Google Dorking)
    - Technical reconnaissance (GitHub, WHOIS)
    - Regulatory searches (OpenCorporates)
    - Confidence-based entity resolution

    Architecture: Search-First, OPSEC-conscious, modular adapter pattern.
    """)

    st.divider()

    st.subheader("Documentation")
    st.markdown("""
    - [GitHub Repository](https://github.com/tsvlgd/osint-prototype)
    - [Architecture Guide](https://github.com/tsvlgd/osint-prototype#2-architecture--design-philosophy-search-first)
    - [Example Report](https://github.com/tsvlgd/osint-prototype/blob/main/reports/travis_haasch%E2%80%9D_ceo_of_aigeeks_osint_report_20260416_153815.md)
    """)
