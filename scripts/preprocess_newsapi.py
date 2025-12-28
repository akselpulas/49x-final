"""
CE49X Final Project - Task 2: Text Preprocessing & NLP
NewsAPI Data Preprocessing Script

This script processes the raw newsapi_articles.csv file by:
- Tokenization
- Normalization (lowercasing, punctuation removal)
- Stopword removal
- Lemmatization
- Extracting N-grams
- Calculating TF-IDF scores

Author: [Your Name]
Course: CE49X - Introduction to Data Science for Civil Engineering
Date: Fall 2025
"""

import os
import sys
import pandas as pd
import re
from pathlib import Path
from typing import List

# Check and import required libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.util import ngrams
except ImportError:
    print("ERROR: NLTK library is not installed.")
    print("Please install it using: pip install nltk")
    sys.exit(1)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    print("ERROR: scikit-learn library is not installed.")
    print("Please install it using: pip install scikit-learn")
    sys.exit(1)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK punkt_tab tokenizer...")
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading NLTK wordnet...")
    nltk.download('wordnet', quiet=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / "data_raw" / "newsapi_articles.csv"
OUTPUT_FILE = PROJECT_ROOT / "data_raw" / "newsapi_articles.csv"  # Overwrite same file

# ============================================================================
# PREPROCESSING FUNCTIONS
# ============================================================================

def combine_text_fields(row: pd.Series) -> str:
    """
    Combine title and description into a single text field.
    
    Args:
        row: DataFrame row containing title and description
        
    Returns:
        Combined text string
    """
    title = str(row.get('title', ''))
    description = str(row.get('description', ''))
    
    # Combine and handle NaN values
    if pd.isna(title):
        title = ''
    if pd.isna(description):
        description = ''
    
    return f"{title} {description}".strip()


def normalize_text(text: str) -> str:
    """
    Normalize text: lowercase and remove special characters.
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text string
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep spaces and alphanumeric
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def remove_stopwords(text: str) -> str:
    """
    Remove English stopwords and domain-specific noise words.
    
    Args:
        text: Input text string
        
    Returns:
        Text with stopwords removed
    """
    # Get English stopwords
    stop_words = set(stopwords.words('english'))
    
    # Add domain-specific noise words
    domain_stopwords = {
        'subscribe', 'click', 'here', 'read', 'more', 'article', 'news',
        'said', 'says', 'according', 'also', 'would', 'could', 'should'
    }
    stop_words.update(domain_stopwords)
    
    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words and len(word) > 2]
    
    return ' '.join(filtered_tokens)


def lemmatize_text(text: str) -> str:
    """
    Lemmatize text: reduce words to their root form.
    
    Args:
        text: Input text string
        
    Returns:
        Lemmatized text string
    """
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)


def extract_ngrams(text: str, n: int) -> List[str]:
    """
    Extract n-grams from text.
    
    Args:
        text: Input text string
        n: N-gram size (2 for bigrams, 3 for trigrams)
        
    Returns:
        List of n-gram strings
    """
    tokens = word_tokenize(text)
    ngram_list = list(ngrams(tokens, n))
    return [' '.join(gram) for gram in ngram_list]


def preprocess_text(text: str) -> dict:
    """
    Complete preprocessing pipeline for a single text.
    
    Args:
        text: Raw input text
        
    Returns:
        Dictionary with processed text and features
    """
    if pd.isna(text) or text == '':
        return {
            'processed_text': '',
            'bigrams': [],
            'trigrams': []
        }
    
    # Step 1: Normalize
    normalized = normalize_text(text)
    
    # Step 2: Remove stopwords
    no_stopwords = remove_stopwords(normalized)
    
    # Step 3: Lemmatize
    lemmatized = lemmatize_text(no_stopwords)
    
    # Step 4: Extract n-grams
    bigrams = extract_ngrams(lemmatized, 2)
    trigrams = extract_ngrams(lemmatized, 3)
    
    return {
        'processed_text': lemmatized,
        'bigrams': bigrams,
        'trigrams': trigrams
    }


def calculate_tfidf(df: pd.DataFrame, text_column: str = 'processed_text') -> pd.DataFrame:
    """
    Calculate TF-IDF scores for processed texts.
    
    Args:
        df: DataFrame with processed text column
        text_column: Name of the column containing processed text
        
    Returns:
        DataFrame with TF-IDF scores added
    """
    # Filter out empty texts
    texts = df[text_column].fillna('').astype(str)
    non_empty = texts[texts.str.len() > 0]
    
    if len(non_empty) == 0:
        print("Warning: No valid texts for TF-IDF calculation")
        return df
    
    # Calculate TF-IDF
    vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2), min_df=2)
    try:
        tfidf_matrix = vectorizer.fit_transform(non_empty)
        feature_names = vectorizer.get_feature_names_out()
        
        # Get top TF-IDF terms for each document
        df['top_tfidf_terms'] = ''
        
        for idx, row_idx in enumerate(non_empty.index):
            # Get top 5 terms for this document
            tfidf_scores = tfidf_matrix[idx].toarray()[0]
            top_indices = tfidf_scores.argsort()[-5:][::-1]
            top_terms = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            df.at[row_idx, 'top_tfidf_terms'] = ', '.join(top_terms)
        
    except ValueError as e:
        print(f"Warning: TF-IDF calculation failed: {e}")
        df['top_tfidf_terms'] = ''
    
    return df


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to process the newsapi_articles.csv file.
    """
    print("=" * 70)
    print("CE49X Final Project - Task 2: Text Preprocessing & NLP")
    print("=" * 70)
    print()
    
    # Check if input file exists
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return
    
    # Load data
    print(f"Loading data from {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} articles")
    except Exception as e:
        print(f"ERROR: Failed to load CSV file: {e}")
        return
    
    # Combine title and description into full_text
    print("\nCombining title and description fields...")
    df['full_text'] = df.apply(combine_text_fields, axis=1)
    
    # Preprocess each article
    print("Preprocessing articles (this may take a while)...")
    processed_data = []
    
    for idx, row in df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} articles...")
        
        result = preprocess_text(row['full_text'])
        processed_data.append(result)
    
    # Add processed columns to dataframe
    df['processed_text'] = [d['processed_text'] for d in processed_data]
    df['bigrams'] = [', '.join(d['bigrams'][:10]) for d in processed_data]  # Top 10 bigrams
    df['trigrams'] = [', '.join(d['trigrams'][:10]) for d in processed_data]  # Top 10 trigrams
    
    print(f"\n[OK] Preprocessing complete for {len(df)} articles")
    
    # Calculate TF-IDF
    print("\nCalculating TF-IDF scores...")
    df = calculate_tfidf(df, 'processed_text')
    
    # Save processed data
    print(f"\nSaving processed data to {OUTPUT_FILE}...")
    try:
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
        print(f"[OK] Saved {len(df)} processed articles to {OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return
    
    # Print statistics
    print("\n" + "=" * 70)
    print("Preprocessing Summary")
    print("=" * 70)
    print(f"Total articles processed: {len(df)}")
    print(f"Articles with processed text: {df['processed_text'].str.len().gt(0).sum()}")
    print()
    
    # Show top words (excluding stopwords)
    print("Top 20 most frequent words (excluding stopwords):")
    all_words = ' '.join(df['processed_text'].fillna('')).split()
    word_freq = pd.Series(all_words).value_counts().head(20)
    for word, count in word_freq.items():
        print(f"  {word}: {count}")
    print()
    
    # Show top bigrams
    print("Top 20 bigrams:")
    all_bigrams = []
    for bigrams_str in df['bigrams'].fillna(''):
        if bigrams_str:
            all_bigrams.extend(bigrams_str.split(', '))
    bigram_freq = pd.Series(all_bigrams).value_counts().head(20)
    for bigram, count in bigram_freq.items():
        print(f"  {bigram}: {count}")
    print()


if __name__ == "__main__":
    main()

