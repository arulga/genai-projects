-- enable pgvector extension (run once per DB / if permitted)
CREATE EXTENSION IF NOT EXISTS vector;

-- documents table: we store page-level chunks
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    doc_name TEXT NOT NULL,
    page_number INT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(384), -- change dimension if using different embed model
    created_at TIMESTAMP DEFAULT now()
);

-- create an ivfflat or hnsw index depending on pgvector extension configuration
-- HNSW index example (if pgvector compiled with HNSW)
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);
-- If you have pgvector >= supports HNSW: use 'ann' or adapt as per pgvector docs
