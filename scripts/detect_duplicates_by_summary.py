"""
LLM kullanarak newsapi_articles tablosundaki summary'lara bakıp
birebir aynı konu olan duplicate'leri tespit eder.
Veritabanını değiştirmez, sadece analiz yapar ve sonuçları CSV'ye kaydeder.
"""

import os
import sys
import json
import time
import csv
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from itertools import combinations

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Output CSV file
OUTPUT_CSV = PROJECT_ROOT / "data" / "duplicate_articles_by_summary.csv"

# Rate limiting
REQUEST_DELAY = 1.0  # Delay between API requests (seconds)


def get_all_articles_with_summary() -> List[Dict]:
    """Summary'si olan tüm newsapi_articles makalelerini getir"""
    with get_db_cursor() as cur:
        query = """
            SELECT id, title, description, summary, url, published_at, source_name
            FROM newsapi_articles
            WHERE summary IS NOT NULL AND summary != ''
            ORDER BY id
        """
        cur.execute(query)
        return cur.fetchall()


def compare_summaries_with_llm(summary1: str, summary2: str, title1: str, title2: str) -> Optional[Dict]:
    """
    İki summary'yi LLM ile karşılaştır ve aynı konu olup olmadığını belirle
    Returns: {"is_same_topic": bool, "confidence": float, "reason": str} or None
    """
    prompt = f"""Compare these two article summaries and determine if they report the same news story or topic.

Article 1:
Title: {title1}
Summary: {summary1}

Article 2:
Title: {title2}
Summary: {summary2}

Are these two articles about the same news story or topic? Consider:
- Same event, same facts, same main points
- Different wording but same core story
- Same topic even if from different sources

Respond ONLY with valid JSON in this exact format:
{{
  "is_same_topic": true or false,
  "confidence": 0.0 to 1.0,
  "reason": "brief explanation in Turkish or English"
}}

Do not include any text outside the JSON."""

    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("  ERROR: OPENAI_API_KEY environment variable not set!")
            return None
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that compares article summaries. Always respond with ONLY valid JSON, no other text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            result = json.loads(result_text)
            # Validate structure
            if "is_same_topic" in result and "confidence" in result:
                return result
            else:
                print(f"    Warning: Invalid response structure: {result_text}")
                return None
        except json.JSONDecodeError as e:
            print(f"    Warning: Failed to parse JSON: {result_text}")
            # Try to extract JSON from text if wrapped
            try:
                # Find JSON object in text
                start = result_text.find('{')
                end = result_text.rfind('}') + 1
                if start >= 0 and end > start:
                    result = json.loads(result_text[start:end])
                    if "is_same_topic" in result and "confidence" in result:
                        return result
            except:
                pass
            return None
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def simple_text_similarity(text1: str, text2: str) -> float:
    """Basit text similarity hesapla (Jaccard similarity)"""
    if not text1 or not text2:
        return 0.0
    
    # Normalize: lowercase, remove punctuation
    import re
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def prefilter_candidates(article1: Dict, article2: Dict, min_similarity: float = 0.3) -> bool:
    """
    İki makalenin potansiyel duplicate olup olmadığını basit heuristics ile kontrol et
    Returns: True if should compare with LLM, False otherwise
    """
    summary1 = article1.get('summary', '')
    summary2 = article2.get('summary', '')
    
    if not summary1 or not summary2:
        return False
    
    # 1. Summary similarity (basit)
    summary_sim = simple_text_similarity(summary1, summary2)
    if summary_sim >= min_similarity:
        return True
    
    # 2. Title similarity
    title1 = article1.get('title', '') or ''
    title2 = article2.get('title', '') or ''
    if title1 and title2:
        title_sim = simple_text_similarity(title1, title2)
        if title_sim >= 0.5:  # Title'lar benzer ise kontrol et
            return True
    
    # 3. Summary uzunlukları benzer ve ilk kelimeler benzer
    len1, len2 = len(summary1), len(summary2)
    if len1 > 0 and len2 > 0:
        len_ratio = min(len1, len2) / max(len1, len2)
        if len_ratio >= 0.7:  # Uzunluklar benzer
            # İlk 50 karakteri karşılaştır
            first_words1 = summary1[:50].lower()
            first_words2 = summary2[:50].lower()
            if simple_text_similarity(first_words1, first_words2) >= 0.4:
                return True
    
    return False


