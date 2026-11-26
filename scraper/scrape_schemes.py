import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from database.db_manager import DatabaseManager
from llm.gemini_handler import GeminiHandler, LocalizedSchemeFields

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TARGET_LANGUAGES = ["hi", "te", "ta", "kn"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FALLBACK_PATH = DATA_DIR / "fallback_schemes.json"
KNOWLEDGE_BASE_PATH = DATA_DIR / "saral_knowledge_base.md"


# ---------------------------------------------------------------------------
# Modular scrapers
# ---------------------------------------------------------------------------

def scrape_state_schemes() -> list:
    """Scrapes Telangana state welfare schemes (or falls back gracefully)."""
    schemes = []
    try:
        url = "https://rythubharosa.telangana.gov.in/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Parse scheme cards/titles dynamically here if accessible
            # Placeholder for live parsing logic
            pass
    except Exception as e:
        logger.warning(f"State portal scrape failed: {e}. Will use fallback data.")
    return schemes


def scrape_central_schemes() -> list:
    """Scrapes national welfare portals (or falls back gracefully)."""
    schemes = []
    try:
        url = "https://pmkisan.gov.in/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Parse national portals here
            pass
    except Exception as e:
        logger.warning(f"Central portal scrape failed: {e}. Will use fallback data.")
    return schemes


# ---------------------------------------------------------------------------
# Fallback data
# ---------------------------------------------------------------------------

def load_fallback_schemes() -> list:
    """Load curated fallback schemes from JSON file, or return built-in defaults."""
    if FALLBACK_PATH.exists():
        try:
            with open(FALLBACK_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} fallback schemes from {FALLBACK_PATH}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load fallback JSON: {e}. Using built-in defaults.")

    # Built-in defaults if JSON file is missing or invalid
    return [
        {
            "title": "PM-KISAN Samman Nidhi",
            "level": "Central",
            "category": "Agriculture",
            "description": "Income support of Rs. 6,000 per year in three equal installments to all landholding farmer families.",
            "eligibility": "All landholding farmers with cultivable land ownership.",
            "benefits": "Rs. 6,000 per year paid directly to bank accounts.",
            "required_documents": "Aadhaar card, land ownership papers, bank passbook, mobile number.",
            "how_to_apply": "Register online via PM-KISAN portal or through local Common Service Centers (CSC).",
            "deadlines": "Open year-round for new enrollments.",
            "post_application_steps": "Check beneficiary status using Aadhaar or mobile number on the official portal. Contact district agriculture officer if delayed.",
            "source_url": "https://pmkisan.gov.in/",
        },
        {
            "title": "Telangana Rythu Bharosa",
            "level": "State",
            "category": "Agriculture",
            "description": "Investment support scheme for farmers to cover agricultural input costs.",
            "eligibility": "Resident farmers of Telangana owning cultivable agricultural land.",
            "benefits": "Financial assistance per acre per crop season.",
            "required_documents": "Pattedar Passbook, Aadhaar card, bank account details.",
            "how_to_apply": "Applications processed through state agriculture department records and Rythu Vedikas.",
            "deadlines": "Announced seasonally before crop sowing periods.",
            "post_application_steps": "Verify fund credit in linked bank account during disbursement windows.",
            "source_url": "https://rythubharosa.telangana.gov.in/",
        },
        {
            "title": "PM Awas Yojana - Gramin",
            "level": "Central",
            "category": "Housing",
            "description": "Housing for all in rural areas - Financial assistance to construct pucca houses with basic amenities.",
            "eligibility": "Homeless families and families living in kutcha houses in rural areas.",
            "benefits": "Rs. 1.20 lakh in plain areas, Rs. 1.30 lakh in hilly areas for house construction.",
            "required_documents": "Aadhaar card, BPL certificate, land ownership document, bank account.",
            "how_to_apply": "Apply through Gram Panchayat or online via PMAY-G portal.",
            "deadlines": "Varies by state; check local block office.",
            "post_application_steps": "Track application status on PMAY-G portal using registration ID.",
            "source_url": "https://pmayg.nic.in/",
        },
        {
            "title": "Pradhan Mantri Ujjwala Yojana",
            "level": "Central",
            "category": "Energy",
            "description": "Free LPG connections to women from BPL families for clean cooking fuel.",
            "eligibility": "Women from BPL families, PMAY, AAY beneficiaries.",
            "benefits": "Free LPG connection with deposit-free cylinder and stove.",
            "required_documents": "BPL ration card, Aadhaar, bank account, age proof.",
            "how_to_apply": "Apply online at pmuy.gov.in or at nearest LPG distributor.",
            "deadlines": "Open year-round.",
            "post_application_steps": "Wait for LPG connection delivery; track via distributor.",
            "source_url": "https://pmuy.gov.in/",
        },
        {
            "title": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana",
            "level": "Central",
            "category": "Health",
            "description": "Health cover of Rs. 5 lakh per family per year for secondary and tertiary care hospitalization.",
            "eligibility": "Poor and vulnerable families as per SECC 2011 database.",
            "benefits": "Cashless treatment up to Rs. 5 lakh per family per year.",
            "required_documents": "Ration card, Aadhaar, age proof, caste certificate if applicable.",
            "how_to_apply": "Check eligibility on mera.pmjay.gov.in or visit nearest empanelled hospital.",
            "deadlines": "Enrollment is continuous.",
            "post_application_steps": "Get Ayushman card; use at empanelled hospitals for cashless care.",
            "source_url": "https://www.pmjay.gov.in/",
        },
        {
            "title": "National Pension Scheme",
            "level": "Central",
            "category": "Pension",
            "description": "NPS - Pension scheme for all citizens to provide retirement income and old age security.",
            "eligibility": "All Indian citizens aged 18-70 years.",
            "benefits": "Tax benefits + pension after 60 years + flexible investment options.",
            "required_documents": "Aadhaar, PAN, bank account, photograph.",
            "how_to_apply": "Register through Point of Presence (PoP) or eNPS portal.",
            "deadlines": "No deadline; open throughout the year.",
            "post_application_steps": "Receive PRAN card; make regular contributions.",
            "source_url": "https://www.npscra.nsdl.co.in/",
        },
        {
            "title": "Pradhan Mantri Mudra Yojana",
            "level": "Central",
            "category": "Employment",
            "description": "MUDRA loans for small businesses and entrepreneurs to promote self-employment.",
            "eligibility": "Small businesses, micro-enterprises, street vendors, artisans.",
            "benefits": "Loans up to Rs. 10 lakh without collateral at low interest rates.",
            "required_documents": "Aadhaar, business proof, bank statement, photograph.",
            "how_to_apply": "Apply at any bank branch or online via Mudra portal.",
            "deadlines": "Open year-round.",
            "post_application_steps": "Track loan status; repay in EMIs.",
            "source_url": "https://www.mudra.org.in/",
        },
        {
            "title": "Telangana Aasara Pensions",
            "level": "State",
            "category": "Pension",
            "description": "Monthly pension for elderly, widows, weavers, toddy tappers, and other vulnerable groups.",
            "eligibility": "Telangana residents meeting age/income criteria for each category.",
            "benefits": "Monthly pension credited directly to bank account.",
            "required_documents": "Aadhaar, age certificate, income certificate, bank passbook.",
            "how_to_apply": "Apply through MeeSeva centers or online via TS ePass portal.",
            "deadlines": "Applications accepted year-round.",
            "post_application_steps": "Check pension status via TS ePass portal.",
            "source_url": "https://epass.telangana.gov.in/",
        },
    ]


# ---------------------------------------------------------------------------
# Knowledge base generator
# ---------------------------------------------------------------------------

def generate_knowledge_base_markdown(db: DatabaseManager):
    """Compiles all English schemes from SQLite into a Markdown file for RAG."""
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes ORDER BY category, title")
        rows = cursor.fetchall()

    md_lines = ["# SARAL Government Schemes Knowledge Base\n"]
    md_lines.append(f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

    for row in rows:
        r = dict(row)
        md_lines.append(f"## Scheme: {r['title']}\n")
        md_lines.append(f"- **Category:** {r.get('category', 'N/A')}\n")
        md_lines.append(f"- **Source URL:** {r.get('url', 'N/A')}\n")
        md_lines.append(f"- **Description:** {r.get('description', 'N/A')}\n")
        md_lines.append(f"- **Eligibility:** {r.get('eligibility', 'N/A')}\n")
        md_lines.append(f"- **Benefits:** {r.get('benefits', 'N/A')}\n")
        md_lines.append(f"- **Required Documents:** {r.get('required_documents', 'N/A')}\n")
        md_lines.append(f"- **How to Apply:** {r.get('how_to_apply', 'N/A')}\n")
        md_lines.append(f"- **Deadlines:** {r.get('deadlines', 'N/A')}\n")
        md_lines.append(f"- **After Applying:** {r.get('post_application_steps', 'N/A')}\n")
        md_lines.append("")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(KNOWLEDGE_BASE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info(f"Generated {KNOWLEDGE_BASE_PATH} with {len(rows)} schemes")


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def sync_schemes():
    """Main pipeline: scrape/load schemes, upsert into SQLite, translate new/changed ones."""
    logger.info("Starting SARAL scheme synchronization pipeline...")

    # 1. Gather live or fallback schemes
    schemes = scrape_state_schemes() + scrape_central_schemes()
    if not schemes:
        logger.info("No live schemes scraped. Loading curated fallback schemes.")
        schemes = load_fallback_schemes()

    logger.info(f"Processing {len(schemes)} schemes...")

    # 2. Upsert and translate
    db = DatabaseManager()
    gemini = GeminiHandler()

    new_or_changed = 0
    skipped = 0

    for scheme in schemes:
        scheme_id = db.upsert_scheme(scheme)

        # Check if this scheme already has translations in scheme_content
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM scheme_content WHERE scheme_id = ?",
                (scheme_id,),
            )
            count = cursor.fetchone()[0]

        if count == 0:
            new_or_changed += 1
            logger.info(f"Translating new/changed scheme ID {scheme_id}: {scheme['title']}")
            for lang in TARGET_LANGUAGES:
                try:
                    translated_fields = gemini.translate_and_simplify_scheme(scheme, lang)
                    for field_name, text in translated_fields.items():
                        db.save_content(scheme_id, lang, field_name, text)
                    time.sleep(1)  # be gentle with the API between languages
                except Exception as e:
                    logger.error(f"Failed translation for '{scheme['title']}' in {lang}: {e}")
        else:
            skipped += 1

    logger.info(f"Translated {new_or_changed} new/changed schemes; {skipped} already cached.")

    # 3. Generate Markdown knowledge base for RAG
    generate_knowledge_base_markdown(db)

    logger.info("Sync pipeline complete.")
    return new_or_changed, skipped


# Alias for app.py compatibility
run_sync_pipeline = sync_schemes


# ---------------------------------------------------------------------------
# Backward-compatible SchemesScraper class (kept for app.py compatibility)
# ---------------------------------------------------------------------------

class SchemesScraper:
    """Wrapper around sync_schemes() preserving the old class interface used by app.py."""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_telangana_schemes(self):
        return scrape_state_schemes()

    def scrape_central_schemes(self):
        return scrape_central_schemes()

    def scrape_all(self):
        """Scrape all schemes, upsert to DB, translate, and save JSON + Markdown."""
        new, skipped = sync_schemes()
        # Save combined list to JSON for compatibility
        all_schemes = scrape_state_schemes() + scrape_central_schemes()
        if not all_schemes:
            all_schemes = load_fallback_schemes()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DATA_DIR / "scraped_schemes.json", "w", encoding="utf-8") as f:
            json.dump(all_schemes, f, indent=2, ensure_ascii=False)
        logger.info(f"Pipeline done. New/changed: {new}, Skipped (cached): {skipped}")
        return all_schemes


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    new, skipped = sync_schemes()
    print(f"\n{'=' * 50}")
    print("SARAL SYNC PIPELINE COMPLETE")
    print(f"{'=' * 50}")
    print(f"New/changed schemes translated: {new}")
    print(f"Schemes already cached:         {skipped}")
    print(f"Knowledge base:                 {KNOWLEDGE_BASE_PATH}")
    print(f"{'=' * 50}\n")
