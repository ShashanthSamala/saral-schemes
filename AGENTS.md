# AGENTS.md - SARAL Schemes

## Project Overview
SARAL (Scheme Access in Regional And Local Languages) — a Streamlit web app that makes Indian government welfare schemes accessible via multi-language translation, text simplification, and an AI chatbot. Built for Smart India Hackathon 2025 (Problem Statement 25126).

## Tech Stack
- **Language:** Python 3.12
- **Framework:** Streamlit
- **AI/LLM:** Google Gemini Pro (via `google-generativeai`)
- **RAG:** Keyword-based search + Gemini generation (no vector DB)
- **Database:** SQLite
- **Scraping:** BeautifulSoup4 + Requests
- **Deployment:** Streamlit Cloud

## Run Commands
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key" > .env

# Initialize DB
python scraper/scrape_schemes.py
python database/db_manager.py

# Run
streamlit run app.py   


## What's Incomplete / TODO
- [ ] Model in code is `gemini-1.5-flash` (outdated) — update to latest available free model
- [ ] RAG is keyword-based only — no LangChain/FAISS (AGENTS.md claims it, but it's not implemented)
- [ ] `app.py` sidebar says "Coming Soon: Text simplification, AI-powered chatbot" — both already exist, remove stale text
- [ ] Verify scraper works against live government URLs
- [ ] Add deployment config for Streamlit Cloud

## Deployment Target
- **Platform:** Streamlit Cloud (free)
- **Entry point:** `app.py`
- **Secrets:** `GOOGLE_API_KEY` set in Streamlit Cloud dashboard
EOF   


