import os
import base64
import tempfile
import shutil
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import fitz  
import pandas as pd

# LangChain + Groq + HuggingFace
# from langchain_groq import ChatGroq
# from langchain.embeddings import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient   # ✅ use HuggingFace InferenceClient

load_dotenv()


st.set_page_config(page_title="Gemma 3 OCR", layout="wide")


if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = None
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None


st.markdown(
    """
    <h1 style='color:#2E96FF; text-align:center;'>📄 Gemma 3 OCR with HuggingFace + Groq</h1>
    <p style='text-align:center; color:gray;'>Upload PDFs or Images → Extract Structured Text → Export in Multiple Formats</p>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    # st.subheader("🔑 API Keys")
    # groq_api_key = st.text_input(
    #     "Groq API Key",
    #     value=os.getenv("GROQ_API_KEY", ""),
    #     type="password",
    #     help="Your Groq API key",
    # )

    hf_api_key = st.text_input(
        "HuggingFace API Token",
        value=os.getenv("HF_API_KEY", ""),
        type="password",
        help="Your HuggingFace token",
    )

    st.divider()

    
    st.subheader("📂 Upload PDF or Image")
    uploaded_file = st.file_uploader(
        "Choose a PDF, JPG, or PNG file",
        type=["pdf", "jpg", "jpeg", "png"],
        accept_multiple_files=False,
    )


def display_file_preview(file):
    if file is None:
        return
    file_type = file.type
    if file_type == "application/pdf":
        st.sidebar.subheader("PDF Preview")
        base64_pdf = base64.b64encode(file.getvalue()).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500"></iframe>'
        st.sidebar.markdown(pdf_display, unsafe_allow_html=True)
    elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
        st.sidebar.subheader("Image Preview")
        st.sidebar.image(file, use_container_width=True)


def gemma_ocr_image(file_bytes, file_type, hf_token):
    """Send image bytes to HuggingFace Inference API using InferenceClient."""
    b64_data = base64.b64encode(file_bytes).decode()

    try:
        client = InferenceClient(token=hf_token)
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it",   
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract details in well-structured text and tables where applicable."},
                        {"type": "image_url", "image_url": {"url": f"data:{file_type};base64,{b64_data}"}}
                    ],
                }
            ],
            max_tokens=512,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"❌ HuggingFace API call failed: {e}"

def process_pdf(file, hf_token):
    """Convert PDF pages to images and run OCR per page."""
    results = []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(file.getvalue())
        tmp_pdf.flush()
        doc = fitz.open(tmp_pdf.name)
        num_pages = doc.page_count
        progress = st.progress(0, text="Processing PDF pages...")
        for i in range(num_pages):
            page = doc.load_page(i)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            text = gemma_ocr_image(img_bytes, "image/png", hf_token)
            results.append(f"--- Page {i+1} ---\n{text}")
            progress.progress((i + 1) / num_pages, text=f"Processed {i+1}/{num_pages} pages")
        progress.empty()
    return "\n\n".join(results)

# EXPORT FUNCTIONS
def export_pdf(text):
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    file_path = "extracted_text.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    story = [Paragraph(p, styles["Normal"]) for p in text.split("\n")]
    doc.build(story)
    return file_path

def export_docx(text):
    from docx import Document
    doc = Document()
    doc.add_paragraph(text)
    file_path = "extracted_text.docx"
    doc.save(file_path)
    return file_path

def export_csv(text):
    file_path = "extracted_text.csv"
    df = pd.DataFrame({"Extracted Text": text.split("\n")})
    df.to_csv(file_path, index=False)
    return file_path

# HANDLE FILE UPLOAD 
if uploaded_file is not None:
    display_file_preview(uploaded_file)

    if st.button("🔍 Extract Text (OCR)", use_container_width=True, type="primary"):
        if not hf_api_key:
            st.error(" Missing HuggingFace API key")
            st.stop()

        if uploaded_file.type == "application/pdf":
            extracted_text = process_pdf(uploaded_file, hf_api_key)
        else:
            extracted_text = gemma_ocr_image(uploaded_file.getvalue(), uploaded_file.type, hf_api_key)

        st.session_state.extracted_text = extracted_text

# ---------------- DISPLAY OCR OUTPUT ----------------
if st.session_state.extracted_text:
    st.markdown("### ✅ Extracted Text")
    st.text_area("Output", st.session_state.extracted_text, height=400)

    st.markdown("### 📤 Export Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.download_button("⬇️ Export as PDF", open(export_pdf(st.session_state.extracted_text), "rb"), "extracted_text.pdf"):
            pass
    with col2:
        if st.download_button("⬇️ Export as DOCX", open(export_docx(st.session_state.extracted_text), "rb"), "extracted_text.docx"):
            pass
    with col3:
        if st.download_button("⬇️ Export as CSV", open(export_csv(st.session_state.extracted_text), "rb"), "extracted_text.csv"):
            pass