def find_duplicate_groups(articles: List[Dict], min_confidence: float = 0.8) -> Tuple[List[List[Dict]], List[Dict]]:
    """
    Articles listesindeki duplicate'leri bul ve grupla
    Returns: (duplicate_groups, duplicate_pairs)
    """
    print(f"\nPre-filtering {len(articles)} articles...")
    
    # Pre-filter: Find candidate pairs
    candidate_pairs = []
    for i, article1 in enumerate(articles):
        for j, article2 in enumerate(articles[i+1:], start=i+1):
            if prefilter_candidates(article1, article2):
                candidate_pairs.append((i, j))
    
    print(f"Found {len(candidate_pairs)} candidate pairs to check with LLM.")
    print(f"(Reduced from {len(articles) * (len(articles) - 1) // 2} total pairs)\n")
    
    if not candidate_pairs:
        print("No candidate pairs found. No duplicates detected.")
        return [], []
    
    # Track which articles are duplicates
    duplicate_pairs = []
    processed = 0
    
    # Compare candidate pairs with LLM
    for i, j in candidate_pairs:
        article1 = articles[i]
        article2 = articles[j]
        processed += 1
        
        summary1 = article1['summary']
        summary2 = article2['summary']
        title1 = article1['title'] or 'No title'
        title2 = article2['title'] or 'No title'
        
        print(f"[{processed}/{len(candidate_pairs)}] Comparing ID {article1['id']} vs {article2['id']}...", end=' ')
        
        # LLM comparison
        result = compare_summaries_with_llm(summary1, summary2, title1, title2)
        
        if result and result.get('is_same_topic', False):
            confidence = result.get('confidence', 0.0)
            if confidence >= min_confidence:
                duplicate_pairs.append({
                    'article1_id': article1['id'],
                    'article2_id': article2['id'],
                    'confidence': confidence,
                    'reason': result.get('reason', ''),
                    'title1': title1,
                    'title2': title2,
                    'summary1': summary1[:200],
                    'summary2': summary2[:200],
                    'url1': article1.get('url', ''),
                    'url2': article2.get('url', ''),
                })
                print(f"✓ DUPLICATE (confidence: {confidence:.2f})")
            else:
                print(f"✗ Not duplicate (confidence: {confidence:.2f} < {min_confidence})")
        else:
            print("✗ Not duplicate")
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
    
    # Group duplicates using union-find approach
    groups = []
    article_to_group = {}
    
    for pair in duplicate_pairs:
        id1 = pair['article1_id']
        id2 = pair['article2_id']
        
        # Find or create groups
        group1_idx = article_to_group.get(id1)
        group2_idx = article_to_group.get(id2)
        
        if group1_idx is None and group2_idx is None:
            # Create new group
            new_group = [id1, id2]
            groups.append(new_group)
            article_to_group[id1] = len(groups) - 1
            article_to_group[id2] = len(groups) - 1
        elif group1_idx is not None and group2_idx is None:
            # Add id2 to group1
            groups[group1_idx].append(id2)
            article_to_group[id2] = group1_idx
        elif group1_idx is None and group2_idx is not None:
            # Add id1 to group2
            groups[group2_idx].append(id1)
            article_to_group[id1] = group2_idx
        else:
            # Merge groups if different
            if group1_idx != group2_idx:
                groups[group1_idx].extend(groups[group2_idx])
                for aid in groups[group2_idx]:
                    article_to_group[aid] = group1_idx
                groups[group2_idx] = []
    
    # Remove empty groups and convert IDs to full article objects
    duplicate_groups = []
    for group in groups:
        if group:
            group_articles = [a for a in articles if a['id'] in group]
            if len(group_articles) > 1:
                duplicate_groups.append(group_articles)
    
    return duplicate_groups, duplicate_pairs


def save_results_to_csv(duplicate_pairs: List[Dict], duplicate_groups: List[List[Dict]]):
    """Sonuçları CSV dosyasına kaydet"""
    # Create data directory if not exists
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    
    # Save duplicate pairs
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'article1_id', 'article2_id', 'confidence', 'reason',
            'title1', 'title2', 'summary1', 'summary2', 'url1', 'url2'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(duplicate_pairs)
    
    print(f"\n✓ Results saved to: {OUTPUT_CSV}")
    
    # Also save groups summary
    groups_csv = PROJECT_ROOT / "data" / "duplicate_groups_summary.csv"
    with open(groups_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['group_id', 'article_ids', 'count', 'titles']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, group in enumerate(duplicate_groups, 1):
            article_ids = [str(a['id']) for a in group]
            titles = ' | '.join([a.get('title', 'No title')[:50] for a in group])
            writer.writerow({
                'group_id': idx,
                'article_ids': ', '.join(article_ids),
                'count': len(group),
                'titles': titles
            })
    
    print(f"✓ Groups summary saved to: {groups_csv}")


def main():
    """Main function"""
    print("=" * 70)
    print("DUPLICATE DETECTION BY SUMMARY (LLM)")
    print("=" * 70)
    print()
    
    if not test_connection():
        print("ERROR: Cannot connect to database!")
        return
    
    # Summary'si olan tüm makaleleri getir
    print("Getting articles with summary from database...")
    articles = get_all_articles_with_summary()
    
    if not articles:
        print("No articles with summary found!")
        return
    
    print(f"Found {len(articles)} articles with summary.\n")
    
    if len(articles) < 2:
        print("Need at least 2 articles to compare!")
        return
    
    # Note: We use pre-filtering to reduce comparisons
    print("Note: Using pre-filtering to reduce LLM API calls.")
    print("Only potentially similar articles will be compared with LLM.\n")
    
    # Confirm before proceeding
    response = input("Proceed with duplicate detection? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Find duplicates
    duplicate_groups, duplicate_pairs = find_duplicate_groups(articles, min_confidence=0.8)
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total duplicate pairs found: {len(duplicate_pairs)}")
    print(f"Total duplicate groups: {len(duplicate_groups)}")
    print(f"Total duplicate articles: {sum(len(g) for g in duplicate_groups)}")
    print()
    
    # Show groups
    if duplicate_groups:
        print("Duplicate Groups:")
        for idx, group in enumerate(duplicate_groups, 1):
            print(f"\nGroup {idx} ({len(group)} articles):")
            for article in group:
                print(f"  - ID {article['id']}: {article.get('title', 'No title')[:60]}")
    
    # Save to CSV
    if duplicate_pairs:
        save_results_to_csv(duplicate_pairs, duplicate_groups)
    else:
        print("\nNo duplicates found!")
    
    print("\n" + "=" * 70)
    print("Analysis complete. Database was NOT modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()

