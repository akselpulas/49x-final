"""
Hem AI hem CE keyword içeren makaleleri filtrele ve ayrı tabloya kaydet.
Bu makaleler için sonra abstract oluşturulacak.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Keyword listeleri (collect_articles_advanced.py'den)
AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "computer vision",
    "robotics", "automation", "generative", "neural", "ai",
    "deep learning", "neural network", "ml", "algorithm"
]

CE_KEYWORDS = [
    "construction", "infrastructure", "bridge", "tunnel", "concrete",
    "structural", "geotechnical", "transport", "smart city", "bim",
    "civil", "building", "engineering", "foundation", "highway",
    "road", "urban planning", "sustainability", "materials"
]


def create_filtered_table():
    """Filtrelenmiş makaleler için tablo oluştur"""
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
        print("[OK] filtered_ai_ce_articles tablosu hazir")


def contains_keywords(text: str, keywords: List[str]) -> List[str]:
    """Metinde hangi keyword'lerin geçtiğini bul"""
    if not text:
        return []
    
    text_lower = text.lower()
    found = []
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    return found


def filter_articles():
    """Hem AI hem CE keyword içeren makaleleri filtrele"""
    if not test_connection():
        print("ERROR: Veritabanina baglanilamiyor")
        return 0
    
    # Tabloyu oluştur
    create_filtered_table()
    
    # Tüm makaleleri getir
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT id, title, content, description, full_text, source, url, published_at
            FROM articles
            WHERE id NOT IN (SELECT article_id FROM filtered_ai_ce_articles WHERE article_id IS NOT NULL)
        """)
        all_articles = cur.fetchall()
    
    print(f"\nToplam {len(all_articles)} makale kontrol ediliyor...")
    
    filtered_count = 0
    processed = 0
    
    for article in all_articles:
        processed += 1
        if processed % 100 == 0:
            print(f"  Islenen: {processed}/{len(all_articles)}...")
        
        # Tüm metin alanlarını birleştir
        title = article['title'] or ''
        content = article.get('content') or ''
        description = article.get('description') or ''
        full_text = article.get('full_text') or ''
        
        combined_text = f"{title} {description} {content} {full_text}"
        
        # AI ve CE keyword'lerini kontrol et
        ai_found = contains_keywords(combined_text, AI_KEYWORDS)
        ce_found = contains_keywords(combined_text, CE_KEYWORDS)
        
        # Hem AI hem CE içeriyorsa kaydet
        if ai_found and ce_found:
            with get_db_cursor() as cur:
                try:
                    cur.execute("""
                        INSERT INTO filtered_ai_ce_articles 
                        (article_id, title, content, description, full_text, source, url, published_at, 
                         ai_keywords_found, ce_keywords_found)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (article_id) DO NOTHING
                    """, (
                        article['id'],
                        article['title'],
                        article.get('content'),
                        article.get('description'),
                        article.get('full_text'),
                        article.get('source'),
                        article.get('url'),
                        article.get('published_at'),
                        ai_found,
                        ce_found
                    ))
                    filtered_count += 1
                except Exception as e:
                    print(f"  HATA (ID {article['id']}): {e}")
                    continue
    
    return filtered_count


def main():
    """Main function"""
    print("=" * 70)
    print("AI ve CE Keyword Filtreleme")
    print("=" * 70)
    print()
    
    print("Filtreleme kriterleri:")
    print(f"  AI Keywords: {len(AI_KEYWORDS)} adet")
    print(f"  CE Keywords: {len(CE_KEYWORDS)} adet")
    print("  Kosul: Hem AI hem CE keyword icermeli")
    print()
    
    filtered = filter_articles()
    
    # İstatistikler
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as count FROM filtered_ai_ce_articles")
        total_filtered = cur.fetchone()['count']
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT source) as sources
            FROM filtered_ai_ce_articles
        """)
        stats = cur.fetchone()
    
    print("\n" + "=" * 70)
    print("FILTRELEME TAMAMLANDI")
    print("=" * 70)
    print(f"Bu islemde filtrelenen: {filtered}")
    print(f"Toplam filtrelenmis makale: {total_filtered}")
    print(f"Farkli kaynak sayisi: {stats['sources']}")
    print()
    print("Sonraki adim:")
    print("  python scripts/add_abstracts_filtered.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

