"""
Migration script to move data from CSV/SQLite to PostgreSQL.
"""

import os
import sys
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = PROJECT_ROOT / "data_raw"


def migrate_from_sqlite():
    """Migrate data from SQLite to PostgreSQL."""
    sqlite_path = DATA_DIR / "articles.sqlite"
    
    if not sqlite_path.exists():
        print(f"SQLite file not found: {sqlite_path}")
        return 0
    
    print(f"Reading from SQLite: {sqlite_path}")
    conn_sqlite = sqlite3.connect(sqlite_path)
    
    try:
        df = pd.read_sql_query("SELECT * FROM articles", conn_sqlite)
        print(f"Found {len(df)} articles in SQLite")
    except Exception as e:
        print(f"Error reading SQLite: {e}")
        return 0
    finally:
        conn_sqlite.close()
    
    return migrate_dataframe(df, source="sqlite")


def migrate_from_csv():
    """Migrate data from CSV files to PostgreSQL."""
    csv_files = [
        DATA_DIR / "articles.csv",
        DATA_RAW_DIR / "newsapi_articles.csv",
        DATA_DIR / "classified_articles.csv"
    ]
    
    total_migrated = 0
    
    for csv_path in csv_files:
        if not csv_path.exists():
            print(f"CSV file not found: {csv_path}")
            continue
        
        print(f"\nReading from CSV: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            print(f"Found {len(df)} rows")
            migrated = migrate_dataframe(df, source=csv_path.stem)
            total_migrated += migrated
        except Exception as e:
            print(f"Error reading {csv_path}: {e}")
            continue
    
    return total_migrated


def migrate_dataframe(df: pd.DataFrame, source: str = "unknown") -> int:
    """
    Migrate DataFrame to PostgreSQL.
    
    Args:
        df: DataFrame with article data
        source: Source identifier
        
    Returns:
        Number of articles migrated
    """
    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        print("Make sure Docker containers are running: docker-compose up -d")
        return 0
    
    # Normalize column names
    column_mapping = {
        'title': 'title',
        'published_at': 'published_at',
        'publication_date': 'published_at',
        'date': 'published_at',
        'source': 'source',
        'url': 'url',
        'link': 'url',
        'content': 'content',
        'description': 'description',
        'full_text': 'full_text',
        'text': 'content',
        'processed_text': 'processed_text',
        'retrieved_at': 'retrieved_at',
        'retrieved': 'retrieved_at'
    }
    
    # Rename columns
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)
    
    # Ensure required columns exist
    if 'title' not in df.columns:
        print("ERROR: 'title' column not found")
        return 0
    if 'url' not in df.columns:
        print("ERROR: 'url' column not found")
        return 0
    
    # Fill missing columns
    for col in ['published_at', 'source', 'content', 'description', 'full_text', 'processed_text']:
        if col not in df.columns:
            df[col] = None
    
    # Parse dates
    if 'published_at' in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    
    if 'retrieved_at' not in df.columns:
        df['retrieved_at'] = datetime.now()
    else:
        df['retrieved_at'] = pd.to_datetime(df['retrieved_at'], errors='coerce')
        df['retrieved_at'] = df['retrieved_at'].fillna(datetime.now())
    
    migrated = 0
    skipped = 0
    
    with get_db_cursor() as cur:
        for idx, row in df.iterrows():
            try:
                # Check if URL already exists
                cur.execute("SELECT id FROM articles WHERE url = %s", (row['url'],))
                existing = cur.fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # Insert article
                cur.execute("""
                    INSERT INTO articles 
                    (title, published_at, source, url, content, description, full_text, processed_text, retrieved_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(row['title']) if pd.notna(row['title']) else '',
                    row['published_at'] if pd.notna(row['published_at']) else None,
                    str(row['source']) if pd.notna(row['source']) else None,
                    str(row['url']),
                    str(row['content']) if pd.notna(row['content']) else None,
                    str(row['description']) if pd.notna(row['description']) else None,
                    str(row['full_text']) if pd.notna(row['full_text']) else None,
                    str(row['processed_text']) if pd.notna(row['processed_text']) else None,
                    row['retrieved_at']
                ))
                
                article_id = cur.fetchone()['id']
                
                # If this is classified_articles.csv, also migrate classifications
                if source == 'classified_articles' and 'ce_areas' in row and 'ai_technologies' in row:
                    ce_areas = []
                    ai_techs = []
                    
                    if pd.notna(row['ce_areas']):
                        ce_areas = [a.strip() for a in str(row['ce_areas']).split(',') if a.strip()]
                    
                    if pd.notna(row['ai_technologies']):
                        ai_techs = [t.strip() for t in str(row['ai_technologies']).split(',') if t.strip()]
                    
                    if ce_areas or ai_techs:
                        cur.execute("""
                            INSERT INTO classifications 
                            (article_id, ce_areas, ai_technologies, classification_method)
                            VALUES (%s, %s, %s, 'keyword')
                        """, (article_id, ce_areas, ai_techs))
                
                migrated += 1
                
                if (migrated + skipped) % 50 == 0:
                    print(f"  Processed {migrated + skipped} articles... ({migrated} migrated, {skipped} skipped)")
                    
            except Exception as e:
                print(f"Error migrating row {idx}: {e}")
                skipped += 1
                continue
    
    print(f"\nMigration complete: {migrated} articles migrated, {skipped} skipped")
    return migrated


def main():
    """Main migration function."""
    print("=" * 70)
    print("CE49X Final Project - Database Migration")
    print("=" * 70)
    print()
    
    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        print("\nPlease ensure:")
        print("1. Docker containers are running: docker-compose up -d")
        print("2. Database credentials in .env file are correct")
        return
    
    print("Database connection successful!\n")
    
    total_migrated = 0
    
    # Try SQLite first
    total_migrated += migrate_from_sqlite()
    
    # Then CSV files
    total_migrated += migrate_from_csv()
    
    print("\n" + "=" * 70)
    print(f"Total articles migrated: {total_migrated}")
    print("=" * 70)
    
    # Show statistics
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM articles")
        total = cur.fetchone()['count']
        print(f"\nTotal articles in database: {total}")
        
        cur.execute("SELECT COUNT(*) as count FROM classifications")
        classified = cur.fetchone()['count']
        print(f"Total classifications: {classified}")


if __name__ == "__main__":
    main()

