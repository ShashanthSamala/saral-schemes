import streamlit as st
import os

from database.db_manager import init_db, get_all_schemes, search_schemes, filter_by_category, get_stats
from scraper.scrape_schemes import run_sync_pipeline
from llm.rag_chatbot import ask_rag_chatbot, sync_knowledge_base_to_store

# Page Configuration
st.set_page_config(
    page_title="SARAL - Government Scheme Access",
    page_icon="🌾",
    layout="wide",
)

# Custom CSS for Rural / Farmer Accessibility (Larger touch targets, high contrast)
st.markdown("""
    <style>
    .stButton button {
        font-size: 18px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
    }
    h1, h2, h3 {
        color: #1B5E20 !important;
    }
    .scheme-card {
        background-color: #F9FBE7;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #C8E6C9;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Database on Startup
init_db()

# Header Section
st.title("SARAL: Scheme Access in Regional And Local Languages")
st.markdown("### Simple, accessible access to State and Central government welfare schemes.")

# Top-Level Language Selector (Pills)
lang_mapping = {
    "English": "en",
    "हिन्दी": "hi",
    "తెలుగు": "te",
    "தமிழ்": "ta",
    "ಕನ್ನಡ": "kn"
}
selected_lang_label = st.pills(
    "Select Language / भाषा / భాష / மொழಿ / ಭಾಷೆ",
    list(lang_mapping.keys()),
    default="English"
)
current_lang_code = lang_mapping[selected_lang_label]

# Main Navigation Tabs
tab_browse, tab_chat, tab_admin = st.tabs(["Browse Schemes", "Ask Assistant", "Admin Controls"])

# -------------------------------------------------------------------------
# TAB 1: BROWSE SCHEMES
# -------------------------------------------------------------------------
with tab_browse:
    st.header("Available Welfare Schemes")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search by keyword (e.g. farmer, pension, health, housing):")
    with col2:
        level_filter = st.selectbox("Filter Level", ["All", "Central", "State"])

    # Fetch schemes based on search or category
    if search_query:
        schemes = search_schemes(search_query, language=current_lang_code)
    else:
        schemes = get_all_schemes(language=current_lang_code)

    if level_filter != "All":
        schemes = [s for s in schemes if s.get("level", "").lower() == level_filter.lower()]

    if not schemes:
        st.info("No schemes found matching your search. Try adjusting keywords or refresh data in Admin tab.")
    else:
        st.write(f"Showing **{len(schemes)}** schemes (Language: **{selected_lang_label}**)")
        
        for scheme in schemes:
            with st.container(border=True):
                st.markdown(f"### {scheme.get('title', 'Untitled Scheme')}")
                
                badge_color = "orange" if scheme.get('level') == "Central" else "green"
                st.markdown(f"**Level:** :{badge_color}[{scheme.get('level', 'General')}] | **Category:** {scheme.get('category', 'General')}")
                
                st.markdown(f"**Overview:** {scheme.get('description', '')}")
                
                with st.expander("📖 View Full Guide (Eligibility, Documents, Application Steps)"):
                    st.markdown(f"**✅ Eligibility Rules:**\n{scheme.get('eligibility', 'N/A')}")
                    st.markdown(f"**💰 Benefits:**\n{scheme.get('benefits', 'N/A')}")
                    st.markdown(f"**📄 Required Documents:**\n{scheme.get('required_documents', 'N/A')}")
                    st.markdown(f"**📝 How to Apply:**\n{scheme.get('how_to_apply', 'N/A')}")
                    st.markdown(f"**⏳ Deadlines:**\n{scheme.get('deadlines', 'N/A')}")
                    st.markdown(f"**📌 What to Do After Applying:**\n{scheme.get('post_application_steps', 'N/A')}")
                    
                    if scheme.get('source_url'):
                        st.markdown(f"[🔗 Official Portal Link]({scheme['source_url']})")

# -------------------------------------------------------------------------
# TAB 2: ASK ASSISTANT (RAG CHATBOT)
# -------------------------------------------------------------------------
with tab_chat:
    st.header("SARAL Scheme Assistant")
    st.markdown("Ask questions about eligibility, required documents, deadlines, or what to do after applying.")

    # Quick starter suggestion buttons
    st.markdown("**Quick Questions:**")
    q_cols = st.columns(3)
    preset_query = None
    if q_cols[0].button("What schemes are for farmers?"):
        preset_query = "What schemes are available for farmers and what benefits do they get?"
    if q_cols[1].button("What documents are needed?"):
        preset_query = "What documents are required to apply for welfare schemes?"
    if q_cols[2].button("What to do after applying?"):
        preset_query = "What should I do after submitting my application and how do I track status?"

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display prior messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User chat input (or preset click)
    prompt = st.chat_input("Type your question here...") or preset_query

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Checking SARAL scheme records..."):
                try:
                    result = ask_rag_chatbot(prompt, language_code=current_lang_code, chat_history=st.session_state.messages)
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    if sources:
                        st.caption(f"📚 Sources: {', '.join(set(sources))}")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error answering your question. Please try again."
                    st.error(error_msg)

# -------------------------------------------------------------------------
# TAB 3: ADMIN CONTROLS
# -------------------------------------------------------------------------
with tab_admin:
    st.header("Administrator Control Panel")
    st.markdown("Manage scheme data synchronization and cloud RAG index updates.")

    stats = get_stats()
    col_a, col_b = st.metric("Total Schemes in Database", stats.get("total_schemes", 0)), st.metric("Categories", len(stats.get("categories", [])))

    if st.button("🔄 Refresh Data & Sync Knowledge Base", type="primary"):
        with st.spinner("Scraping government portals, updating SQLite, translating, and syncing cloud RAG store..."):
            try:
                run_sync_pipeline()
                md_path = os.path.join(os.path.dirname(__file__), "data/saral_knowledge_base.md")
                sync_knowledge_base_to_store(md_path)
                st.success("Data synchronization and RAG store indexing completed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Sync failed: {e}")
