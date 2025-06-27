import streamlit as st
import fitz  # PyMuPDF
import openai
from docx import Document
import tempfile
import os

# ✅ Load OpenRouter API Key and Base URL
api_key = st.secrets.get("api", {}).get("openrouter_key", "")
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"  # Required for OpenRouter

# 🔍 Check API key
if not api_key or not api_key.startswith("sk-or-v1-"):
    st.error("❌ API key not loaded or invalid. Please check your Streamlit Secrets.")
    st.stop()
else:
    st.success("✅ OpenRouter API key loaded.")

# 🎯 Page config
st.set_page_config(page_title="Task 3 - Insurance Template Filler", layout="centered")
st.title("📄 Insurance Template Auto-Filler using PDF + LLM")

# 🤖 Choose Model (Optional)
model_choice = st.selectbox(
    "🤖 Choose LLM Model",
    ["mistralai/mistral-7b-instruct", "meta-llama/llama-3-8b-instruct", "openai/gpt-3.5-turbo"],
    index=0
)

# 📤 Upload Inputs
template_file = st.file_uploader("Upload Insurance Template (.docx)", type="docx")
pdf_files = st.file_uploader("Upload PDF Photo Reports", type="pdf", accept_multiple_files=True)

# 🧠 Extract text from PDFs
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

# 🤖 Call OpenRouter LLM to fill template
def fill_template_with_llm(template_text, pdf_text, model):
    prompt = f"""You are an AI assistant. Fill the insurance template using the PDF content below:

PDF Content:
{pdf_text}

Template:
{template_text}

Return the filled template:"""

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# 🔄 Main Execution
if st.button("Generate Filled Template") and template_file and pdf_files:
    st.info("📤 Extracting text from PDFs...")
    pdf_text = extract_text_from_pdfs(pdf_files)

    with st.expander("📄 Preview Extracted PDF Text"):
        st.text_area("Extracted Text", pdf_text[:2000], height=200)

    st.info("📄 Reading insurance template...")
    doc = Document(template_file)
    template_text = "\n".join([p.text for p in doc.paragraphs])

    st.info("🧠 Calling LLM to generate filled content...")
    try:
        filled_output = fill_template_with_llm(template_text, pdf_text, model_choice)
    except Exception as e:
        st.error(f"❌ LLM Error: {str(e)}")
        st.stop()

    st.success("✅ Template filled successfully!")

    filled_doc = Document()
    for line in filled_output.split("\n"):
        filled_doc.add_paragraph(line.strip())

    output_path = os.path.join(tempfile.gettempdir(), "filled_template.docx")
    filled_doc.save(output_path)

    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download Filled Template", f, file_name="filled_template.docx")
