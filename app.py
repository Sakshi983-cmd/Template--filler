import streamlit as st
import openai
import fitz
from docx import Document
import tempfile
import os

openai.api_key = st.secrets["OPENROUTER_API_KEY"]
openai.api_base = "https://openrouter.ai/api/v1"

st.set_page_config(page_title="Task 3 - Insurance Template Filler")
st.title("📄 Insurance Template Auto-Filler using PDF + LLM")

template_file = st.file_uploader("Upload Insurance Template (.docx)", type="docx")
pdf_files = st.file_uploader("Upload PDF Photo Reports", type="pdf", accept_multiple_files=True)

def extract_text_from_pdfs(files):
    text = ""
    for f in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(f.read())
            path = tmp.name
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
        doc.close()
    return text

def fill_template(template_text, pdf_text):
    prompt = f\"\"\"You are an AI assistant. Fill the insurance template using the PDF content below:

PDF Content:
{pdf_text}

Template:
{template_text}

Return the filled template:
\"\"\"
    response = openai.ChatCompletion.create(
        model="mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response["choices"][0]["message"]["content"]

if st.button("Generate Filled Template") and template_file and pdf_files:
    extracted = extract_text_from_pdfs(pdf_files)
    doc = Document(template_file)
    template = "\\n".join([p.text for p in doc.paragraphs])
    result = fill_template(template, extracted)

    st.success("Filled template generated ✅")

    final_doc = Document()
    for line in result.split('\\n'):
        final_doc.add_paragraph(line.strip())

    out_path = os.path.join(tempfile.gettempdir(), "output.docx")
    final_doc.save(out_path)

    with open(out_path, "rb") as file:
        st.download_button("⬇️ Download", file, file_name="filled_template.docx")
