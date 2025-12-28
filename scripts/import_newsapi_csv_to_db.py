"""
Import NewsAPI CSV file to PostgreSQL database.
Removes duplicates and saves to both articles and filtered_ai_ce_articles tables.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
import pandas as pd

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db_config import get_db_cursor, test_connection

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Input CSV file
INPUT_CSV = PROJECT_ROOT / "data" / "NewsAPI articles son.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "NewsAPI articles son_cleaned.csv"


def normalize_url(url: str) -> str:
    """
    Normalize URL for duplicate detection.
    Removes trailing slashes, query parameters, fragments, and converts to lowercase.
    """
    if not url:
        return ""
    
    # Remove fragments and query parameters
    url = url.split('#')[0].split('?')[0]
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Convert to lowercase
    url = url.lower()
    
    return url


def normalize_title(title: str) -> str:
    """
    Normalize title for duplicate detection.
    Removes extra whitespace, converts to lowercase, and removes special characters.
    """
    if not title:
        return ""
    
    # Convert to lowercase
    title = title.lower()
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Remove common punctuation
    title = title.replace('"', '').replace("'", '').replace('`', '')
    
    return title


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate articles based on normalized URL and title.
    
    Args:
        df: DataFrame with articles
        
    Returns:
        DataFrame with duplicates removed
    """
    print("Removing duplicates...")
    print(f"  Before: {len(df)} articles")
    
    # Normalize URLs and titles
    df['url_normalized'] = df['url'].apply(normalize_url)
    df['title_normalized'] = df['title'].apply(normalize_title)
    
    # Remove duplicates based on normalized URL (priority)
    df_unique = df.drop_duplicates(subset=['url_normalized'], keep='first')
    
    # Also check for title-based duplicates (if URL is missing or similar)
    # Group by normalized title and keep first occurrence
    df_unique = df_unique.drop_duplicates(subset=['title_normalized'], keep='first')
    
    # Remove normalization columns
    df_unique = df_unique.drop(columns=['url_normalized', 'title_normalized'])
    
    print(f"  After: {len(df_unique)} articles")
    print(f"  Removed: {len(df) - len(df_unique)} duplicates")
    
    return df_unique


def create_newsapi_table_if_not_exists():
    """Create newsapi_articles table if it doesn't exist."""
    with get_db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS newsapi_articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                published_at TIMESTAMP,
                source TEXT,
                url TEXT UNIQUE NOT NULL,
                description TEXT,
                full_text TEXT,
                ai_keywords_found TEXT[],
                ce_keywords_found TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            )
        """)


def parse_date(date_str: str) -> str:
    """Parse date string to ISO format."""
    if not date_str or pd.isna(date_str):
        return None
    
    try:
        # Try parsing ISO format (2025-12-24T14:00:00Z)
        if 'T' in str(date_str):
            dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            return dt.isoformat()
        # Try other formats
        dt = pd.to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return None


def save_to_database(df: pd.DataFrame) -> int:
    """
    Save articles to PostgreSQL database in a separate newsapi_articles table.
    
    Args:
        df: DataFrame with articles
        
    Returns:
        Number of inserted articles
    """
    if df.empty:
        return 0
    
    if not test_connection():
        print("ERROR: Cannot connect to database!")
        return 0
    
    # Ensure newsapi_articles table exists
    create_newsapi_table_if_not_exists()
    
    inserted_articles = 0
    skipped = 0
    
    # Get existing URLs first (outside the loop)
    with get_db_cursor() as cur:
        cur.execute("SELECT url FROM newsapi_articles")
        existing_urls = {row['url'] for row in cur.fetchall()}
    
    print(f"  Existing articles in newsapi_articles table: {len(existing_urls)}")
    
    # Process each article in a separate transaction
    for idx, row in df.iterrows():
        url = str(row.get('url', '')).strip()
        if not url or url in existing_urls:
            skipped += 1
            continue
        
        title = str(row.get('title', '')).strip()
        description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
        source = str(row.get('source', '')).strip() if pd.notna(row.get('source')) else ''
        published_at = parse_date(row.get('publication_date'))
        
        # Get keywords (already found in CSV) - convert comma-separated string to array
        ai_keywords_str = str(row.get('ai_keywords_found', '')).strip() if pd.notna(row.get('ai_keywords_found')) else ''
        ce_keywords_str = str(row.get('ce_keywords_found', '')).strip() if pd.notna(row.get('ce_keywords_found')) else ''
        
        # Convert to array (split by comma and strip whitespace)
        ai_keywords = [kw.strip() for kw in ai_keywords_str.split(',') if kw.strip()] if ai_keywords_str else []
        ce_keywords = [kw.strip() for kw in ce_keywords_str.split(',') if kw.strip()] if ce_keywords_str else []
        
        # Use description as full_text (no full_text in CSV)
        full_text = description
        
        # Each article in its own transaction
        try:
            with get_db_cursor() as cur:
                # Insert into newsapi_articles table
                cur.execute("""
                    INSERT INTO newsapi_articles
                    (title, published_at, source, url, description, full_text, 
                     ai_keywords_found, ce_keywords_found)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                """, (
                    title,
                    published_at,
                    source,
                    url,
                    description,
                    full_text,
                    ai_keywords,
                    ce_keywords
                ))
                
                if cur.rowcount > 0:
                    inserted_articles += 1
                else:
                    skipped += 1
                    
        except Exception as e:
            print(f"  Error inserting article '{title[:50]}...': {e}")
            skipped += 1
            continue
        
        # Progress update every 100 articles
        if (inserted_articles + skipped) % 100 == 0:
            print(f"  Progress: {inserted_articles} inserted, {skipped} skipped")
    
    return inserted_articles


def main():
    """Main function."""
    print("=" * 70)
    print("NEWSAPI CSV TO DATABASE IMPORT")
    print("=" * 70)
    print()
    
    # Check if input file exists
    if not INPUT_CSV.exists():
        print(f"ERROR: Input file not found: {INPUT_CSV}")
        return
    
    print(f"Input file: {INPUT_CSV}")
    print()
    
    # Read CSV
    print("Reading CSV file...")
    try:
        df = pd.read_csv(INPUT_CSV, encoding='utf-8')
        print(f"  Loaded: {len(df)} articles")
    except Exception as e:
        print(f"ERROR: Failed to read CSV: {e}")
        return
    
    print()
    
    # Remove duplicates
    df_cleaned = remove_duplicates(df)
    print()
    
    # Save cleaned CSV
    print(f"Saving cleaned CSV to: {OUTPUT_CSV}")
    df_cleaned.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    print("  [OK] Cleaned CSV saved")
    print()
    
    # Save to database
    print("Saving to database...")
    inserted_articles = save_to_database(df_cleaned)
    print(f"  [OK] newsapi_articles table: {inserted_articles} inserted")
    print()
    
    # Final count
    total_newsapi = 0
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM newsapi_articles")
            total_newsapi = cur.fetchone()['count']
    except Exception as e:
        print(f"  Warning: Could not get final counts: {e}")
    
    print("=" * 70)
    print("İŞLEM TAMAMLANDI")
    print("=" * 70)
    print(f"CSV'den okunan: {len(df)} makale")
    print(f"Duplicate temizlendikten sonra: {len(df_cleaned)} makale")
    print(f"Yeni eklenen: {inserted_articles} makale")
    print(f"newsapi_articles tablosunda toplam: {total_newsapi} makale")
    print(f"Temizlenmiş CSV: {OUTPUT_CSV}")
    print("=" * 70)


if __name__ == "__main__":
    main()

