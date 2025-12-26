"""Database operations"""
import sqlite3
import json
from typing import Dict
from config import Config

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            topic TEXT,
            target_seo_score REAL,
            generated_content TEXT,
            achieved_seo_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_session(session_data: Dict):
    """Save session data"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO content_sessions 
        (session_id, topic, target_seo_score, generated_content, achieved_seo_score)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_data['session_id'],
        session_data['topic'],
        session_data['target_seo_score'],
        session_data.get('generated_content', ''),
        session_data.get('achieved_seo_score', 0.0)
    ))
    
    conn.commit()
    conn.close()