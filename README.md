# Template--filler
# app link- 
# 📄 Insurance Template Auto-Filler (Streamlit App)

## 🧠 Objective

This Streamlit application allows users to:
- Upload an insurance claim `.docx` template
- Upload one or more `.pdf` photo reports
- Automatically extract relevant content from the PDFs
- Fill in the `.docx` template using LLM (OpenRouter API)
- Download the final filled template as a Word file

---

## 🚀 How to Run

### 1️⃣ Set Up OpenRouter API Key

> ⚠️ You must have an [OpenRouter](https://openrouter.ai) account and a valid API key.

1. Go to: https://openrouter.ai/keys  
2. Create a new API key (it will start with `sk-or-v1...`)
3. In **Streamlit Cloud**, open your app's **"Secrets"** tab
4. Add the following entry:

```toml
# .streamlit/secrets.toml (for local testing) OR use Streamlit Cloud secrets
[api]
openrouter_key = "sk-or-v1-your-api-key-here"
