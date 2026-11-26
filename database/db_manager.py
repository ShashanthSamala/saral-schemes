import sqlite3
import json
import hashlib
import os
from datetime import datetime

SCHEMA_VERSION = 1

class DatabaseManager:
    def __init__(self, db_name='database/schemes.db'):
        self.db_name = db_name
        os.makedirs(os.path.dirname(db_name), exist_ok=True)
        self.init_database()

    def _get_connection(self):
        """Get a SQLite connection with WAL mode and foreign keys for thread safety."""
        conn = sqlite3.connect(self.db_name, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init_database(self):
        """Initialize database tables and handle schema versioning / migration."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Schema version tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            ''')

            cursor.execute('SELECT version FROM schema_version')
            row = cursor.fetchone()
            current_version = row[0] if row else 0

            if current_version < SCHEMA_VERSION:
                # Migration: drop existing tables and recreate
                cursor.execute('DROP TABLE IF EXISTS scheme_content')
                cursor.execute('DROP TABLE IF EXISTS schemes')
                cursor.execute('DROP TABLE IF EXISTS translations')
                cursor.execute('DROP TABLE IF EXISTS query_log')

                # schemes table: metadata + content hash for change detection
                cursor.execute('''
                    CREATE TABLE schemes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        category TEXT,
                        url TEXT,
                        eligibility TEXT,
                        benefits TEXT,
                        content_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # scheme_content table: pre-translated / simplified multi-language text
                cursor.execute('''
                    CREATE TABLE scheme_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scheme_id INTEGER NOT NULL,
                        language TEXT NOT NULL,
                        field TEXT NOT NULL,
                        translated_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (scheme_id, language, field),
                        FOREIGN KEY (scheme_id) REFERENCES schemes (id) ON DELETE CASCADE
                    )
                ''')

                # Indexes for fast lookups (< 20ms reads)
                cursor.execute('CREATE INDEX idx_scheme_content_lookup ON scheme_content(scheme_id, language, field)')
                cursor.execute('CREATE INDEX idx_schemes_category ON schemes(category)')

                # Query log for analytics
                cursor.execute('''
                    CREATE TABLE query_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT,
                        response TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute(
                    'INSERT OR REPLACE INTO schema_version (version) VALUES (?)',
                    (SCHEMA_VERSION,)
                )
    @staticmethod
    def _compute_content_hash(scheme_dict):
        """Compute MD5 hash of scheme content for change detection."""
        content = (
            f"{scheme_dict.get('title', '')}|"
            f"{scheme_dict.get('description', '')}|"
            f"{scheme_dict.get('eligibility', '')}|"
            f"{scheme_dict.get('benefits', '')}"
        )
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def insert_scheme(self, scheme_dict):
        """Insert a single scheme record and return its new row ID."""
        content_hash = self._compute_content_hash(scheme_dict)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO schemes (title, description, category, url, eligibility, benefits, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                scheme_dict.get('title', 'N/A'),
                scheme_dict.get('description', 'N/A'),
                scheme_dict.get('category', 'N/A'),
                scheme_dict.get('url', '#'),
                scheme_dict.get('eligibility', 'N/A'),
                scheme_dict.get('benefits', 'N/A'),
                content_hash,
            ))
            conn.commit()
            return cursor.lastrowid

    def insert_schemes(self, schemes_list):
        """Bulk insert schemes, clearing existing data first. Returns count inserted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scheme_content')
            cursor.execute('DELETE FROM schemes')

            for scheme in schemes_list:
                content_hash = self._compute_content_hash(scheme)
                cursor.execute('''
                    INSERT INTO schemes (title, description, category, url, eligibility, benefits, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scheme.get('title', 'N/A'),
                    scheme.get('description', 'N/A'),
                    scheme.get('category', 'N/A'),
                    scheme.get('url', '#'),
                    scheme.get('eligibility', 'N/A'),
                    scheme.get('benefits', 'N/A'),
                    content_hash,
                ))

            conn.commit()
            return len(schemes_list)
    
    def save_content(self, scheme_id, language, field, text):
        """Save translated or simplified content to the cache."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO scheme_content (scheme_id, language, field, translated_text)
                VALUES (?, ?, ?, ?)
            ''', (scheme_id, language, field, text))
            conn.commit()

    def get_content(self, scheme_id, language, field):
        """Fetch cached translated/simplified text for a scheme field."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT translated_text FROM scheme_content
                WHERE scheme_id = ? AND language = ? AND field = ?
            ''', (scheme_id, language, field))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_schemes(self, language='en'):
        """Retrieve all schemes with optional localized content overlay."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM schemes ORDER BY category, title')
            rows = cursor.fetchall()

            schemes = []
            for row in rows:
                scheme = dict(row)
                if language and language != 'en':
                    for field in ('title', 'description', 'eligibility', 'benefits', 'simplified'):
                        cached = self.get_content(scheme['id'], language, field)
                        if cached:
                            scheme[field] = cached
                schemes.append(scheme)
            return schemes
    
    def get_translation(self, scheme_id, language, field):
        """Backward-compatible alias for get_content."""
        return self.get_content(scheme_id, language, field)

    def save_translation(self, scheme_id, language, field, text):
        """Backward-compatible alias for save_content."""
        self.save_content(scheme_id, language, field, text)

    def log_query(self, query, response):
        """Log a user query and response for analytics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO query_log (query, response) VALUES (?, ?)',
                (query, (response or '')[:500])
            )
            conn.commit()

    def get_stats(self):
        """Return database statistics for the UI dashboard."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            cursor.execute('SELECT COUNT(*) FROM schemes')
            stats['total_schemes'] = cursor.fetchone()[0]

            cursor.execute('SELECT category, COUNT(*) FROM schemes GROUP BY category')
            stats['by_category'] = dict(cursor.fetchall())

            cursor.execute('SELECT COUNT(*) FROM scheme_content')
            stats['total_translations'] = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM query_log')
            stats['total_queries'] = cursor.fetchone()[0]

            return stats


# Test database
if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE MANAGER TEST")
    print("=" * 50)

    db = DatabaseManager()

    test_scheme = {
        'title': 'PM-KISAN Scheme',
        'description': 'Income support for farmers',
        'category': 'Agriculture',
        'url': 'https://pmkisan.gov.in',
        'eligibility': 'Small and marginal farmers',
        'benefits': '₹6000 per year in 3 installments',
    }

    scheme_id = db.insert_scheme(test_scheme)
    print(f"✅ Inserted scheme with ID: {scheme_id}")

    db.save_content(scheme_id, 'hi', 'title', 'ピエム-キsan')
    cached = db.get_content(scheme_id, 'hi', 'title')
    print(f"✅ Cached translation: {cached}")

    schemes = db.get_all_schemes('en')
    print(f"✅ Retrieved {len(schemes)} schemes")

    stats = db.get_stats()
    print(f"✅ Stats: {stats}")

    print("✅ Database test completed successfully!")
