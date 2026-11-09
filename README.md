# Multi-Agent AI Coding Learning Assistant

Agents: Orchestrator (router) · Tutor · Code Review · Debugger · Mentor · Quiz
RAG: TF-IDF retrieval over `knowledge_base/*.md` (students can upload their own notes)
LLM: Anthropic API  ·  UI: Streamlit

## Setup
1. Install Python 3.10+
2. python -m venv venv
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. pip install -r requirements.txt
5. Copy `.env.example` to `.env` and paste your API key
6. streamlit run app.py   (opens http://localhost:8501)
