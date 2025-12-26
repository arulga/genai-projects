"""Configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "seo_content.db")
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000