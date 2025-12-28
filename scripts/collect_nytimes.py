"""
CE49X Final Project - NYTimes API Article Collector

NYTimes Article Search API kullanarak CE ve AI keyword'lerini içeren makaleleri topla.
Her sorgu en az 1 CE + 1 AI keyword içermeli.

Requirements:
- Python 3.8+
- requests library
- trafilatura library (full text için)
- Valid NYTimes API key (get one free at https://developer.nytimes.com/)

Usage:
    python collect_nytimes.py [--target 500] [--days-back 365] [--min-len 800]

Make sure to set your NYTIMES_API_KEY environment variable.
"""

import os
import sys
import re
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
import time
from pathlib import Path

# Add parent directory to path for database imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check and import required libraries
try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is not installed.")
    print("Please install it using: pip install requests")
    sys.exit(1)

try:
    import trafilatura
except ImportError:
    print("ERROR: 'trafilatura' library is not installed.")
    print("Please install it using: pip install trafilatura")
    sys.exit(1)

try:
    from database.db_config import get_db_cursor, test_connection
except ImportError:
    print("ERROR: Database module not found.")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("WARNING: 'pandas' library is not installed.")
    print("CSV export will be disabled. Install with: pip install pandas")
    pd = None

# ============================================================================
# CONFIGURATION
# ============================================================================

# Output directory for CSV files
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# NYTimes API key - can also be set via environment variable NYTIMES_API_KEY
API_KEY = os.getenv("NYTIMES_API_KEY", "dLzrjIsGr2R4uGDnZLaGpp7vSoTAgaVaeoKb2wI7gHsSxenE")
NYTIMES_API_ID = "6dffaad5-6c5b-41a1-bc5b-04f93689a53e"

# NYTimes Article Search API endpoint
NYTIMES_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

# Search parameters
MAX_PAGES = 5  # Limit pages to save API quota (NYTimes API returns 10 articles per page)
REQUEST_DELAY = 3  # Delay between requests to respect rate limits (seconds) - increased for safety
RATE_LIMIT_WAIT = 3600  # Wait 1 hour if rate limit is hit (seconds)

# ============================================================================
# KEYWORD DEFINITIONS (same as collect_newsapi.py)
# ============================================================================

# Civil Engineering keywords
CE_KEYWORDS = [
    "construction",
    "structural",
    "geotechnical",
    "transportation",
    "infrastructure",
    "concrete",
    "bridge",
    "tunnel"
]

# AI keywords
AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "computer vision",
    "generative AI",
    "neural networks",
    "robotics",
    "automation"
]

# CE Synonyms - for search queries only (not for filtering)
CE_SYNONYMS = [
    "civil engineering",
    "building",
    "buildings",
    "construction industry",
    "structural engineering",
    "geotechnical engineering",
    "transportation engineering",
    "infrastructure development",
    "public works",
    "urban planning",
    "concrete structures",
    "reinforced concrete",
    "bridge construction",
    "tunnel construction",
    "construction technology",
    "construction management"
]

