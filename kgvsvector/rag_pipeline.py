# rag_pipeline.py
import os
import fitz  # PyMuPDF
import numpy as np
import psycopg2
from psycopg2 import OperationalError, InterfaceError
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
import spacy
from neo4j_loader import Neo4jHelper
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

# Config
NEON_PG_URI = os.getenv("NEON_PG_URI")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384

# Load models (these can stay global as they don't have connection issues)
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer(EMBED_MODEL_NAME)

# CONNECTION MANAGEMENT - No global cursors!
_pg_conn = None
_neo4j = None

def get_pg_connection():
    """Get or create PostgreSQL connection with keepalive settings"""
    global _pg_conn
    
    # Check if connection exists and is open
    if _pg_conn is None or _pg_conn.closed:
        _pg_conn = psycopg2.connect(
            NEON_PG_URI,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        register_vector(_pg_conn)
    
    # Test if connection is alive
    try:
        with _pg_conn.cursor() as test_cur:
            test_cur.execute("SELECT 1")
    except (OperationalError, InterfaceError):
        # Connection is dead, reconnect
        try:
            _pg_conn.close()
        except:
            pass
        _pg_conn = psycopg2.connect(
            NEON_PG_URI,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )
        register_vector(_pg_conn)
    
    return _pg_conn

@contextmanager
def get_pg_cursor():
    """Context manager for database cursor with auto-reconnect"""
    conn = get_pg_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def get_neo4j():
    """Get or create Neo4j connection"""
    global _neo4j
    if _neo4j is None:
        _neo4j = Neo4jHelper()
    return _neo4j

# PDF PROCESSING
def extract_pages_from_pdf(file_path):
    """Extract text from each page of a PDF"""
    doc = fitz.open(file_path)
    pages = []
    for page_no in range(len(doc)):
        page = doc.load_page(page_no)
        text = page.get_text("text")
        pages.append((page_no+1, text))
    doc.close()
    return pages

def upsert_page_to_postgres(doc_name, page_no, text):
    """Insert a page into PostgreSQL with embeddings"""
    emb = embedder.encode(text).astype(float).tolist()
    sql = """
    INSERT INTO documents (doc_name, page_number, text, embedding)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
    """
    
    with get_pg_cursor() as cursor:
        cursor.execute(sql, (doc_name, page_no, text, emb))
        new_id = cursor.fetchone()[0]
    
    return new_id

def embed_and_store_pdf(file_path, doc_name):
    """Process PDF: extract text, create embeddings, store in PG and Neo4j"""
    pages = extract_pages_from_pdf(file_path)
    neo4j = get_neo4j()
    stored = []
    
    for page_no, text in pages:
        # Skip empty pages
        if not text.strip():
            continue
            
        # Store in PostgreSQL
        doc_id = upsert_page_to_postgres(doc_name, page_no, text)
        
        # Store into neo4j as page node
        neo4j.create_document_page(doc_id, doc_name, page_no, text)
        
        # Run NER and create entity nodes & mention edges
        doc_spacy = nlp(text)
        ents = set()
        for ent in doc_spacy.ents:
            ent_text = ent.text.strip()
            if ent_text:
                ents.add((ent_text, ent.label_))
        
        for ent_text, label in ents:
            neo4j.create_entity_and_rel(doc_id, page_no, ent_text, label)
        
        stored.append({"id": doc_id, "page": page_no, "text_len": len(text)})
    
    return stored

# VECTOR SEARCH — Neon (pgvector)
def vector_search(query, top_k=5):
    """Search for similar documents using vector embeddings"""
    q_emb = embedder.encode(query).astype(float).tolist()
    
    sql = """
    SELECT id, doc_name, page_number, text
    FROM documents
    ORDER BY embedding <-> %s::vector
    LIMIT %s;
    """
    
    with get_pg_cursor() as cursor:
        cursor.execute(sql, (q_emb, top_k))
        rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "doc_name": r[1],
            "page": r[2],
            "text": r[3],
        })
    return results

# KG SEARCH — Neo4j neighborhood lookup by exact entity match
def kg_search_by_entity(entity_text, depth=1):
    """Search knowledge graph for entity and its neighbors"""
    neo4j = get_neo4j()
    return neo4j.get_entity_neighbors(entity_text, depth=depth)

# Build RAG context: combine top vector passages + KG facts
def build_rag_answer(question, vector_k=4, kg_entity_depth=1):
    """Build RAG context from vector search and knowledge graph"""
    # Vector search
    vec_results = vector_search(question, top_k=vector_k)
    
    # Extract entities from question
    qdoc = nlp(question)
    q_entities = [ent.text for ent in qdoc.ents if ent.text.strip()]
    
    # Knowledge graph search
    kg_results = []
    for e in q_entities:
        try:
            kg_data = kg_search_by_entity(e, depth=kg_entity_depth)
            if kg_data:
                kg_results.extend(kg_data)
        except Exception as ex:
            print(f"KG search error for entity '{e}': {ex}")

    # Build context object with explicit source citations
    context_parts = []
    for i, v in enumerate(vec_results):
        context_parts.append(
            f"[V{i+1}] (doc:{v['doc_name']} page:{v['page']})\n{v['text']}\n---"
        )

    kg_parts = []
    for rec in kg_results:
        kg_parts.append(str(rec))

    return {
        "question": question,
        "vector_results": vec_results,
        "kg_results": kg_results,
        "context_text": "\n".join(context_parts) if context_parts else "No vector results found.",
        "kg_text": "\n".join(kg_parts) if kg_parts else "No KG results found."
    }

# Close connections when done
def close():
    """Close all database connections"""
    global _pg_conn, _neo4j
    
    if _pg_conn and not _pg_conn.closed:
        try:
            _pg_conn.close()
        except:
            pass
    
    if _neo4j:
        try:
            _neo4j.close()
        except:
            pass
        _neo4j = None