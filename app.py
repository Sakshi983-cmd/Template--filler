import streamlit as st
import fitz  # PyMuPDF
import openai
from docx import Document
import tempfile
import os

# ✅ Securely load OpenRouter API key
openai.api_key = st.secrets.get("api", {}).get("openrouter_key", "")

# Page config
st.set_page_config(page_title="Task 3 - Insurance Template Filler")
st.title("📄 Insurance Template Auto-Filler using PDF + LLM")

# Upload inputs
template_file = st.file_uploader("Upload Insurance Template (.docx)", type="docx")
pdf_files = st.file_uploader("Upload PDF Photo Reports", type="pdf", accept_multiple_files=True)

# ✅ Extract text from uploaded PDFs
def extract_text_from_pdfs(files):
    text = ""
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        doc = fitz.open(tmp_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    return text

# ✅ Call LLM using OpenRouter API
def fill_template_with_llm(template_text, pdf_text):
    prompt = f"""You are an AI assistant. Fill the insurance template using the PDF content below:

PDF Content:
{pdf_text}

Template:
{template_text}

Return the filled template:"""

    response = openai.chat.completions.create(
        model="mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# ✅ Generate filled document on button click
if st.button("Generate Filled Template") and template_file and pdf_files:
    st.info("📤 Extracting text from PDFs...")
    pdf_text = extract_text_from_pdfs(pdf_files)

    st.info("📄 Reading insurance template...")
    doc = Document(template_file)
    template_text = "\n".join([p.text for p in doc.paragraphs])

    st.info("🧠 Calling LLM to generate filled content...")
    filled_output = fill_template_with_llm(template_text, pdf_text)

    st.success("✅ Template filled successfully!")

    filled_doc = Document()
    for line in filled_output.split("\n"):
        filled_doc.add_paragraph(line.strip())

    output_path = os.path.join(tempfile.gettempdir(), "filled_template.docx")
    filled_doc.save(output_path)

    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download Filled Template", f, file_name="filled_template.docx")
