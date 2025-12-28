"""
LLM-based classification script for CE49X Final Project.
Uses LLM API to classify articles stored in PostgreSQL database.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection
from scripts.llm_api import get_classifier

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent


def get_unclassified_articles(limit: int = None) -> List[Dict]:
    """Get articles that haven't been classified yet."""
    with get_db_cursor() as cur:
        query = """
            SELECT a.id, a.title, a.content, a.description, a.full_text, a.url
            FROM articles a
            LEFT JOIN classifications c ON a.id = c.article_id
            WHERE c.id IS NULL
            ORDER BY a.created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        cur.execute(query)
        return cur.fetchall()


def save_classification(article_id: int, classification: Dict):
    """Save classification result to database."""
    with get_db_cursor() as cur:
        # Delete old classifications for this article
        cur.execute("DELETE FROM classifications WHERE article_id = %s", (article_id,))
        
        # Insert new classification
        cur.execute("""
            INSERT INTO classifications 
            (article_id, ce_areas, ai_technologies, classification_method, 
             llm_model, confidence_score, raw_llm_response)
            VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
        """, (
            article_id,
            classification['ce_areas'],
            classification['ai_technologies'],
            'llm',
            classification.get('model', 'unknown'),
            classification.get('confidence', 0.0),
            classification.get('raw_response', '{}')
        ))


def main():
    """Main classification function."""
    print("=" * 70)
    print("CE49X Final Project - LLM-based Classification")
    print("=" * 70)
    print()
    
    # Check database connection
    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        print("Make sure Docker containers are running: docker-compose up -d")
        return
    
    # Get LLM classifier
    try:
        provider = os.getenv('LLM_PROVIDER', 'openai')  # 'openai' or 'anthropic'
        classifier = get_classifier(provider=provider)
        print(f"Using LLM provider: {classifier.provider}, model: {classifier.model}")
    except Exception as e:
        print(f"ERROR: Failed to initialize LLM classifier: {e}")
        print("\nPlease set one of:")
        print("  - OPENAI_API_KEY environment variable")
        print("  - ANTHROPIC_API_KEY environment variable")
        return
    
    # Get unclassified articles
    print("\nFetching unclassified articles...")
    articles = get_unclassified_articles()
    
    if not articles:
        print("No unclassified articles found.")
        return
    
    print(f"Found {len(articles)} unclassified articles")
    
    # Ask user for limit
    try:
        limit_input = input(f"\nHow many articles to classify? (Enter for all {len(articles)}): ").strip()
        limit = int(limit_input) if limit_input else len(articles)
        limit = min(limit, len(articles))
    except ValueError:
        limit = len(articles)
    
    articles_to_classify = articles[:limit]
    print(f"\nClassifying {len(articles_to_classify)} articles...")
    
    classified = 0
    failed = 0
    
    for idx, article in enumerate(articles_to_classify, 1):
        print(f"\n[{idx}/{len(articles_to_classify)}] Classifying: {article['title'][:60]}...")
        
        # Combine content fields
        content = article.get('full_text') or article.get('content') or article.get('description') or ''
        
        try:
            classification = classifier.classify_article(
                title=article['title'],
                content=content
            )
            
            # Save to database
            save_classification(article['id'], classification)
            
            print(f"  CE Areas: {', '.join(classification['ce_areas']) or 'None'}")
            print(f"  AI Technologies: {', '.join(classification['ai_technologies']) or 'None'}")
            print(f"  Confidence: {classification.get('confidence', 0.0):.2f}")
            
            classified += 1
            
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
            continue
    
    print("\n" + "=" * 70)
    print(f"Classification complete!")
    print(f"  Successfully classified: {classified}")
    print(f"  Failed: {failed}")
    print("=" * 70)
    
    # Show statistics
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT 
                COUNT(DISTINCT a.id) as total,
                COUNT(DISTINCT CASE WHEN c.ce_areas IS NOT NULL AND c.ai_technologies IS NOT NULL THEN a.id END) as with_both
            FROM articles a
            LEFT JOIN classifications c ON a.id = c.article_id
        """)
        stats = cur.fetchone()
        print(f"\nDatabase Statistics:")
        print(f"  Total articles: {stats['total']}")
        print(f"  Articles with both CE and AI classifications: {stats['with_both']}")


if __name__ == "__main__":
    main()

