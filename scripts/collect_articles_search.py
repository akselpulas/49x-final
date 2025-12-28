"""
Search-based (non-RSS) collector for civil-engineering + AI articles.

Sources:
- Google News via SerpAPI (requires SERPAPI_KEY env var).
- GDELT 2 documents API (no key needed, capped).
- NewsAPI everything endpoint (requires NEWSAPI_KEY env var or --newsapi-key).

Outputs:
- SQLite: ../data/articles.sqlite
- CSV:    ../data/articles.csv

Usage examples (from project root):
  # SerpAPI only
  SERPAPI_KEY=... python "scripts/collect_articles_search.py" --use-serpapi --max-articles 800
  # GDELT only
  python "scripts/collect_articles_search.py" --use-gdelt --max-articles 800
  # Both
  SERPAPI_KEY=... python "scripts/collect_articles_search.py" --use-serpapi --use-gdelt --max-articles 1000

Deps: aiohttp, trafilatura, pandas (for CSV), python-dotenv (optional).
Install: pip install aiohttp trafilatura pandas python-dotenv
"""

import argparse
import asyncio
import datetime as dt
import os
import pathlib
import re
import sqlite3
from typing import Iterable, List, Optional, Set, Tuple

import aiohttp
import trafilatura


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "articles.sqlite"
CSV_PATH = DATA_DIR / "articles.csv"

AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "computer vision",
    "robotics",
    "automation",
    "generative",
    "neural",
    "ai",
]
CE_KEYWORDS = [
    "construction",
    "infrastructure",
    "bridge",
    "tunnel",
    "concrete",
    "structural",
    "geotechnical",
    "transport",
    "smart city",
    "bim",
    "civil",
]

# Query set for search APIs.
SEARCH_QUERIES = [
    '(construction OR infrastructure OR "smart city") AND ("machine learning" OR "computer vision" OR robotics)',
    '(bridge OR tunnel OR concrete) AND ("artificial intelligence" OR automation)',
    '(BIM OR "building information modeling") AND AI',
    'geotechnical AND "machine learning"',
    '"civil engineering" AND "computer vision"',
]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            published_at TEXT,
            source TEXT,
            url TEXT UNIQUE,
            content TEXT,
            retrieved_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def soft_match(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in keywords)


def normalize_source(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return host


async def fetch_text(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=25),
            headers={"user-agent": "Mozilla/5.0 (CE49X search scraper)"},
        ) as resp:
            if resp.status != 200:
                return None
            return await resp.text()
    except Exception:
        return None


async def process_url(
    session: aiohttp.ClientSession, url: str, min_len: int, enforce_topic: bool
) -> Optional[Tuple[str, str, str, str, str, str]]:
    html = await fetch_text(session, url)
    if not html:
        return None
    text = trafilatura.extract(html, url=url, include_comments=False)
    if not text or len(text) < min_len:
        return None
    title = trafilatura.extract_title(html) or ""
    if not title:
        title = url
    source = normalize_source(url)
    retrieved = dt.datetime.utcnow().isoformat()
    # Soft topic filter to stay on theme; can be disabled.
    if enforce_topic and not (soft_match(title + " " + text, AI_KEYWORDS) and soft_match(title + " " + text, CE_KEYWORDS)):
        return None
    return (title, "", source, url, text, retrieved)


async def harvest_serpapi(session: aiohttp.ClientSession, sem: asyncio.Semaphore) -> Set[str]:
    key = os.getenv("SERPAPI_KEY")
    if not key:
        return set()
    urls: Set[str] = set()
    for q in SEARCH_QUERIES:
        params = {
            "engine": "google_news",
            "q": q,
            "hl": "en",
            "api_key": key,
        }
        try:
            async with sem, session.get("https://serpapi.com/search", params=params, timeout=20) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in data.get("news_results", []):
                    link = item.get("link")
                    if link:
                        urls.add(link)
        except Exception:
            continue
    return urls


async def harvest_gdelt(session: aiohttp.ClientSession, sem: asyncio.Semaphore) -> Set[str]:
    # Using the documents API; limited to maxrecords per call.
    urls: Set[str] = set()
    for q in SEARCH_QUERIES:
        params = {
            "query": q,
            "maxrecords": 250,
            "format": "json",
            "timespan": "90days",
        }
        try:
            async with sem, session.get("https://api.gdeltproject.org/api/v2/doc/doc", params=params, timeout=20) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in data.get("articles", []):
                    link = item.get("url")
                    if link:
                        urls.add(link)
        except Exception:
            continue
    return urls


