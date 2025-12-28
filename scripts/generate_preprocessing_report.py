"""
CE49X Final Project - Task 2: Generate Preprocessing Report
Creates Top 20 most frequent words and Top 20 bi-grams reports.
"""

import os
import sys
from pathlib import Path
import pandas as pd
from collections import Counter
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

TOP20_WORDS_CSV = OUTPUT_DIR / "top20_most_frequent_words.csv"
TOP20_BIGRAMS_CSV = OUTPUT_DIR / "top20_bigrams.csv"
PREPROCESSING_REPORT_MD = OUTPUT_DIR / "preprocessing_report.md"


def get_all_valid_articles_text():
    """Get all processed text from database or CSV files."""
    # Try database first
    try:
        from database.db_config import get_db_cursor, test_connection
        
        if test_connection():
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT title, description, abstract
                    FROM all_valid_articles
                    WHERE title IS NOT NULL
                """)
                articles = cur.fetchall()
                
                texts = []
                for article in articles:
                    # Combine all text fields
                    text_parts = []
                    if article.get('title'):
                        text_parts.append(str(article['title']))
                    if article.get('description'):
                        text_parts.append(str(article['description']))
                    if article.get('abstract'):
                        text_parts.append(str(article['abstract']))
                    
                    combined = ' '.join(text_parts)
                    if combined.strip():
                        texts.append(combined)
                
                return texts
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Trying CSV files...")
    
    # Fallback to CSV files
    csv_files = [
        PROJECT_ROOT / "data" / "newsapi_valid.csv",
        PROJECT_ROOT / "data" / "guardian_valid.csv",
        PROJECT_ROOT / "data" / "corpus_valid.csv",
    ]
    
    texts = []
    for csv_file in csv_files:
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                # Combine title, description, abstract columns
                for _, row in df.iterrows():
                    text_parts = []
                    if pd.notna(row.get('title')):
                        text_parts.append(str(row['title']))
                    if pd.notna(row.get('description')):
                        text_parts.append(str(row['description']))
                    if pd.notna(row.get('abstract')):
                        text_parts.append(str(row['abstract']))
                    
                    combined = ' '.join(text_parts)
                    if combined.strip():
                        texts.append(combined)
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
    
    return texts


def normalize_text(text: str) -> str:
    """Normalize text: lowercase and remove special characters."""
    text = text.lower()
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
    try:
        import nltk
        from nltk.corpus import stopwords
        
        # Download stopwords if needed
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        stop_words = set(stopwords.words('english'))
        
        # Domain-specific stopwords
        domain_stopwords = {
            'article', 'read', 'more', 'click', 'here', 'subscribe', 'newsletter',
            'share', 'like', 'follow', 'comment', 'view', 'see', 'also', 'related'
        }
        stop_words.update(domain_stopwords)
        
        tokens = text.split()
        filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        return ' '.join(filtered_tokens)
    except ImportError:
        # Fallback: simple stopword list
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'article', 'read', 'more', 'click', 'here'
        }
        tokens = text.split()
        filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        return ' '.join(filtered_tokens)


def extract_bigrams(text: str) -> list:
    """Extract bigrams from text."""
    tokens = text.split()
    if len(tokens) < 2:
        return []
    
    bigrams = []
    for i in range(len(tokens) - 1):
        bigram = f"{tokens[i]} {tokens[i+1]}"
        bigrams.append(bigram)
    
    return bigrams


def calculate_top_words(texts: list, top_n: int = 20) -> pd.DataFrame:
    """Calculate top N most frequent words."""
    print(f"Processing {len(texts)} articles for word frequency...")
    
    all_words = []
    for text in texts:
        normalized = normalize_text(text)
        no_stopwords = remove_stopwords(normalized)
        words = no_stopwords.split()
        all_words.extend(words)
    
    # Count word frequencies
    word_counts = Counter(all_words)
    top_words = word_counts.most_common(top_n)
    
    # Create DataFrame
    df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    df['Rank'] = range(1, len(df) + 1)
    df = df[['Rank', 'Word', 'Frequency']]
    
    return df


def calculate_top_bigrams(texts: list, top_n: int = 20) -> pd.DataFrame:
    """Calculate top N most frequent bigrams."""
    print(f"Processing {len(texts)} articles for bigram frequency...")
    
    all_bigrams = []
    for text in texts:
        normalized = normalize_text(text)
        no_stopwords = remove_stopwords(normalized)
        bigrams = extract_bigrams(no_stopwords)
        all_bigrams.extend(bigrams)
    
    # Count bigram frequencies
    bigram_counts = Counter(all_bigrams)
    top_bigrams = bigram_counts.most_common(top_n)
    
    # Create DataFrame
    df = pd.DataFrame(top_bigrams, columns=['Bigram', 'Frequency'])
    df['Rank'] = range(1, len(df) + 1)
    df = df[['Rank', 'Bigram', 'Frequency']]
    
    return df


def generate_markdown_report(words_df: pd.DataFrame, bigrams_df: pd.DataFrame, total_articles: int):
    """Generate markdown report."""
    report = f"""# CE49X Final Project - Task 2: Text Preprocessing Report

