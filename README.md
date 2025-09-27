# 📄 Gemma 3 OCR with HuggingFace + Groq

A **Streamlit application** that allows you to upload **PDFs or images** and extract well-structured text using **Google Gemma 3 via HuggingFace Inference API**.  
The app also supports **multi-format export (PDF, DOCX, CSV)** for easy sharing and usage.

---

## 🚀 Features
- ✅ Upload **PDF, JPG, JPEG, PNG**
- ✅ Preview uploaded file (PDF or image) in the sidebar
- ✅ Perform OCR using **Gemma 3 (27B-IT)** via HuggingFace InferenceClient
- ✅ Extract structured text (tables, key details, etc.)
- ✅ Process PDFs page-by-page with a progress bar
- ✅ Export results to:
  - **PDF**
  - **DOCX**
  - **CSV**
- ✅ Fully integrated with **Streamlit Cloud** deployment

---

## 🛠️ Tech Stack
- **[Streamlit](https://streamlit.io/)** → Web interface
- **[HuggingFace Inference API](https://huggingface.co/inference-api)** → OCR model (Gemma 3)
- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** → Convert PDF pages to images
- **[Pandas](https://pandas.pydata.org/)** → Export CSV
- **[ReportLab](https://www.reportlab.com/opensource/)** → Export PDF
- **[python-docx](https://python-docx.readthedocs.io/en/latest/)** → Export DOCX

---

## 🔑 Getting HuggingFace API Token
To use this app, you need a **HuggingFace API token**.

1. Go to [HuggingFace](https://huggingface.co/) and **sign up / log in**.
2. Navigate to your [Access Tokens page](https://huggingface.co/settings/tokens).
3. Click **New Token** → Choose a name (e.g., `gemma3-ocr`) and select **Read** role.
4. Copy the token (it will look like `hf_xxxxx...`).
5. In the app sidebar, paste your token in the **HuggingFace API Token** field.
6. Or, you can set it in your environment as:
   ```bash
   export HF_API_KEY="your_token_here"