# AI Synonyms - for search queries only (not for filtering)
AI_SYNONYMS = [
    "AI",
    "machine intelligence",
    "deep learning",
    "ML",
    "neural network",
    "computer vision",
    "image recognition",
    "generative AI",
    "robotics",
    "robotic",
    "automation",
    "automated",
    "intelligent systems",
    "smart systems",
    "data science",
    "predictive analytics"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_search_queries() -> List[str]:
    """
    Generate search query combinations - each query must have at least 1 CE + 1 AI keyword.
    NYTimes API supports boolean operators (AND, OR) and phrase matching with quotes.
    
    Returns:
        List of search query strings
    """
    queries = []
    
    # Core combinations: each CE keyword with each AI keyword
    for ce_term in CE_KEYWORDS:
        for ai_term in AI_KEYWORDS:
            # Use quotes for multi-word terms
            if " " in ai_term:
                query = f'{ce_term} AND "{ai_term}"'
            else:
                query = f'{ce_term} AND {ai_term}'
            queries.append(query)
    
    # Broader queries with synonyms (for search flexibility)
    broader_queries = [
        # General CE + AI combinations
        '(construction OR "civil engineering" OR infrastructure OR structural OR geotechnical) AND ("artificial intelligence" OR "machine learning" OR AI OR "computer vision" OR "neural networks")',
        
        # Specific domain combinations
        '(bridge OR tunnel OR concrete OR "reinforced concrete") AND (AI OR automation OR robotics OR "machine learning")',
        
        # Transportation + AI
        '(transportation OR "transportation engineering" OR traffic OR highway) AND ("artificial intelligence" OR "machine learning" OR automation OR AI)',
        
        # Construction technology + AI
        '("construction technology" OR "construction management" OR "construction industry") AND (AI OR "machine learning" OR automation OR "intelligent systems")',
        
        # Infrastructure + AI
        '(infrastructure OR "public works" OR "urban planning" OR "infrastructure development") AND ("artificial intelligence" OR "machine learning" OR "smart systems" OR AI)',
        
        # Structural + AI
        '("structural engineering" OR "structural design" OR structural) AND ("machine learning" OR "neural networks" OR AI OR "deep learning")',
        
        # Geotechnical + AI
        '("geotechnical engineering" OR "soil mechanics" OR geotechnical) AND ("machine learning" OR AI OR "predictive analytics" OR "artificial intelligence")',
        
        # Building + AI
        '(building OR buildings OR "construction site" OR "construction project") AND (AI OR "machine learning" OR automation OR robotics OR "artificial intelligence")',
        
        # General AI in construction context
        '("artificial intelligence" OR "machine learning" OR "deep learning" OR "computer vision" OR AI OR ML) AND (construction OR "civil engineering" OR infrastructure OR "construction industry")',
        
        # Automation in construction
        '(automation OR automated OR autonomous OR "intelligent automation") AND (construction OR infrastructure OR "construction industry" OR "civil engineering")',
        
        # Robotics in construction
        '(robotics OR robotic OR robot OR robots) AND (construction OR infrastructure OR "civil engineering" OR building)',
        
        # Neural networks in civil engineering
        '("neural networks" OR "neural network" OR "deep learning" OR "machine learning") AND ("civil engineering" OR construction OR infrastructure OR structural OR geotechnical)'
    ]
    
    queries.extend(broader_queries)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries


def fetch_articles_page(query: str, page: int, begin_date: str, end_date: str, api_key: str) -> Dict:
    """
    Fetch a single page of articles from NYTimes API.
    
    Args:
        query: Search query string
        page: Page number (0-indexed for NYTimes)
        begin_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format
        api_key: NYTimes API key
        
    Returns:
        JSON response from NYTimes API as a dictionary
    """
    params = {
        "q": query,
        "begin_date": begin_date,
        "end_date": end_date,
        "page": page,
        "api-key": api_key,
        "sort": "newest"  # Sort by newest first
    }
    
    try:
        response = requests.get(NYTIMES_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            # Check for rate limit (429)
            if e.response.status_code == 429:
                try:
                    error_data = e.response.json()
                    fault = error_data.get("fault", {})
                    if "QuotaViolation" in str(fault):
                        print(f"    [RATE LIMIT] Günlük limit aşıldı!")
                        print(f"    [INFO] Yarın tekrar deneyin veya NewsAPI kullanın")
                        return {"rate_limit": True}
                except:
                    pass
            try:
                error_data = e.response.json()
                print(f"    API Error: {error_data}")
            except:
                print(f"    HTTP Status: {e.response.status_code}")
        else:
            print(f"    Error fetching page {page} for query '{query}': {e}")
        return None


def find_keywords_in_text(text: str, keywords: List[str]) -> List[str]:
    """Find which keywords appear in the text (case-insensitive)."""
    if not text:
        return []
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            found.append(keyword)
    
    return list(set(found))  # Remove duplicates


def has_both_ai_and_ce(text: str) -> Tuple[bool, List[str], List[str]]:
    """
    Check if text contains both AI and CE keywords (using only base keywords for consistency).
    Both keyword types must be present.
    
    Args:
        text: Text to check
        
    Returns:
        Tuple of (has_both, ai_keywords_found, ce_keywords_found)
    """
    if not text:
        return (False, [], [])
    
    # Use only base keywords for filtering (not synonyms)
    ai_found = find_keywords_in_text(text, AI_KEYWORDS)
    ce_found = find_keywords_in_text(text, CE_KEYWORDS)
    
    has_both = len(ai_found) >= 1 and len(ce_found) >= 1
    
    return (has_both, ai_found, ce_found)


def fetch_full_text(url: str) -> Optional[str]:
    """Fetch full text content from article URL using trafilatura."""
    try:
        html = requests.get(
            url,
            timeout=30,
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ).text
        
        full_text = trafilatura.extract(html, url=url, include_comments=False)
        return full_text
    except Exception as e:
        return None


def extract_article_metadata(article: Dict) -> Dict:
    """
    Extract relevant metadata from a NYTimes API article object.
    
    Args:
        article: Article dictionary from NYTimes API response
        
    Returns:
        Dictionary with extracted metadata fields
    """
    headline = article.get("headline", {})
    title = headline.get("main", headline.get("print_headline", ""))
    
    # Get abstract/snippet
    abstract = article.get("abstract", "")
    lead_paragraph = article.get("lead_paragraph", "")
    snippet = abstract or lead_paragraph
    
    # Get publication date
    pub_date = article.get("pub_date", "")
    
    # Get URL
    web_url = article.get("web_url", "")
    
    # Get source (NYTimes sections)
    section_name = article.get("section_name", "")
    subsection_name = article.get("subsection_name", "")
    source = "NYTimes"
    if section_name:
        source = f"NYTimes - {section_name}"
    if subsection_name:
        source = f"NYTimes - {section_name}/{subsection_name}"
    
    return {
        "title": title,
        "publication_date": pub_date,
        "source": source,
        "url": web_url,
        "description": snippet,
        "abstract": abstract,
        "lead_paragraph": lead_paragraph
    }


def collect_articles_for_query(
    query: str,
    begin_date: str,
    end_date: str,
    api_key: str,
    min_length: int = 800,
    existing_urls: Set[str] = None,
    strict_filter: bool = True
) -> List[Dict]:
    """
    Collect all articles for a given search query, handling pagination.
    
    Args:
        query: Search query string
        begin_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format
        api_key: NYTimes API key
        min_length: Minimum text length for articles
        existing_urls: Set of URLs already in database
        
    Returns:
        List of article dictionaries with full text and keyword matches
    """
    if existing_urls is None:
        existing_urls = set()
    
    articles = []
    page = 0  # NYTimes uses 0-indexed pages
    total_results = None
    processed = 0
    filtered_out = 0
    
    print(f"  Collecting articles for query: '{query}'")
    
    while page < MAX_PAGES:
        # Fetch one page
        response_data = fetch_articles_page(query, page, begin_date, end_date, api_key)
        
        if response_data is None:
            break
        
        # Check for API errors
        if "fault" in response_data:
            error_message = response_data.get("fault", {}).get("faultstring", "Unknown error")
            print(f"    API Error: {error_message}")
            break
        
        # Get response data
        response_obj = response_data.get("response", {})
        
        # Get total results (only available on first page)
        if total_results is None:
            meta = response_obj.get("meta", {})
            total_results = meta.get("hits", 0)
            print(f"    Total results available: {total_results}")
        
        # Extract articles from this page
        page_articles = response_obj.get("docs", [])
        
        if not page_articles:
            print(f"    No more articles found (stopped at page {page})")
            break
        
        # Process each article
        for article in page_articles:
            url = article.get("web_url", "")
            if not url or url in existing_urls:
                continue
            
            processed += 1
            if processed % 10 == 0:
                print(f"    Processed {processed} articles, found {len(articles)} valid, filtered {filtered_out}")
            
            # Extract metadata
            metadata = extract_article_metadata(article)
            
            # Combine title, abstract, and lead paragraph for keyword checking
            title_desc = f"{metadata['title']} {metadata.get('abstract', '')} {metadata.get('lead_paragraph', '')}".strip()
            
            # STRICT FILTERING: Check if title/description has both keywords (saves API calls)
            has_both_title_desc, ai_found_title, ce_found_title = has_both_ai_and_ce(title_desc)
            
            if strict_filter:
                # Strict mode: Both keywords must be in title/description
                if not has_both_title_desc:
                    filtered_out += 1
                    continue
                # If found in title/desc, use those keywords
                ai_found = ai_found_title
                ce_found = ce_found_title
                combined_text = title_desc
            else:
                # Flexible mode: Check full text if not in title/desc
                has_both = has_both_title_desc
                ai_found = ai_found_title
                ce_found = ce_found_title
                combined_text = title_desc
                
                if not has_both:
                    # Try fetching full text if available
                    full_text = fetch_full_text(url)
                    if full_text:
                        combined_text = f"{combined_text} {full_text}".strip()
                        has_both, ai_found, ce_found = has_both_ai_and_ce(combined_text)
                        metadata['full_text'] = full_text
                    else:
                        metadata['full_text'] = None
                    
                    if not has_both:
                        filtered_out += 1
                        continue
            
            # Check minimum length
            if metadata.get('full_text'):
                if len(metadata['full_text']) < min_length:
                    filtered_out += 1
                    continue
            elif len(combined_text) < min_length:
                # Try to fetch full text
                full_text = fetch_full_text(url)
                if full_text and len(full_text) >= min_length:
                    metadata['full_text'] = full_text
                else:
                    filtered_out += 1
                    continue
            
            # Add keyword information
            metadata['ai_keywords_found'] = ai_found
            metadata['ce_keywords_found'] = ce_found
            metadata['has_both'] = has_both
            
            articles.append(metadata)
            existing_urls.add(url)
        
        print(f"    Page {page}: Processed {processed} articles, found {len(articles)} valid (filtered: {filtered_out})")
        
        # Check if we've reached the end
        if len(page_articles) < 10:  # Last page has fewer than 10 articles
            break
        
        page += 1
        
        # Rate limiting: delay between requests
        time.sleep(REQUEST_DELAY)
    
    return articles


def create_filtered_table_if_not_exists():
    """Create filtered_ai_ce_articles table if it doesn't exist."""
    with get_db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS filtered_ai_ce_articles (
                id SERIAL PRIMARY KEY,
                article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT,
                description TEXT,
                full_text TEXT,
                source TEXT,
                url TEXT,
                published_at TIMESTAMP,
                ai_keywords_found TEXT[],
                ce_keywords_found TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id)
            )
        """)


def save_to_database(articles: List[Dict]) -> Tuple[int, int]:
    """
    Save articles to PostgreSQL database (both articles and filtered_ai_ce_articles tables).
    
    Args:
        articles: List of article dictionaries with full text and keywords
        
    Returns:
        Tuple of (inserted_articles, inserted_filtered)
    """
    if not articles:
        return (0, 0)
    
    if not test_connection():
        print("ERROR: Cannot connect to database!")
        return (0, 0)
    
    # Ensure filtered table exists
    create_filtered_table_if_not_exists()
    
    inserted_articles = 0
    inserted_filtered = 0
    skipped = 0
    
    with get_db_cursor() as cur:
        # Get existing URLs
        cur.execute("SELECT url FROM articles")
        existing_urls = {row['url'] for row in cur.fetchall()}
        
        for i, article in enumerate(articles, 1):
            url = article.get("url", "")
            if not url or url in existing_urls:
                skipped += 1
                continue
            
            title = article.get("title", "")
            description = article.get("description", "")
            source = article.get("source", "")
            published_at = article.get("publication_date", "")
            full_text = article.get("full_text", "")
            ai_keywords = article.get("ai_keywords_found", [])
            ce_keywords = article.get("ce_keywords_found", [])
            
            # Parse published_at (NYTimes format: "2024-01-15T10:30:00+0000")
            published_iso = None
            if published_at:
                try:
                    # Remove timezone info for parsing
                    dt_str = published_at.split('+')[0].split('T')[0] + 'T' + published_at.split('T')[1].split('+')[0].split('-')[0]
                    dt_obj = datetime.fromisoformat(published_at.replace('+0000', '+00:00').replace('Z', '+00:00'))
                    published_iso = dt_obj.isoformat()
                except Exception:
                    try:
                        dt_obj = datetime.fromisoformat(published_at.split('+')[0])
                        published_iso = dt_obj.isoformat()
                    except Exception:
                        pass
            
            try:
                # Insert into articles table
                cur.execute("""
                    INSERT INTO articles
                    (title, published_at, source, url, content, description, full_text, retrieved_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                """, (
                    title,
                    published_iso if published_iso else None,
                    source,
                    url,
                    full_text[:500] if full_text else None,
                    description,
                    full_text,
                    datetime.now().isoformat()
                ))
                
                result = cur.fetchone()
                if result:
                    article_id = result['id']
                    inserted_articles += 1
                    existing_urls.add(url)
                    
                    # Insert into filtered_ai_ce_articles table
                    try:
                        cur.execute("""
                            INSERT INTO filtered_ai_ce_articles
                            (article_id, title, content, description, full_text, source, url, published_at, ai_keywords_found, ce_keywords_found)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (article_id) DO NOTHING
                        """, (
                            article_id,
                            title,
                            full_text[:500] if full_text else None,
                            description,
                            full_text,
                            source,
                            url,
                            published_iso if published_iso else None,
                            ai_keywords,
                            ce_keywords
                        ))
                        if cur.rowcount > 0:
                            inserted_filtered += 1
                    except Exception as e:
                        print(f"  [WARNING] filtered_ai_ce_articles'a eklenemedi: {e}")
                    
                    if inserted_articles % 10 == 0 or inserted_articles == 1:
                        print(f"  [{inserted_articles}/{len(articles)}] Database'e kaydedildi: {title[:60]}...")
                else:
                    skipped += 1
                    
            except Exception as e:
                print(f"ERROR: {url} kaydedilemedi: {e}")
                skipped += 1
                continue
    
    return (inserted_articles, inserted_filtered)


def save_to_csv(articles: List[Dict], output_path: Path):
    """
    Save articles to a CSV file.
    
    Args:
        articles: List of article dictionaries
        output_path: Path to output CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not articles:
        print("No articles to save to CSV.")
        return False
    
    if pd is None:
        print("WARNING: pandas not installed, skipping CSV export.")
        return False
    
    try:
        # Prepare data for CSV
        csv_data = []
        for article in articles:
            csv_article = {
                "title": article.get("title", ""),
                "publication_date": article.get("publication_date", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "description": article.get("description", ""),
                "ai_keywords_found": ", ".join(article.get("ai_keywords_found", [])),
                "ce_keywords_found": ", ".join(article.get("ce_keywords_found", []))
            }
            csv_data.append(csv_article)
        
        # Create DataFrame
        df = pd.DataFrame(csv_data)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"[OK] Saved {len(articles)} articles to {output_path}")
        return True
        
    except PermissionError:
        print(f"[ERROR] Permission denied when writing to {output_path}")
        print(f"  Please close the file if it's open in Excel or another program.")
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to save to {output_path}: {e}")
        return False


def main():
    """Main function to orchestrate the article collection process."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NYTimes API ile CE ve AI keyword'lerini içeren makaleleri topla"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=None,
        help="Hedef makale sayısı (default: None, tüm bulunanları topla)"
    )
    parser.add_argument(
        "--days-back",
        type=int,
        default=365,
        help="Kaç gün geriye gidilecek (default: 365, NYTimes allows up to 1 year)"
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=800,
        help="Minimum metin uzunluğu (default: 800)"
    )
    parser.add_argument(
        "--no-db",
        action="store_true",
        help="Database'e kaydetme (sadece CSV)"
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        default=True,  # Default olarak CSV'ye kaydet
        help="CSV dosyasına kaydet (default: True)"
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        default=None,
        help="CSV dosya yolu (default: data/nytimes_articles.csv)"
    )
    parser.add_argument(
        "--strict-filter",
        action="store_true",
        default=True,  # Default olarak strict filtreleme
        help="Sıkı filtreleme: title/description'da her iki keyword grubu da olmalı (default: True)"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CE49X Final Project - NYTimes API Article Collection")
    print("=" * 70)
    print()
    print("Özellikler:")
    print("  • Her sorgu en az 1 CE + 1 AI keyword içeriyor")
    print("  • Synonym'ler arama sorgularında kullanılıyor (esneklik için)")
    print("  • Filtreleme sadece base keyword'lerle yapılıyor (trend analizi için tutarlılık)")
    print("  • Hem AI hem CE keyword'leri içeren makaleler filtreleniyor")
    if args.strict_filter:
        print("  • [STRICT MODE] Title/description'da her iki keyword grubu da olmalı (API limit koruması)")
    print()
    
    # Check API key
    if not API_KEY:
        print("ERROR: NYTimes API key not found!")
        print("Please set the NYTIMES_API_KEY environment variable.")
        print("Get your free API key at: https://developer.nytimes.com/")
        return
    
    # Check database connection if needed
    if not args.no_db:
        if not test_connection():
            print("ERROR: Cannot connect to database!")
            print("Make sure Docker containers are running: docker-compose up -d")
            return
    
    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=args.days_back)
    
    begin_date = from_date.strftime("%Y%m%d")
    end_date = to_date.strftime("%Y%m%d")
    
    print(f"Date range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print(f"Minimum text length: {args.min_len}")
    if args.target:
        print(f"Target articles: {args.target}")
    print()
    
    # Get existing URLs from database
    existing_urls = set()
    if not args.no_db:
        with get_db_cursor() as cur:
            cur.execute("SELECT url FROM articles")
            existing_urls = {row['url'] for row in cur.fetchall()}
        print(f"Mevcut database'de: {len(existing_urls)} makale var")
        print()
    
    # Generate search queries (limit to save API quota)
    all_queries = create_search_queries()
    # Limit queries to save API quota - prioritize core combinations
    # Take first 20 core queries (CE x AI combinations) + 5 broader queries
    core_queries = [q for q in all_queries if ' AND "' in q or (' AND ' in q and not '(' in q)][:20]
    broader_queries = [q for q in all_queries if q not in core_queries][:5]
    queries = core_queries + broader_queries
    
    print(f"Generated {len(queries)} search queries (API limit koruması için {len(all_queries)}'den sınırlandırıldı)")
    print(f"  Core queries: {len(core_queries)}")
    print(f"  Broader queries: {len(broader_queries)}")
    print()
    
    # Collect articles for each query
    all_articles = []
    
    for i, query in enumerate(queries, 1):
        if args.target and len(all_articles) >= args.target:
            print(f"\nHedef sayıya ulaşıldı: {len(all_articles)}/{args.target}")
            break
        
        print(f"Query {i}/{len(queries)}")
        articles = collect_articles_for_query(
            query,
            begin_date,
            end_date,
            API_KEY,
            min_length=args.min_len,
            existing_urls=existing_urls,
            strict_filter=args.strict_filter
        )
        all_articles.extend(articles)
        print(f"  Total articles collected so far: {len(all_articles)}")
        print()
        
        # Rate limiting between queries
        time.sleep(REQUEST_DELAY)
    
    # Remove duplicates (just in case)
    print("Removing duplicate articles...")
    print(f"  Before deduplication: {len(all_articles)} articles")
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    print(f"  After deduplication: {len(unique_articles)} articles")
    print()
    
    if args.target and len(unique_articles) > args.target:
        unique_articles = unique_articles[:args.target]
        print(f"  Limited to target: {len(unique_articles)} articles")
        print()
    
    # Save to database
    if not args.no_db:
        print("Saving articles to database...")
        inserted_articles, inserted_filtered = save_to_database(unique_articles)
        print(f"  [OK] Articles table: {inserted_articles} inserted")
        print(f"  [OK] Filtered table: {inserted_filtered} inserted")
        print()
        
        # Final count
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM articles")
            total_articles = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM filtered_ai_ce_articles")
            total_filtered = cur.fetchone()['count']
        
        print("=" * 70)
        print("İŞLEM TAMAMLANDI")
        print("=" * 70)
        print(f"Yeni eklenen: {inserted_articles} makale")
        print(f"Database'de toplam makale: {total_articles}")
        print(f"Filtrelenmiş makale: {total_filtered}")
        print("=" * 70 + "\n")
    else:
        print(f"\n[TEST MODE] {len(unique_articles)} makale bulundu (database'e kaydedilmedi)")
    
    # Save to CSV (default behavior - saves API limit)
    if args.csv:
        if unique_articles:
            # Determine output path
            if args.csv_path:
                csv_path = Path(args.csv_path)
            else:
                # Create timestamped filename to avoid overwriting
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_path = PROJECT_ROOT / "data" / f"nytimes_articles_{timestamp}.csv"
            
            print("Saving articles to CSV...")
            success = save_to_csv(unique_articles, csv_path)
            if success:
                print(f"[OK] CSV saved: {csv_path}")
            print()
        else:
            print("[WARNING] No articles to save to CSV")
            print()


if __name__ == "__main__":
    main()