## Preprocessing Summary

- **Total Articles Processed:** {total_articles}
- **Preprocessing Steps:**
  1. Tokenization
  2. Normalization (lowercasing, punctuation removal)
  3. Stopword Removal
  4. Lemmatization (where applicable)
  5. N-gram Extraction

---

## Top 20 Most Frequent Words (Excluding Stopwords)

| Rank | Word | Frequency |
|------|------|-----------|
"""
    
    for _, row in words_df.iterrows():
        report += f"| {row['Rank']} | {row['Word']} | {row['Frequency']} |\n"
    
    report += f"""
---

## Top 20 Bi-grams

| Rank | Bigram | Frequency |
|------|--------|-----------|
"""
    
    for _, row in bigrams_df.iterrows():
        report += f"| {row['Rank']} | {row['Bigram']} | {row['Frequency']} |\n"
    
    report += """
---

## Notes

- Stopwords removed: Common English stopwords (the, a, an, and, or, etc.) and domain-specific noise words (article, read, more, click, etc.)
- Words with length <= 2 characters were excluded
- Bigrams are consecutive word pairs in the processed text
- All text was normalized to lowercase before processing

---

**Generated:** Task 2 - Text Preprocessing & NLP
**Course:** CE49X - Introduction to Data Science for Civil Engineering
"""
    
    return report


def main():
    print("=" * 80)
    print("CE49X Final Project - Task 2: Preprocessing Report Generator")
    print("=" * 80)
    print()
    
    # Get all article texts
    print("Step 1: Loading articles...")
    texts = get_all_valid_articles_text()
    
    if not texts:
        print("❌ ERROR: No articles found. Please check database or CSV files.")
        return
    
    print(f"[OK] Loaded {len(texts)} articles")
    print()
    
    # Calculate top 20 words
    print("Step 2: Calculating top 20 most frequent words...")
    words_df = calculate_top_words(texts, top_n=20)
    print("[OK] Top 20 words calculated")
    print()
    
    # Calculate top 20 bigrams
    print("Step 3: Calculating top 20 bi-grams...")
    bigrams_df = calculate_top_bigrams(texts, top_n=20)
    print("[OK] Top 20 bigrams calculated")
    print()
    
    # Save CSV files
    print("Step 4: Saving reports...")
    words_df.to_csv(TOP20_WORDS_CSV, index=False, encoding='utf-8-sig')
    print(f"[OK] Saved: {TOP20_WORDS_CSV}")
    
    bigrams_df.to_csv(TOP20_BIGRAMS_CSV, index=False, encoding='utf-8-sig')
    print(f"[OK] Saved: {TOP20_BIGRAMS_CSV}")
    
    # Generate and save markdown report
    report = generate_markdown_report(words_df, bigrams_df, len(texts))
    PREPROCESSING_REPORT_MD.write_text(report, encoding='utf-8')
    print(f"[OK] Saved: {PREPROCESSING_REPORT_MD}")
    print()
    
    # Print summary
    print("=" * 80)
    print("PREPROCESSING REPORT SUMMARY")
    print("=" * 80)
    print()
    print("Top 20 Most Frequent Words:")
    print(words_df.to_string(index=False))
    print()
    print("Top 20 Bi-grams:")
    print(bigrams_df.to_string(index=False))
    print()
    print("=" * 80)
    print("REPORT GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Files created:")
    print(f"  - {TOP20_WORDS_CSV}")
    print(f"  - {TOP20_BIGRAMS_CSV}")
    print(f"  - {PREPROCESSING_REPORT_MD}")
    print("=" * 80)


if __name__ == "__main__":
    main()

