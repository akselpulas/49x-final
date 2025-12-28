"""
Collect ~500+ civil-engineering + AI related articles from RSS feeds.

Outputs:
- SQLite: ../data/articles.sqlite
- CSV:    ../data/articles.csv

Dependencies: aiohttp, feedparser, trafilatura, pandas (for CSV export).
Install: pip install aiohttp feedparser trafilatura pandas
"""

import argparse
import asyncio
import datetime as dt
import pathlib
import re
import sqlite3
from typing import Iterable, List, Optional, Tuple

import aiohttp
import feedparser
import trafilatura


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "articles.sqlite"
CSV_PATH = DATA_DIR / "articles.csv"

# Expandable list of feeds focused on construction / civil / ConTech / AI.
FEEDS: List[str] = [
    # Civil / ConTech news
    "https://www.enr.com/rss/articles",
    "https://www.constructiondive.com/feeds/news/",
    "https://csengineermag.com/feed/",
    "https://www.bimplus.co.uk/feed/",
    "https://www.globalconstructionreview.com/feed/",
    "https://www.concrete.org/Portals/0/Files/RSS/ACI-News.xml",
    "https://www.roadsbridges.com/rss.xml",
    # Vendor blogs with ConTech
    "https://www.autodesk.com/blogs/construction/feed/",
    "https://www.bentley.com/category/blog/feed/",
    "https://construction.trimble.com/blog/rss.xml",
    # Tech + AI (filtered later by keywords)
    "https://techcrunch.com/category/ai/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.wired.com/feed/tag/ai/",
    "https://www.mitre.org/rss/artificial-intelligence",
]

# Keywords to keep AI + civil focus; used as a soft filter on title/summary.
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
    """Return True if any keyword appears in text (case-insensitive)."""
    lowered = text.lower()
    return any(k in lowered for k in keywords)


async def fetch_html(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(
            url,
            timeout=aiohttp.ClientTimeout(total=25),
            headers={"user-agent": "Mozilla/5.0 (CE49X scraper)"},
        ) as resp:
            if resp.status != 200:
                return None
            return await resp.text()
    except Exception:
        return None


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


async def process_entry(
    session: aiohttp.ClientSession, entry, min_len: int
) -> Optional[Tuple[str, str, str, str, str, str]]:
    url = entry.get("link")
    title = (entry.get("title") or "").strip()
    summary = (entry.get("summary") or "").strip()
    if not url or not title:
        return None

    # Soft filter to stay on-topic.
    if not (soft_match(title + " " + summary, AI_KEYWORDS) and soft_match(title + " " + summary, CE_KEYWORDS)):
        return None

    html = await fetch_html(session, url)
    if not html:
        return None

    text = trafilatura.extract(html, url=url, include_comments=False)
    if not text or len(text) < min_len:
        return None

    published_iso = parse_date(entry)
    source = normalize_source(url)
    retrieved = dt.datetime.utcnow().isoformat()
    return (title, published_iso, source, url, text, retrieved)


async def collect_articles(max_articles: int, min_len: int, concurrency: int) -> int:
    sem = asyncio.Semaphore(concurrency)
    conn = sqlite3.connect(DB_PATH)
    seen_urls = set(
        row[0] for row in conn.execute("SELECT url FROM articles").fetchall()
    )

    entries = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        entries.extend(parsed.entries)

    async with aiohttp.ClientSession() as session:
        tasks = []

        async def run(entry):
            nonlocal conn
            async with sem:
                row = await process_entry(session, entry, min_len)
                if not row:
                    return
                url = row[3]
                if url in seen_urls:
                    return
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
                    seen_urls.add(url)
                except sqlite3.Error:
                    # Ignore insertion errors; continue collecting.
                    pass

        for entry in entries:
            if len(tasks) >= max_articles * 2:  # gather extra to survive filtering
                break
            tasks.append(asyncio.create_task(run(entry)))

        await asyncio.gather(*tasks)

    conn.close()
    return len(seen_urls)


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
    parser = argparse.ArgumentParser(
        description="Collect civil-engineering + AI news articles into SQLite/CSV."
    )
    parser.add_argument("--max-articles", type=int, default=800, help="Upper bound of entries to attempt.")
    parser.add_argument("--min-len", type=int, default=800, help="Minimum character length of extracted text.")
    parser.add_argument("--concurrency", type=int, default=8, help="Concurrent fetches.")
    args = parser.parse_args()

    ensure_dirs()
    init_db()

    print(f"Collecting articles (target up to {args.max_articles})...")
    total = asyncio.run(
        collect_articles(
            max_articles=args.max_articles,
            min_len=args.min_len,
            concurrency=args.concurrency,
        )
    )
    print(f"Rows now in DB: {total}")

    exported = export_csv()
    if exported:
        print(f"Exported {exported} rows to {CSV_PATH}")
    else:
        print("CSV export skipped.")


if __name__ == "__main__":
    main()

