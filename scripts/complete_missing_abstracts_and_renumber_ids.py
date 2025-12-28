"""
Complete missing abstracts for articles in all_valid_articles table using LLM,
then renumber IDs starting from 1.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import time
from typing import Optional

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Database connection
from database.db_config import get_db_cursor, test_connection

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def get_articles_without_abstracts():
    """Get articles that are missing abstracts."""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, title, description, text_content
            FROM all_valid_articles
            WHERE abstract IS NULL OR abstract = '' OR TRIM(abstract) = ''
            ORDER BY id
        """)
        return cur.fetchall()


def generate_abstract(title: str, description: str = None, text_content: str = None) -> Optional[str]:
    """
    Generate abstract using LLM API.
    
    Args:
        title: Article title
        description: Article description
        text_content: Full text content
        
    Returns:
        Abstract text or None
    """
    # Combine available content
    content_parts = []
    if description:
        content_parts.append(f"Description: {description}")
    if text_content:
        # Limit text content to avoid token limits
        max_text_length = 2000
        if len(text_content) > max_text_length:
            text_content = text_content[:max_text_length] + "..."
        content_parts.append(f"Content: {text_content}")
    
    content = "\n\n".join(content_parts) if content_parts else "No content available."
    
    prompt = f"""Create a concise abstract (summary) for the following article about Civil Engineering and AI.
The abstract should summarize the main topic, findings, and importance of the article.

IMPORTANT: The abstract must be 50-100 words. Do not make it shorter or longer.

Article Title: {title}

Article Content:
{content}

Write only the abstract text, no explanations. The abstract can be in English or Turkish. Word count must be 50-100 words."""

    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise abstracts for articles about Civil Engineering and AI. Always respond with only the abstract text, no explanations. Abstract must be 50-100 words."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        abstract = response.choices[0].message.content.strip()
        return abstract
        
    except Exception as e:
        print(f"  ERROR generating abstract: {e}")
        return None


def update_abstract(article_id: int, abstract: str):
    """Update abstract in database."""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE all_valid_articles 
            SET abstract = %s 
            WHERE id = %s
        """, (abstract, article_id))


def renumber_ids():
    """Renumber all IDs starting from 1, maintaining order by current ID."""
    print("\n" + "=" * 80)
    print("RENUMBERING IDs")
    print("=" * 80)
    
    with get_db_cursor() as cur:
        # Get all IDs in order
        cur.execute("""
            SELECT id 
            FROM all_valid_articles 
            ORDER BY id
        """)
        all_ids = [row['id'] for row in cur.fetchall()]
        
        total = len(all_ids)
        print(f"\nTotal articles: {total}")
        
        if total == 0:
            print("No articles to renumber.")
            return
        
        # Check if IDs already start from 1 and are sequential
        if all_ids == list(range(1, total + 1)):
            print("✓ IDs are already numbered sequentially from 1. No changes needed.")
            return
        
        # Create a mapping: old_id -> new_id
        id_mapping = {old_id: new_id for new_id, old_id in enumerate(all_ids, start=1)}
        
        # We need to use a temporary column to avoid conflicts
        print("\nStep 1: Adding temporary ID column...")
        try:
            cur.execute("ALTER TABLE all_valid_articles ADD COLUMN temp_new_id INTEGER")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "duplicate" in error_str or "column" in error_str:
                print("  Temporary column already exists, dropping it first...")
                cur.execute("ALTER TABLE all_valid_articles DROP COLUMN IF EXISTS temp_new_id")
                cur.execute("ALTER TABLE all_valid_articles ADD COLUMN temp_new_id INTEGER")
            else:
                raise
        
        # Update temp_new_id in batches for better performance
        print("Step 2: Assigning new IDs...")
        batch_size = 100
        for i in range(0, len(all_ids), batch_size):
            batch = all_ids[i:i+batch_size]
            for old_id in batch:
                new_id = id_mapping[old_id]
                cur.execute("""
                    UPDATE all_valid_articles 
                    SET temp_new_id = %s 
                    WHERE id = %s
                """, (new_id, old_id))
            print(f"  Processed {min(i+batch_size, len(all_ids))}/{len(all_ids)} articles...")
        
        # Drop old primary key constraint if exists
        print("\nStep 3: Dropping old primary key constraint...")
        try:
            # Get constraint name first
            cur.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'all_valid_articles' 
                AND constraint_type = 'PRIMARY KEY'
            """)
            pk_constraint = cur.fetchone()
            if pk_constraint:
                constraint_name = pk_constraint[0]
                cur.execute(f"ALTER TABLE all_valid_articles DROP CONSTRAINT {constraint_name}")
        except Exception as e:
            print(f"  Note: {e}")
        
        # Rename columns
        print("Step 4: Renaming ID columns...")
        cur.execute("ALTER TABLE all_valid_articles DROP COLUMN id")
        cur.execute("ALTER TABLE all_valid_articles RENAME COLUMN temp_new_id TO id")
        
        # Recreate primary key
        print("Step 5: Recreating primary key...")
        cur.execute("""
            ALTER TABLE all_valid_articles 
            ADD PRIMARY KEY (id)
        """)
        
        # Verify the renumbering
        cur.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM all_valid_articles")
        result = cur.fetchone()
        min_id = result['min']
        max_id = result['max']
        count = result['count']
        
        print(f"\n✓ Successfully renumbered {total} articles")
        print(f"  - ID range: {min_id} to {max_id}")
        print(f"  - Total count: {count}")


def main():
    print("=" * 80)
    print("COMPLETE MISSING ABSTRACTS AND RENUMBER IDs")
    print("=" * 80)
    
    # Test database connection
    if not test_connection():
        print("❌ Database connection failed. Please check your database configuration.")
        return
    
    # Step 1: Check for missing abstracts
    print("\nStep 1: Checking for articles without abstracts...")
    articles = get_articles_without_abstracts()
    missing_count = len(articles)
    
    if missing_count == 0:
        print("✓ All articles already have abstracts!")
    else:
        print(f"Found {missing_count} articles without abstracts")
        
        # Step 2: Generate abstracts
        print("\nStep 2: Generating abstracts using LLM...")
        print("This may take a while due to API rate limits...\n")
        
        success_count = 0
        fail_count = 0
        
        for i, article in enumerate(articles, 1):
            article_id = article['id']
            title = article.get('title') or "No title"
            description = article.get('description')
            text_content = article.get('text_content')
            
            print(f"[{i}/{missing_count}] Processing article ID {article_id}: {title[:60]}...")
            
            abstract = generate_abstract(title, description, text_content)
            
            if abstract:
                update_abstract(article_id, abstract)
                print(f"  ✓ Abstract generated ({len(abstract)} chars)")
                success_count += 1
            else:
                print(f"  ✗ Failed to generate abstract")
                fail_count += 1
            
            # Rate limiting - wait between API calls
            if i < missing_count:
                time.sleep(1)  # 1 second delay between calls
        
        print(f"\n✓ Abstract generation complete:")
        print(f"  - Success: {success_count}")
        print(f"  - Failed: {fail_count}")
    
    # Step 3: Renumber IDs
    print("\n" + "=" * 80)
    print("\nRenumbering IDs starting from 1...")
    renumber_ids()
    
    print("\n" + "=" * 80)
    print("PROCESS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

