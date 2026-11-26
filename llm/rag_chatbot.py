import os
import time
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

STORE_DISPLAY_NAME = "saral-schemes-store"
PRIMARY_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODEL = "gemini-3.6-flash"

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
}


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY in environment variables.")
    return genai.Client(api_key=api_key)


def get_or_create_store(client: genai.Client) -> str:
    """Returns the existing File Search Store resource name or creates a new one."""
    for store in client.file_search_stores.list():
        if store.display_name == STORE_DISPLAY_NAME:
            return store.name

    new_store = client.file_search_stores.create(
        config={"display_name": STORE_DISPLAY_NAME}
    )
    logger.info(f"Created new File Search Store: {new_store.name}")
    return new_store.name


def sync_knowledge_base_to_store(md_file_path: str) -> bool:
    """Replaces old documents in the store with the latest saral_knowledge_base.md."""
    if not os.path.exists(md_file_path):
        logger.error(f"Knowledge base file not found: {md_file_path}")
        return False

    client = get_client()
    store_name = get_or_create_store(client)

    # Remove stale documents so outdated scheme rules are never retrieved
    for doc in client.file_search_stores.documents.list(parent=store_name):
        client.file_search_stores.documents.delete(name=doc.name)

    operation = client.file_search_stores.upload_to_file_search_store(
        file=md_file_path,
        file_search_store_name=store_name,
        config={"display_name": "SARAL Schemes Knowledge Base"},
    )

    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)

    logger.info("Successfully indexed knowledge base into Gemini File Search Store.")
    return True


def ask_rag_chatbot(user_query: str, language_code: str = "en", chat_history: list = None) -> dict:
    """
    Answers user queries strictly from the SARAL File Search Store without web search.
    Returns dict: {"answer": str, "sources": list[str]}
    """
    target_lang = LANGUAGE_MAP.get(language_code, "English")
    client = get_client()
    store_name = get_or_create_store(client)

    system_instruction = f"""
    You are the SARAL Government Scheme Assistant helping farmers, elderly citizens, and rural residents.
    
    STRICT RULES:
    1. Answer ONLY using facts retrieved from the SARAL File Search Store. NEVER use outside internet knowledge or guess.
    2. When relevant to the user's question, clearly organize your answer covering:
       - Eligibility rules (who can apply)
       - Required documents
       - How to apply (step-by-step)
       - Deadlines
       - What to do after applying (status tracking, disbursement, or grievance steps)
    3. If the answer is not found in the SARAL scheme documents, state clearly in {target_lang}: 
       "This information is not currently available in the SARAL scheme database."
    4. Write in simple, clear, 5th-grade level {target_lang} without bureaucratic jargon.
    """

    contents = []
    if chat_history:
        for turn in chat_history[-4:]:
            role = "user" if turn["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=turn["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_query)]))

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.1,
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
                )
            )
        ],
    )

    last_error = None
    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                
                sources = []
                if response.candidates and response.candidates[0].grounding_metadata:
                    chunks = response.candidates[0].grounding_metadata.grounding_chunks or []
                    for chunk in chunks:
                        if hasattr(chunk, "retrieved_context") and chunk.retrieved_context:
                            title = getattr(chunk.retrieved_context, "title", None)
                            if title and title not in sources:
                                sources.append(title)

                return {
                    "answer": response.text,
                    "sources": sources,
                }
            except Exception as e:
                last_error = e
                logger.warning(f"RAG query failed on {model_name} (attempt {attempt + 1}): {e}")
                time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"RAG Chatbot failed across fallback models: {last_error}")
