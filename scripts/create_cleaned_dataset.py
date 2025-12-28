"""
CE49X Final Project - Task 2: Create Cleaned Dataset
Creates a cleaned version of the dataset with preprocessed text.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import re

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Output files
OUTPUT_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

CLEANED_DATASET_CSV = OUTPUT_DIR / "cleaned_dataset.csv"


def normalize_text(text: str) -> str:
    """Normalize text: lowercase and remove special characters."""
    if pd.isna(text) or not text:
        return ""
    
    text = str(text).lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def remove_stopwords(text: str) -> str:
    """Remove common English stopwords."""
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'article', 'read', 'more', 'click', 'here', 'subscribe', 'newsletter',
        'share', 'like', 'follow', 'comment', 'view', 'see', 'also', 'related'
    }
    
    tokens = text.split()
    filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
    return ' '.join(filtered_tokens)


def get_all_valid_articles():
    """Get all valid articles from database."""
    try:
        from database.db_config import get_db_cursor, test_connection
        
        if test_connection():
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, url, source, publication_date, abstract,
                           ce_areas, ai_technologies
                    FROM all_valid_articles
                    ORDER BY id
                """)
                articles = cur.fetchall()
                
                # Convert to DataFrame
                df = pd.DataFrame(articles)
                return df
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def preprocess_article_text(row):
    """Preprocess a single article's text."""
    # Combine title, description, and abstract
    text_parts = []
    if pd.notna(row.get('title')):
        text_parts.append(str(row['title']))
    if pd.notna(row.get('description')):
        text_parts.append(str(row['description']))
    if pd.notna(row.get('abstract')):
        text_parts.append(str(row['abstract']))
    
    combined_text = ' '.join(text_parts)
    
    # Normalize
    normalized = normalize_text(combined_text)
    
    # Remove stopwords
    cleaned = remove_stopwords(normalized)
    
    return cleaned


def main():
    print("=" * 80)
    print("CE49X Final Project - Task 2: Create Cleaned Dataset")
    print("=" * 80)
    print()
    
    # Get articles from database
    print("Step 1: Loading articles from database...")
    df = get_all_valid_articles()
    
    if df is None or len(df) == 0:
        print("[ERROR] No articles found in database.")
        return
    
    print(f"[OK] Loaded {len(df)} articles")
    print()
    
    # Preprocess text
    print("Step 2: Preprocessing text (normalization, stopword removal)...")
    df['cleaned_text'] = df.apply(preprocess_article_text, axis=1)
    print("[OK] Text preprocessing complete")
    print()
    
    # Select columns for cleaned dataset
    cleaned_df = df[[
        'id', 'title', 'description', 'url', 'source', 'publication_date',
        'abstract', 'ce_areas', 'ai_technologies', 'cleaned_text'
    ]].copy()
    
    # Save cleaned dataset
    print("Step 3: Saving cleaned dataset...")
    cleaned_df.to_csv(CLEANED_DATASET_CSV, index=False, encoding='utf-8-sig')
    print(f"[OK] Saved: {CLEANED_DATASET_CSV}")
    print()
    
    # Print summary
    print("=" * 80)
    print("CLEANED DATASET SUMMARY")
    print("=" * 80)
    print(f"Total articles: {len(cleaned_df)}")
    print(f"Articles with cleaned text: {cleaned_df['cleaned_text'].str.len().gt(0).sum()}")
    print(f"Average cleaned text length: {cleaned_df['cleaned_text'].str.len().mean():.0f} characters")
    print()
    print("Sample cleaned text (first article):")
    if len(cleaned_df) > 0 and cleaned_df.iloc[0]['cleaned_text']:
        sample = cleaned_df.iloc[0]['cleaned_text'][:200]
        print(f"  {sample}...")
    print()
    print("=" * 80)
    print("CLEANED DATASET CREATION COMPLETE")
    print("=" * 80)
    print()
    print(f"File created: {CLEANED_DATASET_CSV}")
    print("=" * 80)


if __name__ == "__main__":
    main()

