# streamlit_app.py
import streamlit as st
import os
from dotenv import load_dotenv
from rag_pipeline import embed_and_store_pdf, build_rag_answer, close
from neo4j_loader import Neo4jHelper
import tempfile
from openai import OpenAI


st.set_page_config(page_title="RAG: Neo4j + Neon Postgres", layout="wide")
st.title("RAG demo — Neo4j (KG) + Neon Postgres (Vector)")

load_dotenv()

# Initialize OpenAI client (NEW way)
@st.cache_resource
def get_openai_client():
    """Initialize and cache OpenAI client"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key)
    return None

client = get_openai_client()


# PDF Upload Section
uploaded = st.file_uploader("Upload a PDF to index", type=["pdf"])
if uploaded:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
        tmpf.write(uploaded.getvalue())
        tmp_path = tmpf.name
    
    with st.spinner("Extracting and indexing PDF (this may take a few seconds)..."):
        stored = embed_and_store_pdf(tmp_path, uploaded.name)
    
    st.success(f"✅ Indexed {len(stored)} pages. Example: {stored[:2]}")
    
    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except:
        pass

st.markdown("---")

# Question & Answer Section
st.header("Ask a question (the system will return Vector & Graph evidence)")
q = st.text_input("Question", placeholder="e.g., What is the main topic discussed in the document?")

if st.button("Search", type="primary") and q:
    with st.spinner("Searching vector DB and knowledge graph..."):
        result = build_rag_answer(q, vector_k=3, kg_entity_depth=1)

    # Vector Search Results
    st.subheader("📄 Vector Search (Top Passages)")
    if result["vector_results"]:
        for i, v in enumerate(result["vector_results"]):
            with st.expander(f"**[V{i+1}]** {v['doc_name']} — Page {v['page']}", expanded=(i==0)):
                st.write(v['text'][:1000])  # show snippet
    else:
        st.info("No vector results found.")

    # Knowledge Graph Results
    st.subheader("🔗 Knowledge Graph Evidence (Entities & Neighbors)")
    if result["kg_results"]:
        with st.expander("View KG Evidence", expanded=False):
            st.json(result["kg_results"][:10])
    else:
        st.info("_No KG evidence found for entities in the question._")

    # Context Preview
    st.subheader("📋 Assembled Context")
    with st.expander("View full context sent to LLM"):
        st.text(result["context_text"][:2000] + "\n\n[...truncated...]")

    # LLM Answer Section
    if client:
        st.subheader("🤖 AI-Generated Answer (Grounded)")
        
        # Build strict prompt
        prompt = f"""You are a helpful assistant. Answer the question using ONLY the provided sources below. 
If the answer is not found in the sources, say "I don't know" or "Not enough information".
Cite the sources by their tag (e.g. [V1], page number, or KG fact).
Do NOT hallucinate or invent facts.

QUESTION:
{q}

SOURCES:
{result["context_text"]}

KG_EVIDENCE:
{result["kg_text"]}

Answer:"""

        try:
            # ✅ NEW OpenAI API syntax
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4", "gpt-3.5-turbo"
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based only on provided context. Always cite your sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            # ✅ NEW way to access response
            answer = response.choices[0].message.content
            st.write(answer)
            
            # Show token usage
            with st.expander("📊 Token Usage"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Prompt Tokens", response.usage.prompt_tokens)
                col2.metric("Completion Tokens", response.usage.completion_tokens)
                col3.metric("Total Tokens", response.usage.total_tokens)
                
        except Exception as e:
            st.error(f"❌ Error calling OpenAI API: {e}")
            st.info("Please check your OPENAI_API_KEY in the .env file")
    else:
        st.warning("⚠️ No OPENAI_API_KEY found — you can inspect retrieved passages/KG and avoid hallucination manually.")
        st.info("Add your OpenAI API key to the .env file to enable AI-generated answers.")

# Optional: Add a cleanup button
if st.button("Clear Cache & Connections"):
    st.cache_resource.clear()
    try:
        close()
        st.success("✅ Cleared cache and closed connections")
    except:
        st.warning("Could not close connections")