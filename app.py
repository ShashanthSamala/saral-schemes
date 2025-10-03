import streamlit as st
import os
from scraper.scrape_schemes import SchemesScraper
from database.db_manager import DatabaseManager

# Page config
st.set_page_config(
    page_title="SARAL - Scheme Access Portal",
    page_icon="🏛️",
    layout="wide"
)

# CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scheme-card {
        background: #f5f7fa;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Sidebar
with st.sidebar:
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
    
    if st.button("🔄 Load Schemes Data", use_container_width=True):
        with st.spinner("Loading schemes..."):
            try:
                scraper = SchemesScraper()
                schemes = scraper.scrape_all()
                st.session_state.db.insert_schemes(schemes)
                st.success(f"✅ Loaded {len(schemes)} schemes!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    stats = st.session_state.db.get_stats()
    st.metric("Total Schemes", stats.get('total_schemes', 0))
    
    st.markdown("---")
    st.caption("Smart India Hackathon 2025")
    st.caption("Problem Statement: 25126")

# Header
st.markdown("""
    <div class="main-header">
        <h1>🏛️ SARAL</h1>
        <p style="font-size: 1.2rem; margin: 0.5rem 0;">Scheme Access in Regional And Local Languages</p>
        <p style="font-size: 0.95rem;">सरल | సరళ | எளிய | सुलभ</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🏠 Browse Schemes", "🔍  Search", "ℹ️ About"])

# TAB 1: Browse
with tab1:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0; text-align: center;">
                📋 Available Government Schemes
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    category = st.selectbox(
        "Filter by Category",
        ["All", "Telangana State", "Central Government"]
    )
    
    all_schemes = st.session_state.db.get_all_schemes()
    
    if not all_schemes:
        st.warning("⚠️ No schemes loaded. Click 'Load Schemes Data' button in sidebar.")
        
        st.info("""
        **Quick Start:**
        1. Click the **"🔄 Load Schemes Data"** button in the sidebar
        2. Wait a few seconds for data to load
        3. Browse through available schemes
        """)
    else:
        if category != "All":
            schemes = [s for s in all_schemes if s['category'] == category]
        else:
            schemes = all_schemes
        
        st.success(f"📊 Showing **{len(schemes)}** schemes")
        
        for scheme in schemes:
            with st.expander(f"📄 {scheme['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write("**📝 Description:**")
                    st.write(scheme['description'])
                    
                    st.write("**✅ Eligibility:**")
                    st.write(scheme['eligibility'])
                    
                    st.write("**💰 Benefits:**")
                    st.write(scheme['benefits'])
                
                with col2:
                    st.write(f"**🏷️ Category:**")
                    st.write(scheme['category'])
                    
                    if scheme.get('url') and scheme['url'] != '#':
                        st.markdown(f"**🔗 [Visit Website]({scheme['url']})**")

# TAB 2: Search
with tab2:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0; text-align: center;">
                🔍 Search Government Schemes
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    query = st.text_input("🔎 Enter keywords (e.g., farmer, pension, health, education)")
    
    if query:
        results = st.session_state.db.search_schemes(query)
        st.success(f"📊 Found **{len(results)}** schemes matching '{query}'")
        
        if results:
            for scheme in results:
                st.markdown(f"""
                    <div class="scheme-card">
                        <h3>📄 {scheme['title']}</h3>
                        <p><strong>🏷️ Category:</strong> {scheme['category']}</p>
                        <p><strong>📝 Description:</strong> {scheme['description']}</p>
                        <p><strong>💰 Benefits:</strong> {scheme['benefits']}</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No schemes found. Try different keywords.")

# TAB 3: About
with tab3:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0; text-align: center;">
                ℹ️ About SARAL
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Key Features")
        st.write("✅ **Browse Government Schemes**")
        st.write("- Telangana State schemes")
        st.write("- Central Government schemes")
        st.write("")
        st.write("✅ **Smart Search**")
        st.write("- Keyword-based search")
        st.write("- Filter by category")
        st.write("")
        st.write("✅ **User-Friendly Design**")
        st.write("- Clean interface")
        st.write("- Mobile responsive")
        st.write("- Easy navigation")
        
        st.markdown("---")
        
        st.markdown("### 🛠️ Technology Stack")
        st.code("""
Frontend:  Streamlit
Backend:   Python 3.12
Database:  SQLite
Scraping:  BeautifulSoup4
Cloud:     Streamlit Cloud
        """)
    
    with col2:
        st.markdown("### 📊 Live Statistics")
        
        stats = st.session_state.db.get_stats()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("📄 Total Schemes", stats.get('total_schemes', 0))
        with col_b:
            st.metric("💬 Categories", len(stats.get('by_category', {})))
        
        st.markdown("---")
        
        st.markdown("### 🚀 Coming Soon")
        st.write("🌐 Multi-language translation")
        st.write("🔄 Text simplification")
        st.write("💬 AI-powered chatbot")
        st.write("🎤 Voice input/output")
        st.write("📱 WhatsApp integration")
    
    st.markdown("---")
    
    st.markdown("### 👥 Team Information")
    
    st.info("""
**Smart India Hackathon 2025**

**Problem Statement:** 25126 - Government Schemes Accessibility

SARAL (Scheme Access in Regional And Local Languages) is a solution that bridges the gap between government welfare schemes and the people who need them most - especially rural, elderly, and less educated citizens across India.

**Our Mission:** Making every government scheme accessible to every Indian, in their own language, in simple words they can understand.
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
**🌾 For Rural Citizens**

Simple interface  
Clear information  
Easy access  
No tech barriers
        """)
    
    with col2:
        st.info("""
**👴 For Elderly**

Large text  
Easy navigation  
Simple language  
Patient design
        """)
    
    with col3:
        st.info("""
**�� For Everyone**

100% Free  
No registration  
24/7 available  
Mobile friendly
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        <p><strong>SARAL</strong> - Scheme Access in Regional And Local Languages</p>
        <p>सरल | సరళ | எளிய | सुलभ | ಸರಳ</p>
        <p style="font-size: 0.9rem;">Smart India Hackathon 2025 | Problem Statement: 25126</p>
        <p style="font-size: 0.85rem;">Made with ❤️ for Rural India 🇮🇳</p>
    </div>
""", unsafe_allow_html=True)
