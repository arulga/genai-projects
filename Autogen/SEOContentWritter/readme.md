# SEO Content Generator

AI-powered SEO content generation using multi-agent architecture.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Run Application
```bash
python -m uvicorn backend:app
streamlit run app.py
```

### 4. Open Browser

Navigate to: http://localhost:8501

## 📋 Requirements

- Python 3.9+
- OpenAI API Key
- Internet connection

## 🔧 Configuration

Edit `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini
```
