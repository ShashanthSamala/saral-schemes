import streamlit as st
import os
from scraper.scrape_schemes import SchemesScraper
from database.db_manager import DatabaseManager
from llm.gemini_handler import GeminiHandler
from llm.rag_chatbot import RAGChatbot
import streamlit.components.v1 as components

# Handle environment variables for Streamlit Cloud
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SARAL - Telangana",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #f0f0f0;
        margin: 0.5rem 0 0 0;
    }
    .scheme-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .scheme-card:hover {
        transform: translateX(5px);
    }
    .scheme-title {
        color: #2d3748;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .scheme-category {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    .info-box {
        background: #e6fffa;
        border-left: 4px solid #38b2ac;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fffaf0;
        border-left: 4px solid #ed8936;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #48bb78;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        color: #718096;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    
    if 'llm' not in st.session_state:
        try:
            st.session_state.llm = GeminiHandler()
            st.session_state.llm_available = True
        except Exception as e:
            st.session_state.llm_available = False
            st.session_state.llm_error = str(e)
    
    if 'chatbot' not in st.session_state:
        schemes = st.session_state.db.get_all_schemes()
        if schemes and st.session_state.get('llm_available', False):
            try:
                st.session_state.chatbot = RAGChatbot(schemes)
            except:
                st.session_state.chatbot = None
    
    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

initialize_session_state()

# Sidebar
with st.sidebar:
    # SARAL Logo Box
    st.markdown("""
    <div style="text-align: center; padding: 1rem; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 8px; color: white; margin-bottom: 1rem;">
        <h2 style="margin: 0; color: white;">सरल</h2>
        <p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: #f0f0f0;">SARAL</p>
        <p style="margin: 0.25rem 0 0 0; font-size: 0.7rem; color: #e0e0e0;">
            Scheme Access in Regional<br>And Local Languages
        </p>
    </div>
""", unsafe_allow_html=True)
    st.markdown("---")
    
    # Language selector
    st.markdown("### 🌐 Language / भाषा")
    language = st.selectbox(
        "Select your preferred language",
        ["English", "Hindi", "Telugu", "Tamil", "Kannada"],
        key='lang_select',
        label_visibility="collapsed"
    )
    st.session_state.language = language
    
    st.markdown("---")
    
    # Data management
    st.markdown("### 📊 Data Management")
    
    if st.button("🔄 Refresh Schemes Data", use_container_width=True):
        with st.spinner("Fetching latest schemes..."):
            try:
                scraper = SchemesScraper()
                schemes = scraper.scrape_all()
                st.session_state.db.insert_schemes(schemes)
                
                # Reinitialize chatbot
                if st.session_state.get('llm_available', False):
                    st.session_state.chatbot = RAGChatbot(schemes)
                
                st.success(f"✅ Updated {len(schemes)} schemes!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Statistics
    st.markdown("### 📈 Statistics")
    stats = st.session_state.db.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Schemes", stats.get('total_schemes', 0))
    with col2:
        st.metric("Queries", stats.get('total_queries', 0))
    
    # Category breakdown
    if stats.get('by_category'):
        st.markdown("**By Category:**")
        for cat, count in stats['by_category'].items():
            st.write(f"• {cat}: {count}")
    
    st.markdown("---")
    
    # API Status
    st.markdown("### ⚙️ System Status")
    if st.session_state.get('llm_available', False):
        st.success("✅ AI Translation: Active")
    else:
        st.warning("⚠️ AI: Limited Mode")
    
    st.markdown("---")
    st.caption("**Smart India Hackathon 2025**")
    st.caption("Problem Statement: 25126")
    st.caption("Made with ❤️ for Rural India")

# Main header
st.markdown("""
    <div class="main-header">
        <h1>🏛️ SARAL</h1>
        <p>सरकारी योजनाएं | ప్రభుత్వ పథకాలు | அரசு திட்டங்கள்</p>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Making Government Schemes Accessible to Everyone
        </p>
    </div>
""", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Browse Schemes", 
    "💬 Ask Assistant", 
    "🔍 Search", 
    "📊 My Profile",
    "ℹ️ About"
])

# ===== TAB 1: Browse Schemes =====
with tab1:
    st.markdown("## 📋 Available Government Schemes")
    
    # Filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All Categories", "Telangana State", "Central Government"],
            key='category_filter'
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Name (A-Z)", "Category"],
            key='sort_filter'
        )
    
    # Get schemes
    all_schemes = st.session_state.db.get_all_schemes()
    
    if not all_schemes:
        st.markdown("""
            <div class="warning-box">
                <h3>⚠️ No schemes found</h3>
                <p>Click "Refresh Schemes Data" in the sidebar to load schemes.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Filter schemes
        if category_filter != "All Categories":
            filtered_schemes = [s for s in all_schemes if s['category'] == category_filter]
        else:
            filtered_schemes = all_schemes
        
        # Sort schemes
        if sort_by == "Name (A-Z)":
            filtered_schemes.sort(key=lambda x: x['title'])
        else:
            filtered_schemes.sort(key=lambda x: x['category'])
        
        st.markdown(f"**Showing {len(filtered_schemes)} schemes**")
        st.markdown("---")
        
        # Display schemes
        for scheme in filtered_schemes:
            with st.expander(f"📄 {scheme['title']}", expanded=False):
                # Category badge
                st.markdown(f'<span class="scheme-category">{scheme["category"]}</span>', 
                           unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Translation handling
                    if st.session_state.language != 'English' and st.session_state.get('llm_available', False):
                        # Check cache
                        cached = st.session_state.db.get_translation(
                            scheme['id'], 
                            st.session_state.language
                        )
                        
                        if cached:
                            display_scheme = {
                                'description': cached['translated_description'],
                                'eligibility': cached['translated_eligibility'],
                                'benefits': cached['translated_benefits']
                            }
                        else:
                            # Translate
                            translate_btn = st.button(
                                f"🌐 Translate to {st.session_state.language}",
                                key=f"trans_{scheme['id']}"
                            )
                            
                            if translate_btn:
                                with st.spinner("Translating..."):
                                    translated = st.session_state.llm.translate_scheme(
                                        scheme, 
                                        st.session_state.language
                                    )
                                    st.session_state.db.save_translation(
                                        scheme['id'],
                                        st.session_state.language,
                                        translated
                                    )
                                    st.rerun()
                            
                            display_scheme = scheme
                    else:
                        display_scheme = scheme
                    
                    # Display content
                    st.markdown(f"**📝 Description:**")
                    st.write(display_scheme.get('description', scheme['description']))
                    
                    st.markdown(f"**✅ Eligibility:**")
                    st.write(display_scheme.get('eligibility', scheme['eligibility']))
                    
                    st.markdown(f"**💰 Benefits:**")
                    st.write(display_scheme.get('benefits', scheme['benefits']))
                    
                    # Simplification
                    if st.session_state.get('llm_available', False):
                        if st.checkbox("🔄 Show Simplified Explanation", key=f"simp_{scheme['id']}"):
                            with st.spinner("Simplifying..."):
                                simplified = st.session_state.llm.generate_simple_explanation(scheme)
                                st.markdown(f"""
                                    <div class="info-box">
                                        <strong>📖 Simple Explanation:</strong><br>
                                        {simplified}
                                    </div>
                                """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**🏷️ Category:**")
                    st.write(scheme['category'])
                    
                    if scheme.get('url') and scheme['url'] != '#':
                        st.link_button("🔗 Official Website", scheme['url'], use_container_width=True)
                    
                    # Quick actions
                    if st.button("💾 Save", key=f"save_{scheme['id']}", use_container_width=True):
                        st.success("Saved to your profile!")

# ===== TAB 2: Chatbot =====
with tab2:
    st.markdown("## 💬 AI Assistant - Ask About Schemes")
    
    if not st.session_state.get('llm_available', False):
        st.markdown("""
            <div class="warning-box">
                <h3>⚠️ AI Assistant Unavailable</h3>
                <p>Please configure GOOGLE_API_KEY in .env file to enable the chatbot.</p>
                <p>Error: {}</p>
            </div>
        """.format(st.session_state.get('llm_error', 'Unknown error')), unsafe_allow_html=True)
    else:
        # Sample questions
        st.markdown("""
    <div style="background: #764ba2; 
                color: white; 
                padding: 1rem; 
                border-radius: 8px; 
                margin: 1rem 0;
                border-left: 5px solid #667eea;">
        <strong>💡 Try asking:</strong><br>
        • "What schemes are available for farmers?"<br>
        • "I am 70 years old, what can I get?"<br>
        • "Tell me about pension schemes"<br>
        • "How much money can I get from Rythu Bandhu?"
    </div>
""", unsafe_allow_html=True)
        # Quick question buttons
        st.markdown("### 🎯 Quick Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👨‍🌾 Farmer Schemes", use_container_width=True):
                st.session_state.quick_question = "What schemes are available for farmers?"
        
        with col2:
            if st.button("👴 Senior Citizen", use_container_width=True):
                st.session_state.quick_question = "What schemes are for elderly people?"
        
        with col3:
            if st.button("💰 Financial Aid", use_container_width=True):
                st.session_state.quick_question = "Which schemes give direct money?"
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("### 💭 Chat")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.chat_message("user", avatar="👤").write(message['content'])
            else:
                st.chat_message("assistant", avatar="🤖").write(message['content'])
        
        # Handle quick question
        if 'quick_question' in st.session_state:
            user_input = st.session_state.quick_question
            del st.session_state.quick_question
        else:
            user_input = st.chat_input("Type your question here...")
        
        if user_input:
            # Add user message
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            st.chat_message("user", avatar="👤").write(user_input)
            
            # Get bot response
            with st.spinner("🤔 Thinking..."):
                if st.session_state.chatbot:
                    response = st.session_state.chatbot.chat(user_input)
                    
                    # Log query
                    st.session_state.db.log_query(user_input, response)
                else:
                    response = "Sorry, the chatbot is not available. Please refresh the schemes data."
                
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.chat_message("assistant", avatar="🤖").write(response)
            
            st.rerun()
        
        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()

# ===== TAB 3: Search =====
with tab3:
    st.markdown("## 🔍 Search Schemes")
    
    search_query = st.text_input(
        "Enter keywords (e.g., farmer, pension, health, education)",
        placeholder="Type keywords to search...",
        key='search_input'
    )
    
    if search_query:
        results = st.session_state.db.search_schemes(search_query)
        
        st.markdown(f"### Found {len(results)} schemes matching '{search_query}'")
        st.markdown("---")
        
        if results:
            for scheme in results:
                st.markdown(f"""
                    <div class="scheme-card">
                        <div class="scheme-title">📄 {scheme['title']}</div>
                        <span class="scheme-category">{scheme['category']}</span>
                        <p style="margin-top: 1rem;"><strong>Description:</strong> {scheme['description']}</p>
                        <p><strong>Benefits:</strong> {scheme['benefits']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📖 View Details", key=f"view_{scheme['id']}"):
                        st.info("Switch to 'Browse Schemes' tab to see full details")
                with col2:
                    if scheme.get('url') and scheme['url'] != '#':
                        st.markdown(f"[🔗 Official Link]({scheme['url']})")                
                
        else:
            st.markdown("""
                <div class="warning-box">
                    <h3>😕 No results found</h3>
                    <p>Try different keywords or browse all schemes in the 'Browse Schemes' tab.</p>
                </div>
            """, unsafe_allow_html=True)

# ===== TAB 4: Profile =====
# TAB 4: About
with tab4:
    st.markdown("## ℹ️ About SARAL")
    
    # Project intro
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0;">🏛️ SARAL</h2>
            <h3 style="color: #f0f0f0; margin: 0.5rem 0; font-weight: normal;">
                Scheme Access in Regional And Local Languages
            </h3>
            <p style="margin: 1rem 0 0 0; font-size: 1.1rem;">
                सरल | సరళ | எளிய | सुलभ | ಸರಳ
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Key Features
        
        **1. 🌐 Multi-Language Translation**
        - Hindi, Telugu, Tamil, Kannada
        - Powered by Google Gemini AI
        - Real-time translation
        
        **2. 🔄 Smart Simplification**
        - Complex → Simple language
        - Designed for rural users
        - Easy to understand
        
        **3. 💬 AI-Powered Chatbot**
        - Natural language queries
        - Context-aware responses
        - Personalized recommendations
        
        **4. 🎨 User-Friendly Design**
        - Visual appeal for all
        - Mobile responsive
        - Accessible interface
        
        ### 🛠️ Technology Stack
        ```
        Frontend:    Streamlit
        Backend:     Python 3.12
        Database:    SQLite
        AI/LLM:      Google Gemini Pro
        Scraping:    BeautifulSoup4
        Cloud:       Streamlit Cloud
        ```
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Impact Statistics
        """)
        
        stats = st.session_state.db.get_stats()
        
        st.metric("📄 Total Schemes", stats.get('total_schemes', 0))
        st.metric("💬 User Queries", stats.get('total_queries', 0))
        st.metric("🌐 Translations", stats.get('total_translations', 0))
        st.metric("🗣️ Languages", "5")
        
        st.markdown("---")
        
        st.markdown("""
        ### 🚀 Future Enhancements
        - 🎤 Voice input/output
        - 📱 WhatsApp integration
        - 🖼️ Image-based explanations
        - 📍 Location-based filtering
        - 🔔 Deadline notifications
        - 📝 Application assistance
        """)
    
    st.markdown("---")
    
    # Team Information
    
        # Team Information with styled box
    st.components.v1.html("""
        <div style="background: linear-gradient(135deg, #f7fafc 0%, #e6f2ff 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    border-left: 5px solid #667eea; 
                    margin: 2rem 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="color: #2d3748; margin-top: 0; font-family: sans-serif;">👥 Team Information</h3>
            
            <p style="font-size: 1.1rem; margin: 1rem 0; color: #2d3748; font-family: sans-serif;">
                <strong>Smart India Hackathon 2025</strong><br>
                <strong>Problem Statement:</strong> 25126 - Government Schemes Accessibility
            </p>
            
            <p style="color: #4a5568; line-height: 1.8; font-family: sans-serif;">
                SARAL (Scheme Access in Regional And Local Languages) demonstrates how 
                technology can bridge the gap between government welfare schemes and the 
                people who need them most - especially rural, elderly, and less educated 
                citizens across India.
            </p>
            
            <p style="color: #4a5568; margin-top: 1rem; font-family: sans-serif;">
                <strong>Mission:</strong> Making every government scheme accessible to every Indian, 
                in their own language, in simple words they can understand.
            </p>
        </div>
    """, height=300)
           
    # Features showcase
    st.markdown("### 🌟 Why SARAL?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **🎯 For Rural Citizens**
            - Simple language
            - Local languages
            - Visual interface
        """)
    
    with col2:
        st.markdown("""
            **👴 For Elderly**
            - Large text
            - Easy navigation
            - Voice support (coming)
        """)
    
    with col3:
        st.markdown("""
            **📚 For Everyone**
            - Free to use
            - No registration
            - Always available
        """)
# ===== TAB 5: About =====
with tab5:
    st.markdown("## ℹ️ About This Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            ### 🎯 Project Goals
            
            This portal aims to make government schemes accessible to everyone, especially:
            
            - **🌾 Rural Population** - Farmers, villagers
            - **👴 Elderly Citizens** - Senior citizens needing support
            - **📚 Less Educated** - People who struggle with complex language
            - **🌐 Non-English Speakers** - Regional language users
            
            ### ✨ Key Features
            
            1. **🌐 Multi-Language Translation**
               - Translate schemes to Hindi, Telugu, Tamil, Kannada
               - Uses Google Gemini AI for accurate translation
            
            2. **🔄 Text Simplification**
               - Convert complex government language
               - Simple explanations anyone can understand
            
            3. **💬 AI Chatbot**
               - Ask questions in natural language
               - Get instant answers about schemes
               - Personalized recommendations
            
            4. **🎨 Visual Design**
               - Clean, colorful interface
               - Easy navigation for everyone
               - Mobile-friendly design
        """)
    
    with col2:
        st.markdown("""
            ### 🛠️ Technology Stack
            
            ```
            Frontend:    Streamlit
            Backend:     Python 3.x
            Database:    SQLite
            AI/LLM:      Google Gemini Pro
            Scraping:    BeautifulSoup4
            Deployment:  Streamlit Cloud
            ```
            
            ### 📊 Data Flow
            
            ```
            Government Websites
                    ↓
            [Web Scraping]
                    ↓
            SQLite Database
                    ↓
            [AI Processing]
            - Translation
            - Simplification
            - Question Answering
                    ↓
            Streamlit UI
                    ↓
            Users (Rural India)
            ```
            
            ### 🚀 Future Enhancements
            
            - 🎤 Voice input/output for illiterate users
            - 📱 WhatsApp bot integration
            - 🖼️ Image-based scheme explanations
            - 📍 Location-based scheme filtering
            - 🔔 Scheme deadline notifications
            - 📝 Application form assistance
            - 🏦 Direct application submission
        """)
    
    st.markdown("---")
    
    # Team section
    st.markdown("### 👥 Team Information")
    st.markdown("""
        **Smart India Hackathon 2025**  
        **Problem Statement:** 1426 - Government Schemes Accessibility
        
        This prototype demonstrates how technology can bridge the gap between 
        government welfare schemes and the people who need them most.
    """)
    
    # Statistics
    st.markdown("### 📈 Impact Statistics")
    stats = st.session_state.db.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_schemes', 0)}</div>
                <div class="stat-label">Total Schemes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_queries', 0)}</div>
                <div class="stat-label">User Queries</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_translations', 0)}</div>
                <div class="stat-label">Translations</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">5</div>
                <div class="stat-label">Languages</div>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #718096; padding: 2rem;">
        <p>🏛️ <strong>SARAL</strong> | Smart India Hackathon 2025</p>
        <p>Making Government Schemes Accessible to Every Indian 🇮🇳</p>
        <p style="font-size: 0.85rem;">Built with ❤️ using Streamlit & Google Gemini AI</p>
    </div>
""", unsafe_allow_html=True)
