"""
Quick setup script for database initialization.
Run this after starting Docker containers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.db_config import test_connection, get_db_cursor


def main():
    print("=" * 70)
    print("CE49X Final Project - Database Setup")
    print("=" * 70)
    print()
    
    # Test connection
    print("Testing database connection...")
    if not test_connection():
        print("\n❌ ERROR: Cannot connect to PostgreSQL database.")
        print("\nPlease ensure:")
        print("1. Docker containers are running: docker-compose up -d")
        print("2. Wait a few seconds for database to initialize")
        print("3. Check database credentials in .env file")
        return False
    
    print("✅ Database connection successful!")
    
    # Check if tables exist
    print("\nChecking database schema...")
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in cur.fetchall()]
        
        expected_tables = ['articles', 'classifications', 'cooccurrence_matrix', 
                          'temporal_trends', 'sources']
        
        missing = [t for t in expected_tables if t not in tables]
        
        if missing:
            print(f"⚠️  Missing tables: {', '.join(missing)}")
            print("   Database schema may not be initialized.")
            print("   Check docker-compose.yml and database/init.sql")
        else:
            print("✅ All required tables exist")
    
    # Show statistics
    print("\nDatabase Statistics:")
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM articles")
        article_count = cur.fetchone()['count']
        print(f"  Articles: {article_count}")
        
        cur.execute("SELECT COUNT(*) as count FROM classifications")
        class_count = cur.fetchone()['count']
        print(f"  Classifications: {class_count}")
        
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM classifications 
            WHERE array_length(ce_areas, 1) > 0 
              AND array_length(ai_technologies, 1) > 0
        """)
        both_count = cur.fetchone()['count']
        print(f"  Articles with both CE and AI: {both_count}")
    
    print("\n" + "=" * 70)
    print("Setup complete! You can now:")
    print("  - Run: python scripts/migrate_to_postgres.py (to migrate existing data)")
    print("  - Run: python scripts/classify_with_llm.py (to classify articles)")
    print("  - Run: python scripts/analyze_from_db.py (to generate analysis)")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