async def harvest_newsapi(session: aiohttp.ClientSession, sem: asyncio.Semaphore, key: Optional[str]) -> Set[str]:
    # NewsAPI limits: everything endpoint allows up to 100 results per request, 30-day window.
    if not key:
        return set()
    urls: Set[str] = set()
    from_date = (dt.datetime.utcnow() - dt.timedelta(days=30)).date().isoformat()
    for q in SEARCH_QUERIES:
        params = {
            "q": q,
            "language": "en",
            "from": from_date,
            "sortBy": "publishedAt",
            "pageSize": 100,
            "apiKey": key,
        }
        try:
            async with sem, session.get("https://newsapi.org/v2/everything", params=params, timeout=20) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in data.get("articles", []):
                    link = item.get("url")
                    if link:
                        urls.add(link)
        except Exception:
            continue
    return urls


async def collect_all(
    use_serpapi: bool,
    use_gdelt: bool,
    use_newsapi: bool,
    newsapi_key: Optional[str],
    max_articles: int,
    min_len: int,
    enforce_topic: bool,
    concurrency: int,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    seen = {row[0] for row in conn.execute("SELECT url FROM articles")}

    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        url_candidates: Set[str] = set()
        tasks = []
        labels: List[str] = []

        if use_serpapi:
            tasks.append(asyncio.create_task(harvest_serpapi(session, sem)))
            labels.append("serpapi")
        if use_gdelt:
            tasks.append(asyncio.create_task(harvest_gdelt(session, sem)))
            labels.append("gdelt")
        if use_newsapi:
            key = newsapi_key or os.getenv("NEWSAPI_KEY")
            tasks.append(asyncio.create_task(harvest_newsapi(session, sem, key)))
            labels.append("newsapi")

        if tasks:
            results = await asyncio.gather(*tasks)
            for label, s in zip(labels, results):
                print(f"[info] {label} candidate URLs: {len(s)}")
                url_candidates.update(s)
        else:
            results = []
            print("No sources enabled; nothing to do.")

        # Process URLs for full text.
        process_tasks = []
        rows: List[Tuple[str, str, str, str, str, str]] = []

        async def run(url: str):
            async with sem:
                row = await process_url(session, url, min_len, enforce_topic)
                if row:
                    rows.append(row)

        for url in list(url_candidates)[: max_articles * 2]:
            if len(process_tasks) >= max_articles * 2:
                break
            process_tasks.append(asyncio.create_task(run(url)))

        await asyncio.gather(*process_tasks)

    inserted = 0
    for row in rows:
        url = row[3]
        if url in seen:
            continue
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO articles
                (title, published_at, source, url, content, retrieved_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                row,
            )
            conn.commit()
            seen.add(url)
            inserted += 1
            if len(seen) >= max_articles:
                break
        except sqlite3.Error:
            continue

    conn.close()
    return len(seen)


def export_csv() -> int:
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed; skipping CSV export.")
        return 0
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()
    df.to_csv(CSV_PATH, index=False)
    return len(df)


def main():
    parser = argparse.ArgumentParser(description="Search-based civil+AI article collector (no RSS).")
    parser.add_argument("--use-serpapi", action="store_true", help="Enable SerpAPI Google News harvesting (requires SERPAPI_KEY).")
    parser.add_argument("--use-gdelt", action="store_true", help="Enable GDELT doc API harvesting.")
    parser.add_argument("--use-newsapi", action="store_true", help="Enable NewsAPI everything harvesting (requires NEWSAPI_KEY or --newsapi-key).")
    parser.add_argument("--newsapi-key", type=str, default=None, help="Override NEWSAPI_KEY environment variable.")
    parser.add_argument("--max-articles", type=int, default=1000, help="Target number of unique URLs.")
    parser.add_argument("--min-len", type=int, default=800, help="Minimum extracted text length.")
    parser.add_argument("--no-topic-filter", action="store_true", help="Disable AI + CE keyword filter (keeps more results).")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent fetch limit.")
    args = parser.parse_args()

    ensure_dirs()
    init_db()

    total = asyncio.run(
        collect_all(
            use_serpapi=args.use_serpapi,
            use_gdelt=args.use_gdelt,
            use_newsapi=args.use_newsapi,
            newsapi_key=args.newsapi_key,
            max_articles=args.max_articles,
            min_len=args.min_len,
            enforce_topic=not args.no_topic_filter,
            concurrency=args.concurrency,
        )
    )
    print(f"DB now holds ~{total} rows.")
    exported = export_csv()
    if exported:
        print(f"Exported {exported} rows to {CSV_PATH}")
    else:
        print("CSV export skipped.")


if __name__ == "__main__":
    main()

