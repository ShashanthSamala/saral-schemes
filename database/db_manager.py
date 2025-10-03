import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='database/schemes.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create schemes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                url TEXT,
                eligibility TEXT,
                benefits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create translations cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scheme_id INTEGER,
                language TEXT,
                translated_title TEXT,
                translated_description TEXT,
                translated_eligibility TEXT,
                translated_benefits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scheme_id) REFERENCES schemes (id)
            )
        ''')
        
        # Create user queries log (for analytics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def insert_schemes(self, schemes_list):
        """Insert scraped schemes into database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Clear existing data (for prototype)
        cursor.execute('DELETE FROM schemes')
        
        inserted = 0
        for scheme in schemes_list:
            cursor.execute('''
                INSERT INTO schemes (title, description, category, url, eligibility, benefits)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scheme.get('title', 'N/A'),
                scheme.get('description', 'N/A'),
                scheme.get('category', 'N/A'),
                scheme.get('url', '#'),
                scheme.get('eligibility', 'N/A'),
                scheme.get('benefits', 'N/A')
            ))
            inserted += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {inserted} schemes into database")
        return inserted
    
    def get_all_schemes(self):
        """Retrieve all schemes"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schemes ORDER BY category, title')
        rows = cursor.fetchall()
        
        schemes = [dict(row) for row in rows]
        conn.close()
        return schemes
    
    def get_scheme_by_id(self, scheme_id):
        """Get single scheme"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schemes WHERE id = ?', (scheme_id,))
        row = cursor.fetchone()
        
        scheme = dict(row) if row else None
        conn.close()
        return scheme
    
    def search_schemes(self, query):
        """Search schemes by keyword"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f'%{query}%'
        cursor.execute('''
            SELECT * FROM schemes 
            WHERE title LIKE ? 
            OR description LIKE ? 
            OR category LIKE ?
            OR eligibility LIKE ?
            OR benefits LIKE ?
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    WHEN description LIKE ? THEN 2
                    ELSE 3
                END
        ''', (search_term, search_term, search_term, search_term, search_term, search_term, search_term))
        
        rows = cursor.fetchall()
        schemes = [dict(row) for row in rows]
        conn.close()
        return schemes
    
    def filter_by_category(self, category):
        """Filter schemes by category"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schemes WHERE category = ? ORDER BY title', (category,))
        rows = cursor.fetchall()
        
        schemes = [dict(row) for row in rows]
        conn.close()
        return schemes
    
    def save_translation(self, scheme_id, language, translations):
        """Cache translations to avoid repeated API calls"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if translation already exists
        cursor.execute('''
            SELECT id FROM translations 
            WHERE scheme_id = ? AND language = ?
        ''', (scheme_id, language))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing translation
            cursor.execute('''
                UPDATE translations 
                SET translated_title = ?,
                    translated_description = ?,
                    translated_eligibility = ?,
                    translated_benefits = ?
                WHERE scheme_id = ? AND language = ?
            ''', (
                translations.get('title', ''),
                translations.get('description', ''),
                translations.get('eligibility', ''),
                translations.get('benefits', ''),
                scheme_id,
                language
            ))
        else:
            # Insert new translation
            cursor.execute('''
                INSERT INTO translations 
                (scheme_id, language, translated_title, translated_description, 
                 translated_eligibility, translated_benefits)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                scheme_id,
                language,
                translations.get('title', ''),
                translations.get('description', ''),
                translations.get('eligibility', ''),
                translations.get('benefits', '')
            ))
        
        conn.commit()
        conn.close()
    
    def get_translation(self, scheme_id, language):
        """Retrieve cached translation"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM translations 
            WHERE scheme_id = ? AND language = ?
        ''', (scheme_id, language))
        
        row = cursor.fetchone()
        translation = dict(row) if row else None
        conn.close()
        return translation
    
    def log_query(self, query, response):
        """Log user queries for analytics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_log (query, response)
            VALUES (?, ?)
        ''', (query, response[:500]))  # Limit response length
        
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total schemes
        cursor.execute('SELECT COUNT(*) FROM schemes')
        stats['total_schemes'] = cursor.fetchone()[0]
        
        # Schemes by category
        cursor.execute('SELECT category, COUNT(*) FROM schemes GROUP BY category')
        stats['by_category'] = dict(cursor.fetchall())
        
        # Total translations
        cursor.execute('SELECT COUNT(*) FROM translations')
        stats['total_translations'] = cursor.fetchone()[0]
        
        # Total queries
        cursor.execute('SELECT COUNT(*) FROM query_log')
        stats['total_queries'] = cursor.fetchone()[0]
        
        conn.close()
        return stats

# Test database
if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE MANAGER TEST")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Load scraped data
    print("\n📂 Loading scraped schemes...")
    try:
        with open('data/scraped_schemes.json', 'r', encoding='utf-8') as f:
            schemes = json.load(f)
        
        print(f"✅ Loaded {len(schemes)} schemes from JSON")
        
        # Insert into database
        print("\n💾 Inserting into database...")
        db.insert_schemes(schemes)
        
        # Get stats
        print("\n📊 Database Statistics:")
        stats = db.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Test search
        print("\n🔍 Testing search for 'farmer':")
        results = db.search_schemes('farmer')
        print(f"   Found {len(results)} results")
        if results:
            print(f"   First result: {results[0]['title']}")
        
        print("\n✅ Database test completed successfully!")
        
    except FileNotFoundError:
        print("❌ Error: Run scraper first to generate data/scraped_schemes.json")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 50)