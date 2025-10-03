
**सरल | సరళ | எளிய | सुलभ | ಸರಳ**

> Smart India Hackathon 2025 - Problem Statement 25126

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-AI-orange?style=for-the-badge)](https://ai.google.dev/)

---

## 📖 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Features](#-features)
- [Technology Stack](#️-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Screenshots](#-screenshots)
- [Team](#-team)

---

## 🎯 Problem Statement

**Problem Statement 25126:** Government Schemes Accessibility

### The Challenge

Millions of Indians, especially in rural areas, cannot access government welfare schemes due to:

- ❌ **Language Barriers** - Content only in English
- ❌ **Complex Terminology** - Bureaucratic jargon
- ❌ **Low Awareness** - Don't know what schemes exist
- ❌ **Digital Divide** - Difficult to navigate websites

### Target Audience

- 🌾 **Rural Population** - Farmers, villagers
- 👴 **Elderly Citizens** - Senior citizens needing support
- 📚 **Less Educated** - People with limited literacy
- 🌐 **Non-English Speakers** - Regional language users

---

## 💡 Solution

**SARAL** (Scheme Access in Regional And Local Languages) is a web application that makes government schemes accessible through:

### Three Core Pillars

1. **🌐 Translation** - Convert to Hindi, Telugu, Tamil, Kannada
2. **🔄 Simplification** - Complex → Simple language
3. **🎨 Visual Appeal** - User-friendly design for rural users

---

## ✨ Features

### 1. Multi-Language Translation
- Supports 5 languages: English, Hindi, Telugu, Tamil, Kannada
- Powered by Google Gemini AI
- Real-time translation with caching
- Translation memory to reduce API calls

### 2. Smart Text Simplification
- Converts bureaucratic language to simple words
- Explanations suitable for 5th-grade reading level
- Context-aware simplification

### 3. AI-Powered Chatbot (RAG)
- Ask questions in natural language
- Context-aware responses using scheme database
- Personalized scheme recommendations
- Query history and analytics

### 4. Web Scraping
- Automatic data collection from:
  - Telangana State Government websites
  - Central Government portals
- Scheduled updates
- Fallback to curated data

### 5. Advanced Search
- Keyword-based search
- Category filtering
- Relevance-based ranking

### 6. User-Friendly Interface
- Beautiful gradient design
- Mobile responsive
- Accessible for all age groups
- Visual cards for easy browsing

---

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Python web framework
- **HTML/CSS** - Custom styling

### Backend
- **Python 3.12** - Core language
- **SQLite** - Database
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP library

### AI/ML
- **Google Gemini Pro** - LLM for translation & simplification
- **LangChain** - RAG framework
- **FAISS** - Vector database (optional)

### Deployment
- **Streamlit Cloud** - Free hosting
- **Git/GitHub** - Version control

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key (free)
- Git

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/samalashashanth/saral-schemes.git
   cd saral-schemes```

2. **Create virtual environment**
```
Bash

python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```
3. **Install dependencies**
```
Bash

pip install -r requirements.txt
```
4. **Configure API Key**
```
Bash

# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
```
5. **Initialize database**
```

Bash

python scraper/scrape_schemes.py
python database/db_manager.py
```
6. **Run application**
```
Bash

streamlit run app.py
```

📱 Usage
For End Users
1. Browse Schemes
        View all available schemes
        Filter by category (State/Central)
        Translate to your language
        Simplify complex text
2. Ask Chatbot
Type questions like:

    "What schemes are for farmers?"
    "I am 70 years old, what can I get?"
    "How much money in PM-KISAN?"
3. Search Schemes
    Enter keywords: farmer, pension, health
    Get relevant results instantly
4. Get Recommendations
    Fill your profile
    Get personalized scheme suggestions

For Administrators

1. Refresh Data

    Click "🔄 Refresh Data" in sidebar
    Updates schemes from government websites

2. View Statistics

        Total schemes
        User queries
        Translation usage


📂 Project Structure

saral-schemes/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # API keys (not in git)
├── README.md                   # This file
│
├── scraper/
│   ├── __init__.py
│   └── scrape_schemes.py      # Web scraping module
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py          # Database operations
│   └── schemes.db             # SQLite database
│
├── llm/
│   ├── __init__.py
│   ├── gemini_handler.py      # LLM integration
│   └── rag_chatbot.py         # Chatbot with RAG
│
├── utils/
│   ├── __init__.py
│   └── helpers.py             # Helper functions
│
└── data/
    └── scraped_schemes.json   # Cached schemes data


🔮 Future Enhancements


    🎤 Voice Input/Output - For illiterate users
    📱 WhatsApp Bot - Access via WhatsApp
    🖼️ Image Explanations - Visual scheme descriptions
    📍 Location-Based - Filter by user location
    🔔 Notifications - Deadline reminders
    📝 Application Forms - Fill forms with AI help
    �� Direct Apply - Submit applications online
    📊 Analytics Dashboard - Usage statistics
    🔐 User Accounts - Save favorite schemes
    📧 Email Alerts - New schemes notifications

🧪 Testing

Run Tests
```
bash 
# Test scraper
python scraper/scrape_schemes.py

# Test database
python database/db_manager.py

# Test LLM
python llm/gemini_handler.py

# Test chatbot
python llm/rag_chatbot.py
```

🤝 Contributing

Contributions are welcome! Please follow these steps:

   1. Fork the repository
   2. Create a feature branch (git checkout -b feature/AmazingFeature)
   3. Commit changes (git commit -m 'Add AmazingFeature')
   4. Push to branch (git push origin feature/AmazingFeature)
   5. Open a Pull Request

👥 Team

Smart India Hackathon 2025
Problem Statement: 25126

Team Name: HexCore

Team Members:

Team Leader - Samala Shashanth
Team Member - Konakalla Prajith Reddy
Team Member - Kandadi Shivacharan Reddy
Team Member - Merugu Srinith Reddy
Team Member - Valaboju Hamsika
Team Member - Sunkara Rithika


Mentor: Lalith
        S.R Reddy

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

    Smart India Hackathon - For the opportunity
    Google - For Gemini API
    Streamlit - For the amazing framework
    Government of India - For open data initiatives
    Telangana State Government - For scheme information
