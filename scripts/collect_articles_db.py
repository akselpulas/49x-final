"""
Updated article collection script that saves directly to PostgreSQL.
Based on collect_articles_advanced.py but uses PostgreSQL instead of SQLite.
"""

import argparse
import asyncio
import datetime as dt
import os
import pathlib
import re
import sys
from typing import Iterable, List, Optional, Set, Tuple

# Add parent directory to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

import aiohttp
import feedparser
import trafilatura

ROOT = pathlib.Path(__file__).resolve().parents[1]

# RSS feeds
FEEDS: List[str] = [
    "https://www.enr.com/rss/articles",
    "https://www.constructiondive.com/feeds/news/",
    "https://csengineermag.com/feed/",
    "https://www.bimplus.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
    "https://www.autodesk.com/blogs/construction/feed/",
    "https://www.bentley.com/category/blog/feed/",
    "https://construction.trimble.com/blog/rss.xml",
    "https://techcrunch.com/category/ai/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/tag/ai/",
    "https://www.mitre.org/rss/artificial-intelligence",
]

SITEMAP_DOMAINS = [
    "www.enr.com",
    "www.constructiondive.com",
    "csengineermag.com",
    "www.globalconstructionreview.com",
    "www.autodesk.com",
    "www.bentley.com",
    "construction.trimble.com",
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "computer vision",
    "robotics", "automation", "generative", "neural", "ai",
]

CE_KEYWORDS = [
    "construction", "infrastructure", "bridge", "tunnel", "concrete",
    "structural", "geotechnical", "transport", "smart city", "bim", "civil",
]


def soft_match(text: str, keywords: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in keywords)


def normalize_source(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return host


def parse_date(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, key, None)
        if parsed:
            try:
                return dt.datetime(*parsed[:6]).isoformat()
            except Exception:
                continue
    return ""


async def fetch_text(session: aiohttp.ClientSession, url: str, as_bytes: bool = False) -> Optional[str]:
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=25),
            headers={"user-agent": "Mozilla/5.0 (CE49X advanced scraper)"},
        ) as resp:
            if resp.status != 200:
                return None
            return await (resp.read() if as_bytes else resp.text())
    except Exception:
        return None


async def process_entry(
    session: aiohttp.ClientSession, entry, min_len: int
) -> Optional[Tuple[str, str, str, str, str, str]]:
    url = entry.get("link")
    title = (entry.get("title") or "").strip()
    summary = (entry.get("summary") or "").strip()
    if not url or not title:
        return None
    if not (soft_match(title + " " + summary, AI_KEYWORDS) and soft_match(title + " " + summary, CE_KEYWORDS)):
        return None
    html = await fetch_text(session, url)
    if not html:
        return None
    text = trafilatura.extract(html, url=url, include_comments=False)
    if not text or len(text) < min_len:
        return None
    published_iso = parse_date(entry)
    source = normalize_source(url)
    retrieved = dt.datetime.utcnow().isoformat()
    return (title, published_iso, source, url, text, retrieved)


async def harvest_feeds(session: aiohttp.ClientSession, min_len: int, sem: asyncio.Semaphore) -> List[Tuple[str, str, str, str, str, str]]:
    entries = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        entries.extend(parsed.entries)

    tasks = []
    rows: List[Tuple[str, str, str, str, str, str]] = []

    async def run(entry):
        async with sem:
            row = await process_entry(session, entry, min_len)
            if row:
                rows.append(row)

    for entry in entries:
        tasks.append(asyncio.create_task(run(entry)))
    await asyncio.gather(*tasks)
    return rows


def save_to_db(rows: List[Tuple[str, str, str, str, str, str]], max_articles: int) -> int:
    """Save articles to PostgreSQL database."""
    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        return 0
    
    inserted = 0
    skipped = 0
    
    with get_db_cursor() as cur:
        # Get existing URLs
        cur.execute("SELECT url FROM articles")
        seen = {row['url'] for row in cur.fetchall()}
        
        for row in rows:
            title, published_at, source, url, content, retrieved_at = row
            
            if url in seen:
                skipped += 1
                continue
            
            try:
                cur.execute("""
                    INSERT INTO articles
                    (title, published_at, source, url, content, retrieved_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                """, (
                    title,
                    published_at if published_at else None,
                    source,
                    url,
                    content,
                    retrieved_at
                ))
                
                if cur.fetchone():
                    inserted += 1
                    seen.add(url)
                    
                    if len(seen) >= max_articles:
                        break
                        
            except Exception as e:
                print(f"Error inserting {url}: {e}")
                skipped += 1
                continue
    
    return inserted


async def collect_all(max_articles: int, min_len: int, concurrency: int) -> int:
    """Collect articles from all sources."""
    sem = asyncio.Semaphore(concurrency)
    
    async with aiohttp.ClientSession() as session:
        feed_task = asyncio.create_task(harvest_feeds(session, min_len, sem))
        rows = await feed_task
    
    inserted = save_to_db(rows, max_articles)
    
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM articles")
        total = cur.fetchone()['count']
    
    return total


def main():
    parser = argparse.ArgumentParser(description="Collect civil+AI articles to PostgreSQL.")
    parser.add_argument("--max-articles", type=int, default=130, help="Target number of articles.")
    parser.add_argument("--min-len", type=int, default=800, help="Minimum extracted text length.")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent fetch limit.")
    args = parser.parse_args()

    if not test_connection():
        print("ERROR: Cannot connect to PostgreSQL database.")
        print("Make sure Docker containers are running: docker-compose up -d")
        return

    print("Starting article collection...")
    total = asyncio.run(
        collect_all(
            max_articles=args.max_articles,
            min_len=args.min_len,
            concurrency=args.concurrency,
        )
    )
    print(f"Database now holds {total} articles.")


if __name__ == "__main__":
    main()

