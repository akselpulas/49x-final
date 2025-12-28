"""
CE49X Final Project - Task 1: Data Collection
NewsAPI Article Collector

This script collects news articles related to Civil Engineering and Artificial Intelligence
using the NewsAPI "everything" endpoint. It collects metadata only (title, publication_date,
source, url, description) and saves the results to a CSV file.

Author: [Your Name]
Course: CE49X - Introduction to Data Science for Civil Engineering
Date: Fall 2025

Requirements:
- Python 3.8+
- requests library
- pandas library
- Valid NewsAPI key (get one free at https://newsapi.org/)

Usage:
    python collect_newsapi.py

Make sure to set your NEWSAPI_KEY environment variable or modify the API_KEY variable below.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
import time
from pathlib import Path

# Check and import required libraries
try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is not installed.")
    print("Please install it using: pip install requests")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: 'pandas' library is not installed.")
    print("Please install it using: pip install pandas")
    sys.exit(1)

try:
    import trafilatura
except ImportError:
    print("ERROR: 'trafilatura' library is not installed.")
    print("Please install it using: pip install trafilatura")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

# NewsAPI keys - can also be set via environment variable NEWSAPI_KEY
# Get your free API key at: https://newsapi.org/register
API_KEY_1 = os.getenv("NEWSAPI_KEY_1", "9005640feba648b991e3b028bd2dbc5f")  # First key (queries 1-24)
API_KEY_2 = os.getenv("NEWSAPI_KEY_2", "6a13e6c421694262985150291959e9d4")  # Second key (queries 25+)
SWITCH_QUERY_NUMBER = 25  # Switch to second key after this query number
SWITCH_QUERY_NUMBER = 25  # Switch to second key after this query number

# NewsAPI endpoint
NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Output directory and file (relative to project root)
# This assumes the script is in the scripts/ subdirectory
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR_RAW = PROJECT_ROOT / "data_raw"
OUTPUT_DIR_DATA = PROJECT_ROOT / "data"
OUTPUT_FILE_RAW = "newsapi_articles.csv"
OUTPUT_FILE_DATA = "articles.csv"

# Search parameters
LANGUAGE = "en"  # English only
DAYS_BACK = 30  # NewsAPI free tier allows up to 1 month of historical data
REQUEST_DELAY = 0.5  # Delay between requests to respect rate limits (seconds) - reduced for speed

# NewsAPI Rate Limits (Free Tier)
MAX_REQUESTS_PER_DAY = 100  # Free tier limit: 100 requests per day
REQUESTS_PER_PAGE = 1  # Each page fetch = 1 request
MIN_PAGES_PER_QUERY = 1  # Minimum pages to fetch per query (to ensure coverage)
MAX_PAGES_PER_QUERY = 3  # Maximum pages per query (to distribute limit evenly)

# ============================================================================
# KEYWORD DEFINITIONS
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_search_queries() -> List[str]:
    """
    Generate comprehensive search query combinations for maximum article coverage.
    
    NewsAPI supports boolean operators (AND, OR) and phrase matching with quotes.
    We create queries that combine CE terms with AI terms in various ways.
    
    Returns:
        List of search query strings
    """
    queries = []
    
    # Core combinations: each CE keyword with each AI keyword (56 queries)
    for ce_term in CE_KEYWORDS:
        for ai_term in AI_KEYWORDS:
            # Use quotes for multi-word terms to ensure exact phrase matching
            if " " in ai_term:
                query = f'{ce_term} AND "{ai_term}"'
            else:
                query = f'{ce_term} AND {ai_term}'
            queries.append(query)
    
    # Broader queries with OR combinations for more coverage
    broader_queries = [
        # General CE + AI combinations
        '("civil engineering" OR construction OR infrastructure OR structural OR geotechnical) AND ("artificial intelligence" OR "machine learning" OR "computer vision" OR AI OR "neural networks")',
        
        # Construction + AI (various)
        '(construction OR "construction industry" OR "construction site" OR "construction project") AND ("artificial intelligence" OR "machine learning" OR AI OR automation OR robotics)',
        
        # Infrastructure + AI
        '(infrastructure OR "infrastructure development" OR "public works" OR "urban planning") AND ("artificial intelligence" OR "machine learning" OR "smart systems" OR AI)',
        
        # Structural + AI
        '("structural engineering" OR "structural design" OR "structural analysis" OR structural) AND ("machine learning" OR "neural networks" OR AI OR "deep learning" OR "artificial intelligence")',
        
        # Transportation + AI
        '(transportation OR "transportation engineering" OR traffic OR highway OR road) AND ("artificial intelligence" OR "machine learning" OR automation OR AI)',
        
        # Geotechnical + AI
        '("geotechnical engineering" OR "soil mechanics" OR geotechnical OR foundation) AND ("machine learning" OR AI OR "predictive analytics" OR "artificial intelligence")',
        
        # Concrete + AI
        '(concrete OR "reinforced concrete" OR "concrete structures" OR "precast concrete") AND ("artificial intelligence" OR "machine learning" OR AI OR automation)',
        
        # Bridge + AI
        '(bridge OR "bridge construction" OR "bridge design" OR bridges) AND ("artificial intelligence" OR "machine learning" OR AI OR automation OR robotics)',
        
        # Tunnel + AI
        '(tunnel OR "tunnel construction" OR tunneling OR tunnels) AND ("artificial intelligence" OR "machine learning" OR AI OR automation)',
        
        # Building + AI
        '(building OR buildings OR "construction site" OR "construction project") AND (AI OR "machine learning" OR automation OR robotics OR "artificial intelligence")',
        
        # General AI in construction context
        '("artificial intelligence" OR "machine learning" OR "deep learning" OR "computer vision" OR AI OR ML) AND (construction OR "civil engineering" OR infrastructure OR "construction industry")',
        
        # Automation in construction
        '(automation OR automated OR autonomous OR "intelligent automation") AND (construction OR infrastructure OR "construction industry" OR "civil engineering")',
        
        # Robotics in construction
        '(robotics OR robotic OR robot OR robots) AND (construction OR infrastructure OR "civil engineering" OR building)',
        
        # Neural networks in civil engineering
        '("neural networks" OR "neural network" OR "deep learning" OR "machine learning") AND ("civil engineering" OR construction OR infrastructure OR structural OR geotechnical)',
        
        # Computer vision in construction
        '("computer vision" OR "image recognition" OR "object detection") AND (construction OR infrastructure OR "civil engineering" OR building)',
        
        # Generative AI in construction
        '("generative AI" OR "generative artificial intelligence" OR "gen AI") AND (construction OR infrastructure OR "civil engineering" OR building)',
        
        # Smart infrastructure
        '("smart infrastructure" OR "intelligent infrastructure" OR "smart cities") AND (AI OR "artificial intelligence" OR "machine learning")',
        
        # Construction technology + AI
        '("construction technology" OR "construction management" OR "project management") AND (AI OR "machine learning" OR automation OR "intelligent systems")',
        
        # Data centers + infrastructure (AI related)
        '("data center" OR "data centres" OR "data centers") AND (construction OR infrastructure) AND (AI OR "artificial intelligence")',
        
        # Energy infrastructure + AI
        '(("energy infrastructure" OR "power infrastructure" OR "renewable energy") AND construction) AND (AI OR "artificial intelligence" OR "machine learning")'
    ]
    
    queries.extend(broader_queries)
    
    return queries


def fetch_articles_page(query: str, page: int, from_date: str, api_key: str) -> Dict:
    """
    Fetch a single page of articles from NewsAPI.
    
    Args:
        query: Search query string
        page: Page number (1-indexed)
        from_date: Start date in YYYY-MM-DD format
        api_key: NewsAPI API key
        
    Returns:
        JSON response from NewsAPI as a dictionary
    """
    params = {
        "q": query,
        "language": LANGUAGE,
        "from": from_date,
        "sortBy": "publishedAt",  # Sort by publication date
        "pageSize": 100,  # Maximum articles per page (NewsAPI limit)
        "page": page,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(NEWSAPI_URL, params=params, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page} for query '{query}': {e}")
        return None


def find_keywords_in_text(text: str, keywords: List[str]) -> List[str]:
    """Find which keywords appear in the text (case-insensitive)."""
    if not text:
        return []
    
    text_lower = str(text).lower()
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
            timeout=10,  # Reduced timeout for faster skipping of slow sites
            headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ).text
        
        full_text = trafilatura.extract(html, url=url, include_comments=False)
        return full_text
    except Exception as e:
        return None


def extract_article_metadata(article: Dict) -> Dict:
    """
    Extract relevant metadata from a NewsAPI article object.
    
    Args:
        article: Article dictionary from NewsAPI response
        
    Returns:
        Dictionary with extracted metadata fields
    """
    return {
        "title": article.get("title", ""),
        "publication_date": article.get("publishedAt", ""),
        "source": article.get("source", {}).get("name", ""),
        "url": article.get("url", ""),
        "description": article.get("description", ""),
        "content": article.get("content", "")  # NewsAPI sometimes provides content
    }


def collect_articles_for_query(
    query: str, 
    from_date: str, 
    api_key: str,
    min_length: int = 500,
    strict_filter: bool = True,
    existing_urls: Set[str] = None,
    max_pages: int = MAX_PAGES_PER_QUERY  # Dynamic page limit
) -> List[Dict]:
    """
    Collect all articles for a given search query, handling pagination and strict filtering.
    
    Args:
        query: Search query string
        from_date: Start date in YYYY-MM-DD format
        api_key: NewsAPI API key
        min_length: Minimum text length for articles
        strict_filter: If True, both keywords must be in title/description
        existing_urls: Set of URLs already collected
        max_pages: Maximum pages to fetch for this query (to distribute API limit)
        
    Returns:
        List of article metadata dictionaries with keywords
    """
    if existing_urls is None:
        existing_urls = set()
    
    articles = []
    page = 1
    total_results = None
    processed = 0
    filtered_out = 0
    
    print(f"  Collecting articles for query: '{query}' (max {max_pages} pages)")
    
    while page <= max_pages:
        # Fetch one page
        response_data = fetch_articles_page(query, page, from_date, api_key)
        
        if response_data is None:
            break
        
        # Check for API errors
        if response_data.get("status") != "ok":
            error_message = response_data.get("message", "Unknown error")
            print(f"    API Error: {error_message}")
            if "rate limit" in error_message.lower() or "429" in str(response_data):
                print("    [RATE LIMIT] NewsAPI rate limit reached!")
                break
            break
        
        # Get total results (only available on first page)
        if total_results is None:
            total_results = response_data.get("totalResults", 0)
            print(f"    Total results available: {total_results}")
        
        # Extract articles from this page
        page_articles = response_data.get("articles", [])
        
        if not page_articles:
            print(f"    No more articles found (stopped at page {page})")
            break
        
        # Process each article with strict filtering
        for article in page_articles:
            url = article.get("url", "")
            if not url:
                continue
            
            # Normalize URL for duplicate checking
            normalized_url = normalize_url(url)
            if normalized_url in existing_urls:
                continue
            
            processed += 1
            if processed % 50 == 0:  # Less frequent updates for speed
                print(f"    Processed {processed} articles, found {len(articles)} valid, filtered {filtered_out}")
            
            # Extract metadata
            metadata = extract_article_metadata(article)
            
            # Combine title, description, and content for keyword checking
            title_desc = f"{metadata['title']} {metadata.get('description', '')} {metadata.get('content', '')}".strip()
            
            # STRICT FILTERING: Check if title/description has both keywords (saves API calls)
            has_both_title_desc, ai_found_title, ce_found_title = has_both_ai_and_ce(title_desc)
            
            if strict_filter:
                # Strict mode: Both keywords must be in title/description/content
                # Try content field first (faster than fetching full text)
                if not has_both_title_desc:
                    # Check content field if available
                    content = metadata.get('content', '')
                    if content:
                        combined_check = f"{title_desc} {content}".strip()
                        has_both_content, ai_content, ce_content = has_both_ai_and_ce(combined_check)
                        if has_both_content:
                            ai_found = ai_content
                            ce_found = ce_content
                            combined_text = combined_check
                        else:
                            # Try fetching full text for more articles (but limit to avoid slowness)
                            # Only fetch if we haven't found many articles yet
                            if len(articles) < 50 or processed <= 20:  # Fetch for first 20 articles or if we need more
                                full_text = fetch_full_text(url)
                                if full_text:
                                    combined_text = f"{title_desc} {full_text}".strip()
                                    has_both_full, ai_found, ce_found = has_both_ai_and_ce(combined_text)
                                    if not has_both_full:
                                        filtered_out += 1
                                        continue
                                else:
                                    filtered_out += 1
                                    continue
                            else:
                                filtered_out += 1
                                continue
                    else:
                        # No content field, try fetching full text (but limit)
                        if len(articles) < 50 or processed <= 20:
                            full_text = fetch_full_text(url)
                            if full_text:
                                combined_text = f"{title_desc} {full_text}".strip()
                                has_both_full, ai_found, ce_found = has_both_ai_and_ce(combined_text)
                                if not has_both_full:
                                    filtered_out += 1
                                    continue
                            else:
                                filtered_out += 1
                                continue
                        else:
                            filtered_out += 1
                            continue
                else:
                    # Found in title/desc, use those keywords
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
            
            # Check minimum length (more flexible)
            # If we have both keywords, be more lenient with length
            if len(combined_text) < min_length:
                # If it's very short (< 200), definitely skip
                if len(combined_text) < 200:
                    filtered_out += 1
                    continue
                # If it's between 200-500, only skip if we already have many articles
                elif len(combined_text) >= 200 and len(articles) > 100:
                    filtered_out += 1
                    continue
                # Otherwise, accept it (we need more articles)
            
            # Add keyword information
            metadata['ai_keywords_found'] = ai_found
            metadata['ce_keywords_found'] = ce_found
            metadata['has_both'] = True
            
            articles.append(metadata)
            # Add normalized URL to prevent duplicates
            existing_urls.add(normalized_url)
        
        print(f"    Page {page}: Processed {processed} articles, found {len(articles)} valid (filtered: {filtered_out})")
        
        # Check if we've reached the end
        if len(page_articles) < 100:  # Last page has fewer than 100 articles
            break
        
        page += 1
        
        # Rate limiting: delay between requests
        time.sleep(REQUEST_DELAY)
    
    return articles


def normalize_url(url: str) -> str:
    """
    Normalize URL for duplicate detection.
    Removes trailing slashes, query parameters, fragments, and converts to lowercase.
    
    Args:
        url: URL string to normalize
        
    Returns:
        Normalized URL string
    """
    if not url:
        return ""
    
    # Remove fragments and query parameters for duplicate detection
    # (same article might have different tracking parameters)
    url = url.split('#')[0].split('?')[0]
    
    # Remove trailing slash
    url = url.rstrip('/')
    
    # Convert to lowercase for case-insensitive comparison
    url = url.lower()
    
    return url


def normalize_title(title: str) -> str:
    """
    Normalize title for duplicate detection.
    Removes extra whitespace, converts to lowercase, and removes special characters.
    
    Args:
        title: Title string to normalize
        
    Returns:
        Normalized title string
    """
    if not title:
        return ""
    
    # Convert to lowercase
    title = title.lower()
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Remove common punctuation that might differ
    title = title.replace('"', '').replace("'", '').replace('`', '')
    
    return title


def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """
    Remove duplicate articles based on URL and title.
    Uses normalized URLs and titles for better duplicate detection.
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        List of unique articles (by URL and title)
    """
    seen_urls: Set[str] = set()
    seen_titles: Set[str] = set()
    unique_articles = []
    duplicate_count = 0
    
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        
        # Normalize for comparison
        normalized_url = normalize_url(url)
        normalized_title = normalize_title(title)
        
        # Check for duplicates by URL or title
        is_duplicate = False
        
        if normalized_url and normalized_url in seen_urls:
            is_duplicate = True
        elif normalized_title and normalized_title in seen_titles:
            # Only check title if URL is missing or very short
            # (some articles might have same title but different URLs)
            if not normalized_url or len(normalized_url) < 10:
                is_duplicate = True
        
        if not is_duplicate:
            if normalized_url:
                seen_urls.add(normalized_url)
            if normalized_title:
                seen_titles.add(normalized_title)
            unique_articles.append(article)
        else:
            duplicate_count += 1
    
    if duplicate_count > 0:
        print(f"  Removed {duplicate_count} duplicate articles")
    
    return unique_articles


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
        print("No articles to save.")
        return False
    
    try:
        # Create DataFrame
        df = pd.DataFrame(articles)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file is open/read-only and handle it
        if output_path.exists():
            # Try to remove read-only attribute if it exists
            try:
                os.chmod(output_path, 0o666)  # Make file writable
            except (OSError, PermissionError):
                pass  # If we can't change permissions, try to write anyway
        
        # Save to CSV
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"✓ Saved {len(articles)} articles to {output_path}")
        return True
        
    except PermissionError:
        print(f"✗ ERROR: Permission denied when writing to {output_path}")
        print(f"  Please close the file if it's open in Excel or another program.")
        print(f"  Or check if the file is set to read-only.")
        return False
        
    except Exception as e:
        print(f"✗ ERROR: Failed to save to {output_path}: {e}")
        return False


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to orchestrate the article collection process.
    """
    print("=" * 70)
    print("CE49X Final Project - Task 1: NewsAPI Article Collection")
    print("=" * 70)
    print()
    
    # Check API keys
    if API_KEY_1 == "YOUR_NEWSAPI_KEY_HERE" or not API_KEY_1:
        print("ERROR: NewsAPI Key 1 not found!")
        print("Please set the NEWSAPI_KEY_1 environment variable or modify API_KEY_1 in the script.")
        print("Get your free API key at: https://newsapi.org/register")
        return
    
    if API_KEY_2 == "YOUR_NEWSAPI_KEY_HERE" or not API_KEY_2:
        print("ERROR: NewsAPI Key 2 not found!")
        print("Please set the NEWSAPI_KEY_2 environment variable or modify API_KEY_2 in the script.")
        print("Get your free API key at: https://newsapi.org/register")
        return
    
    print(f"Using API Key 1 for queries 1-{SWITCH_QUERY_NUMBER-1}")
    print(f"Using API Key 2 for queries {SWITCH_QUERY_NUMBER}+")
    print()
    
    # Calculate date range (NewsAPI free tier: up to 1 month back)
    to_date = datetime.now()
    from_date = (to_date - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")
    
    print(f"Date range: {from_date} to {to_date.strftime('%Y-%m-%d')}")
    print(f"Language: {LANGUAGE}")
    print()
    
    # Generate search queries
    all_queries = create_search_queries()
    
    # Calculate how many pages per query based on API limit
    # Free tier: 100 requests per day
    # Each page = 1 request
    # We want to distribute requests evenly across all queries
    total_queries = len(all_queries)
    available_requests = MAX_REQUESTS_PER_DAY - 5  # Reserve 5 requests for safety
    
    # Calculate pages per query
    pages_per_query = max(
        MIN_PAGES_PER_QUERY,
        min(
            MAX_PAGES_PER_QUERY,
            available_requests // total_queries
        )
    )
    
    # If we have too many queries, prioritize broader queries
    if pages_per_query < MIN_PAGES_PER_QUERY:
        # Too many queries, prioritize broader queries (they return more results)
        broader_queries = [q for q in all_queries if '(' in q and 'OR' in q]
        core_queries = [q for q in all_queries if q not in broader_queries]
        
        # Calculate how many queries we can handle
        max_queries = available_requests // MIN_PAGES_PER_QUERY
        queries = broader_queries[:max_queries] if len(broader_queries) >= max_queries else broader_queries
        remaining_slots = max_queries - len(queries)
        if remaining_slots > 0:
            queries.extend(core_queries[:remaining_slots])
        
        pages_per_query = MIN_PAGES_PER_QUERY
        print(f"⚠️  Too many queries ({total_queries}), prioritizing {len(queries)} queries")
    else:
        queries = all_queries
    
    print(f"Generated {len(queries)} search queries")
    print(f"  API Limit: {MAX_REQUESTS_PER_DAY} requests/day")
    print(f"  Available requests: {available_requests}")
    print(f"  Pages per query: {pages_per_query}")
    print(f"  Total requests to use: {len(queries) * pages_per_query}")
    print()
    
    # Track API usage for both keys
    requests_used_key1 = 0
    requests_used_key2 = 0
    all_articles = []
    existing_urls = set()
    current_api_key = API_KEY_1
    current_key_name = "Key 1"
    
    for i, query in enumerate(queries, 1):
        # Switch to second API key at SWITCH_QUERY_NUMBER
        if i == SWITCH_QUERY_NUMBER:
            print(f"\n{'='*70}")
            print(f"🔄 Switching to API Key 2 (Query {i}+)")
            print(f"{'='*70}\n")
            current_api_key = API_KEY_2
            current_key_name = "Key 2"
            requests_used_key1 = 0  # Reset counter for new key
            available_requests = MAX_REQUESTS_PER_DAY - 5  # Reset available requests
        
        # Check which key we're using and its limit
        if i < SWITCH_QUERY_NUMBER:
            # Using first key
            if requests_used_key1 >= available_requests:
                print(f"\n⚠️  API Key 1 limit reached! Switching to Key 2 at query {i}")
                current_api_key = API_KEY_2
                current_key_name = "Key 2"
                requests_used_key1 = 0
                available_requests = MAX_REQUESTS_PER_DAY - 5
            current_requests_used = requests_used_key1
        else:
            # Using second key
            if requests_used_key2 >= available_requests:
                print(f"\n⚠️  API Key 2 limit reached! Stopping at query {i-1}/{len(queries)}")
                print(f"   Requests used (Key 2): {requests_used_key2}/{available_requests}")
                break
            current_requests_used = requests_used_key2
        
        # Check if we've used too many requests
        if current_requests_used >= available_requests:
            print(f"\n⚠️  {current_key_name} limit reached! Stopping at query {i-1}/{len(queries)}")
            print(f"   Requests used: {current_requests_used}/{available_requests}")
            break
        
        print(f"Query {i}/{len(queries)} [{current_key_name}]")
        articles = collect_articles_for_query(
            query, 
            from_date, 
            current_api_key,  # Use current API key
            min_length=300,  # Reduced from 500 to get more articles
            strict_filter=True,  # Strict filtreleme aktif
            existing_urls=existing_urls,
            max_pages=pages_per_query  # Use calculated page limit
        )
        all_articles.extend(articles)
        
        # Update request counter for current key
        if i < SWITCH_QUERY_NUMBER:
            requests_used_key1 += pages_per_query
            current_requests_used = requests_used_key1
        else:
            requests_used_key2 += pages_per_query
            current_requests_used = requests_used_key2
        
        print(f"  Total articles collected so far: {len(all_articles)}")
        print(f"  Requests used ({current_key_name}): {current_requests_used}/{available_requests}")
        
        # Auto-save every 5 queries to prevent data loss
        if i % 5 == 0 or i == len(queries):
            try:
                # Prepare articles for CSV
                unique_temp = remove_duplicates(all_articles)
                csv_articles = []
                for article in unique_temp:
                    csv_article = {
                        "title": article.get("title", ""),
                        "publication_date": article.get("publication_date", ""),
                        "source": article.get("source", ""),
                        "url": article.get("url", ""),
                        "description": article.get("description", ""),
                        "ai_keywords_found": ", ".join(article.get("ai_keywords_found", [])),
                        "ce_keywords_found": ", ".join(article.get("ce_keywords_found", []))
                    }
                    csv_articles.append(csv_article)
                
                # Save to temporary file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_output = OUTPUT_DIR_DATA / f"newsapi_articles_progress_{timestamp}.csv"
                save_to_csv(csv_articles, temp_output)
                print(f"  💾 Auto-saved: {len(unique_temp)} articles to {temp_output.name}")
            except Exception as e:
                print(f"  ⚠️  Auto-save failed: {str(e)[:50]}")
        
        print()
        
        # Rate limiting between queries
        time.sleep(REQUEST_DELAY)
    
    # Remove duplicates
    print("Removing duplicate articles...")
    print(f"  Before deduplication: {len(all_articles)} articles")
    unique_articles = remove_duplicates(all_articles)
    print(f"  After deduplication: {len(unique_articles)} articles")
    print()
    
    # Prepare articles for CSV (add keyword columns)
    csv_articles = []
    for article in unique_articles:
        csv_article = {
            "title": article.get("title", ""),
            "publication_date": article.get("publication_date", ""),
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "description": article.get("description", ""),
            "ai_keywords_found": ", ".join(article.get("ai_keywords_found", [])),
            "ce_keywords_found": ", ".join(article.get("ce_keywords_found", []))
        }
        csv_articles.append(csv_article)
    
    # Save to CSV file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR_DATA / f"newsapi_articles_{timestamp}.csv"
    
    print("Saving articles to CSV file...")
    success = save_to_csv(csv_articles, output_path)
    
    if not success:
        print("\n[ERROR] CSV dosyasına kaydedilemedi!")
    else:
        print(f"\n[OK] CSV kaydedildi: {output_path.name}")
        print(f"     Tam yol: {output_path.absolute()}")
    
    # Print summary statistics
    print("\n" + "=" * 70)
    print("Collection Summary")
    print("=" * 70)
    print(f"Total unique articles collected: {len(unique_articles)}")
    if requests_used_key1 > 0:
        print(f"API Key 1 requests used: {requests_used_key1}/{available_requests}")
    if requests_used_key2 > 0:
        print(f"API Key 2 requests used: {requests_used_key2}/{available_requests}")
    print(f"Output file: {output_path}")
    print()
    
    # Show sample of sources
    if unique_articles:
        sources = {}
        for article in unique_articles:
            source = article.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        print("Top 10 sources by article count:")
        sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]
        for source, count in sorted_sources:
            print(f"  {source}: {count}")
        print()
        
        # Show keyword distribution
        ai_keyword_counts = {}
        ce_keyword_counts = {}
        for article in unique_articles:
            for kw in article.get("ai_keywords_found", []):
                ai_keyword_counts[kw] = ai_keyword_counts.get(kw, 0) + 1
            for kw in article.get("ce_keywords_found", []):
                ce_keyword_counts[kw] = ce_keyword_counts.get(kw, 0) + 1
        
        print("AI Keyword dağılımı:")
        for kw, count in sorted(ai_keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {kw}: {count}")
        print()
        
        print("CE Keyword dağılımı:")
        for kw, count in sorted(ce_keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {kw}: {count}")
        print()


if __name__ == "__main__":
    main()

