"""
Advanced pipeline to collect 500+ civil-engineering + AI articles.

Features:
- RSS feed harvesting (civil/ConTech + AI).
- Optional Google News via SerpAPI (set SERPAPI_KEY env var).
- Optional sitemap crawling for selected domains.
- Full-text extraction with trafilatura.
- SQLite storage + CSV export.

Usage examples (from project root):
  python "scripts/collect_articles_advanced.py" --max-articles 1200 --concurrency 12
  SERPAPI_KEY=... python "scripts/collect_articles_advanced.py" --use-serpapi

Deps: aiohttp, feedparser, trafilatura, pandas (for CSV), python-dotenv (optional).
Install: pip install aiohttp feedparser trafilatura pandas python-dotenv
"""

import argparse
import asyncio
import datetime as dt
import os
import pathlib
import re
import sqlite3
import xml.etree.ElementTree as ET
from typing import Iterable, List, Optional, Set, Tuple

import aiohttp
import feedparser
import trafilatura

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "articles.sqlite"
CSV_PATH = DATA_DIR / "articles.csv"

# RSS feeds (extendable).
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

# Domains to sitemap-scan (shallow).
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


async def fetch_sitemap_urls(session: aiohttp.ClientSession, domain: str) -> Set[str]:
    urls: Set[str] = set()
    for candidate in (f"https://{domain}/sitemap.xml", f"https://{domain}/sitemap_index.xml"):
        content = await fetch_text(session, candidate)
        if not content:
            continue
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            continue
        for loc in root.iter():
            if loc.tag.endswith("loc") and loc.text:
                urls.add(loc.text.strip())
        if urls:
            break
    return urls


async def process_url(
    session: aiohttp.ClientSession, url: str, min_len: int
) -> Optional[Tuple[str, str, str, str, str, str]]:
    html = await fetch_text(session, url)
    if not html:
        return None
    text = trafilatura.extract(html, url=url, include_comments=False)
    if not text or len(text) < min_len:
        return None
    title = trafilatura.extract_title(html) or ""
    source = normalize_source(url)
    retrieved = dt.datetime.utcnow().isoformat()
    if not title:
        title = url
    return (title, "", source, url, text, retrieved)


async def harvest_sitemaps(session: aiohttp.ClientSession, min_len: int, sem: asyncio.Semaphore) -> List[Tuple[str, str, str, str, str, str]]:
    rows: List[Tuple[str, str, str, str, str, str]] = []
    url_candidates: Set[str] = set()
    for domain in SITEMAP_DOMAINS:
        urls = await fetch_sitemap_urls(session, domain)
        url_candidates.update(urls)

    tasks = []

    async def run(url: str):
        async with sem:
            row = await process_url(session, url, min_len)
            if row and soft_match(row[0] + " " + row[4], AI_KEYWORDS) and soft_match(row[0] + " " + row[4], CE_KEYWORDS):
                rows.append(row)

    for url in list(url_candidates)[:800]:  # limit for politeness
        tasks.append(asyncio.create_task(run(url)))
    await asyncio.gather(*tasks)
    return rows


async def harvest_serpapi(session: aiohttp.ClientSession, min_len: int, sem: asyncio.Semaphore, queries: List[str]) -> List[Tuple[str, str, str, str, str, str]]:
    key = os.getenv("SERPAPI_KEY")
    if not key:
        return []
    rows: List[Tuple[str, str, str, str, str, str]] = []
    serp_urls: Set[str] = set()
    for q in queries:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_news",
            "q": q,
            "hl": "en",
            "api_key": key,
        }
        try:
            async with session.get(url, params=params, timeout=20) as resp:
                if resp.status != 200:
                    continue
                data = await resp.json()
                for item in data.get("news_results", []):
                    link = item.get("link")
                    if link:
                        serp_urls.add(link)
        except Exception:
            continue

    tasks = []

    async def run(url: str):
        async with sem:
            row = await process_url(session, url, min_len)
            if row and soft_match(row[0] + " " + row[4], AI_KEYWORDS) and soft_match(row[0] + " " + row[4], CE_KEYWORDS):
                rows.append(row)

    for url in list(serp_urls)[:400]:  # cap to avoid over-fetch
        tasks.append(asyncio.create_task(run(url)))
    await asyncio.gather(*tasks)
    return rows


async def collect_all(max_articles: int, min_len: int, concurrency: int, use_serpapi: bool) -> int:
    conn = sqlite3.connect(DB_PATH)
    seen = {row[0] for row in conn.execute("SELECT url FROM articles")}

    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        # Parallel harvesting
        feed_task = asyncio.create_task(harvest_feeds(session, min_len, sem))
        sitemap_task = asyncio.create_task(harvest_sitemaps(session, min_len, sem))

        serp_task = None
        serp_queries = [
            '(construction OR infrastructure OR "smart city") AND ("machine learning" OR "computer vision" OR robotics)',
            '(bridge OR tunnel OR concrete) AND ("artificial intelligence" OR automation)',
            '(BIM OR "building information modeling") AND AI',
        ]
        if use_serpapi and os.getenv("SERPAPI_KEY"):
            serp_task = asyncio.create_task(harvest_serpapi(session, min_len, sem, serp_queries))

        rows = []
        rows.extend(await feed_task)
        rows.extend(await sitemap_task)
        if serp_task:
            rows.extend(await serp_task)

    # Insert with dedupe
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
    parser = argparse.ArgumentParser(description="Advanced civil+AI article collector.")
    parser.add_argument("--max-articles", type=int, default=1200, help="Stop after roughly this many unique URLs.")
    parser.add_argument("--min-len", type=int, default=800, help="Minimum extracted text length.")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent fetch limit.")
    parser.add_argument("--use-serpapi", action="store_true", help="Enable SerpAPI Google News enrichment.")
    args = parser.parse_args()

    ensure_dirs()
    init_db()

    total = asyncio.run(
        collect_all(
            max_articles=args.max_articles,
            min_len=args.min_len,
            concurrency=args.concurrency,
            use_serpapi=args.use_serpapi,
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

