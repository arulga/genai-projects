"""
streamlit_chatbot_from_documents (app.py)

Instructions:
1. Install dependencies:
   pip install streamlit openai pdfplumber python-docx python-pptx numpy

2. Set your OpenAI API key in environment:
   On Linux / macOS:
     export OPENAI_API_KEY="sk-..."
   On Windows (PowerShell):
     $env:OPENAI_API_KEY="sk-..."

3. Run:
   streamlit run app.py

Notes:
- This example uses OpenAI embeddings and Chat Completion (gpt-3.5-turbo by default).
- Adjust MODEL_* names and threshold as you prefer.
- If you want persistent vector stores across restarts, swap in FAISS or a DB.
"""

----------------------------

chatbot loc
--------------

pip install streamlit sentence-transformers pdfplumber python-docx python-pptx numpy