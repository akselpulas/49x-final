"""
NewsAPI articles için OpenAI LLM ile 50-100 kelimelik özet (summary) oluştur.
CSV dosyasından makaleleri okuyup, özetleri database'e kaydeder.
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Input CSV file
INPUT_CSV = PROJECT_ROOT / "data" / "NewsAPI articles son_cleaned.csv"

# Rate limiting
REQUEST_DELAY = 1.0  # Delay between API requests (seconds)


def ensure_summary_column():
    """newsapi_articles tablosuna summary kolonu ekle"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='newsapi_articles' AND column_name='summary'
        """)
        
        if not cur.fetchone():
            print("summary kolonu ekleniyor...")
            cur.execute("ALTER TABLE newsapi_articles ADD COLUMN summary TEXT")
            print("summary kolonu eklendi.")


def get_articles_without_summary() -> list:
    """Summary'si olmayan newsapi_articles makalelerini getir"""
    with get_db_cursor() as cur:
        query = """
            SELECT id, title, description, full_text, url
            FROM newsapi_articles
            WHERE summary IS NULL OR summary = ''
            ORDER BY id
        """
        cur.execute(query)
        return cur.fetchall()


def count_words(text: str) -> int:
    """Metindeki kelime sayısını hesapla"""
    if not text:
        return 0
    return len(text.split())


def generate_summary(title: str, description: str, full_text: str = None, max_retries: int = 3) -> Optional[str]:
    """OpenAI LLM kullanarak en az 50 kelimelik özet oluştur"""
    # İçeriği birleştir ve sınırla
    content = full_text or description or ''
    if not content:
        return None
    
    # İçeriği sınırla (3000 karakter)
    max_content_length = 3000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "..."
    
    prompt = f"""Write a comprehensive summary (abstract) for the following article. 
The summary should capture the main topic, findings, and importance of the article.

CRITICAL REQUIREMENT: The summary must be AT LEAST 50 words. It can be up to 100 words, but MUST NOT be shorter than 50 words.

Article Title: {title}

Article Content:
{content}

Write only the summary text, no explanations. The summary can be in English or Turkish. The summary MUST be at least 50 words long."""

    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("  ERROR: OPENAI_API_KEY environment variable not set!")
            return None
        
        client = OpenAI(api_key=api_key)
        
        # Retry mechanism if summary is too short
        for attempt in range(max_retries):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates comprehensive summaries for articles. Always respond with only the summary text, no explanations. Summary must be AT LEAST 50 words, up to 100 words."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=250  # Increased for longer summaries
            )
            
            summary = response.choices[0].message.content.strip()
            word_count = count_words(summary)
            
            # Check if summary meets minimum word requirement
            if word_count >= 50:
                return summary
            else:
                if attempt < max_retries - 1:
                    print(f"    Warning: Summary too short ({word_count} words), retrying...")
                    time.sleep(0.5)  # Brief delay before retry
                else:
                    print(f"    Warning: Summary still too short after {max_retries} attempts ({word_count} words)")
                    # Return anyway if it's close (at least 40 words)
                    if word_count >= 40:
                        return summary
                    return None
        
        return summary
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def save_summary(article_id: int, summary: str):
    """Summary'yi veritabanına kaydet"""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE newsapi_articles 
            SET summary = %s 
            WHERE id = %s
        """, (summary, article_id))


def main():
    """Main function"""
    print("=" * 70)
    print("NEWSAPI ARTICLES - SUMMARY GENERATION")
    print("=" * 70)
    print()
    
    if not test_connection():
        print("ERROR: Cannot connect to database!")
        return
    
    # Summary kolonunu ekle
    ensure_summary_column()
    
    # Summary'si olmayan makaleleri getir
    print("Getting articles without summary from database...")
    articles = get_articles_without_summary()
    
    if not articles:
        print("All articles already have summaries or no articles found.")
        
        # İstatistik göster
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM newsapi_articles")
            total = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as with_summary FROM newsapi_articles WHERE summary IS NOT NULL AND summary != ''")
            with_summary = cur.fetchone()['with_summary']
            print(f"\nTotal articles: {total}")
            print(f"With summary: {with_summary}")
            print(f"Without summary: {total - with_summary}")
        return
    
    print(f"Found {len(articles)} articles without summary.\n")
    
    # Her makale için summary oluştur
    success_count = 0
    fail_count = 0
    
    for idx, article in enumerate(articles, 1):
        article_id = article['id']
        title = article['title'] or 'No title'
        description = article.get('description') or ''
        full_text = article.get('full_text') or ''
        url = article.get('url', '')
        
        print(f"[{idx}/{len(articles)}] Processing (ID: {article_id}): {title[:60]}...")
        
        # Summary oluştur
        summary = generate_summary(title, description, full_text)
        
        if summary:
            word_count = count_words(summary)
            # Veritabanına kaydet
            save_summary(article_id, summary)
            print(f"  [OK] Summary created and saved ({word_count} words)")
            print(f"  Summary: {summary[:100]}...")
            success_count += 1
        else:
            print(f"  [ERROR] Failed to create summary")
            fail_count += 1
        
        print()
        
        # Rate limiting
        if idx < len(articles):
            time.sleep(REQUEST_DELAY)
    
    # Özet
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total processed: {len(articles)}")
    print("=" * 70)
    
    # Genel istatistikler
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM newsapi_articles")
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as with_summary FROM newsapi_articles WHERE summary IS NOT NULL AND summary != ''")
        with_summary = cur.fetchone()['with_summary']
        print(f"\nOverall Status:")
        print(f"  Total articles: {total}")
        print(f"  With summary: {with_summary}")
        print(f"  Without summary: {total - with_summary}")


if __name__ == "__main__":
    main()

