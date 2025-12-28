"""
Filtrelenmiş makaleler (hem AI hem CE içeren) için abstract oluştur.
LLM API'yi sadece bu makaleler için kullanır.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent


def ensure_abstract_column():
    """filtered_ai_ce_articles tablosuna abstract kolonu ekle"""
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='filtered_ai_ce_articles' AND column_name='abstract'
        """)
        
        if not cur.fetchone():
            print("abstract kolonu ekleniyor...")
            cur.execute("ALTER TABLE filtered_ai_ce_articles ADD COLUMN abstract TEXT")
            print("abstract kolonu eklendi.")


def get_filtered_articles_without_abstract(limit: int = 10) -> list:
    """Abstract'ı olmayan filtrelenmiş makaleleri getir"""
    with get_db_cursor() as cur:
        query = """
            SELECT id, article_id, title, content, description, full_text
            FROM filtered_ai_ce_articles
            WHERE abstract IS NULL OR abstract = ''
            ORDER BY id
            LIMIT %s
        """
        cur.execute(query, (limit,))
        return cur.fetchall()


def generate_abstract(title: str, content: str) -> Optional[str]:
    """LLM kullanarak abstract oluştur (50-100 kelime)"""
    # İçeriği sınırla
    max_content_length = 3000
    if content and len(content) > max_content_length:
        content = content[:max_content_length] + "..."
    
    prompt = f"""Aşağıdaki makale için kısa ve öz bir abstract (özet) yazın. 
Abstract, makalenin ana konusunu, bulgularını ve önemini özetlemelidir.

ÖNEMLİ: Abstract 50-100 kelime arasında olmalıdır. Daha kısa veya uzun olmamalı.

Makale Başlığı: {title}

Makale İçeriği:
{content or 'İçerik bulunamadı.'}

Sadece abstract metnini yazın, başka açıklama eklemeyin. Abstract Türkçe veya İngilizce olabilir. Kelime sayısı 50-100 arasında olmalıdır."""

    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise abstracts for articles. Always respond with only the abstract text, no explanations. Abstract must be 50-100 words."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        abstract = response.choices[0].message.content.strip()
        return abstract
        
    except Exception as e:
        print(f"  HATA: {e}")
        return None


def save_abstract(filtered_id: int, abstract: str):
    """Abstract'ı veritabanına kaydet"""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE filtered_ai_ce_articles 
            SET abstract = %s 
            WHERE id = %s
        """, (abstract, filtered_id))


def main():
    """Main function"""
    print("=" * 70)
    print("Filtrelenmis Makaleler icin Abstract Olusturma")
    print("=" * 70)
    print()
    
    if not test_connection():
        print("ERROR: Veritabanina baglanilamiyor.")
        return
    
    # Abstract kolonunu ekle
    ensure_abstract_column()
    
    # Filtrelenmiş makaleleri getir
    print("Abstract'i olmayan filtrelenmis makaleler getiriliyor...")
    articles = get_filtered_articles_without_abstract(limit=10)
    
    if not articles:
        print("Tum filtrelenmis makalelerin abstract'i var veya makale bulunamadi.")
        
        # İstatistik göster
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as total FROM filtered_ai_ce_articles")
            total = cur.fetchone()['total']
            cur.execute("SELECT COUNT(*) as with_abstract FROM filtered_ai_ce_articles WHERE abstract IS NOT NULL AND abstract != ''")
            with_abs = cur.fetchone()['with_abstract']
            print(f"\nToplam filtrelenmis makale: {total}")
            print(f"Abstract'i olan: {with_abs}")
            print(f"Abstract'i olmayan: {total - with_abs}")
        return
    
    print(f"{len(articles)} makale bulundu.\n")
    
    # Her makale için abstract oluştur
    success_count = 0
    fail_count = 0
    
    for idx, article in enumerate(articles, 1):
        filtered_id = article['id']
        article_id = article['article_id']
        title = article['title'] or 'Baslik yok'
        content = article.get('full_text') or article.get('content') or article.get('description') or ''
        
        print(f"[{idx}/{len(articles)}] Isleniyor (Article ID: {article_id}): {title[:60]}...")
        
        # Abstract oluştur
        abstract = generate_abstract(title, content)
        
        if abstract:
            # Veritabanına kaydet
            save_abstract(filtered_id, abstract)
            print(f"  [OK] Abstract olusturuldu ve kaydedildi")
            print(f"  Abstract: {abstract[:100]}...")
            success_count += 1
        else:
            print(f"  [HATA] Abstract olusturulamadi")
            fail_count += 1
        
        print()
    
    # Özet
    print("=" * 70)
    print("OZET")
    print("=" * 70)
    print(f"Basarili: {success_count}")
    print(f"Basarisiz: {fail_count}")
    print(f"Toplam: {len(articles)}")
    print("=" * 70)
    
    # Genel istatistikler
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) as total FROM filtered_ai_ce_articles")
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as with_abstract FROM filtered_ai_ce_articles WHERE abstract IS NOT NULL AND abstract != ''")
        with_abs = cur.fetchone()['with_abstract']
        print(f"\nGenel Durum:")
        print(f"  Toplam filtrelenmis makale: {total}")
        print(f"  Abstract'i olan: {with_abs}")
        print(f"  Abstract'i olmayan: {total - with_abs}")


if __name__ == "__main__":
    main()

