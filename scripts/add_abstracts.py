"""
LLM API kullanarak makalelere abstract ekleme scripti.
İlk 10 makale ile test edilir.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import get_db_cursor, test_connection
from scripts.llm_api import get_classifier

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent


def ensure_abstract_column():
    """articles tablosuna abstract kolonu ekle (yoksa)"""
    with get_db_cursor() as cur:
        # Kolonun var olup olmadığını kontrol et
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='articles' AND column_name='abstract'
        """)
        
        if not cur.fetchone():
            # Kolonu ekle
            print("abstract kolonu ekleniyor...")
            cur.execute("ALTER TABLE articles ADD COLUMN abstract TEXT")
            print("abstract kolonu eklendi.")


def get_articles_without_abstract(limit: int = 10) -> list:
    """Abstract'ı olmayan makaleleri getir"""
    with get_db_cursor() as cur:
        query = """
            SELECT id, title, content, description, full_text
            FROM articles
            WHERE abstract IS NULL OR abstract = ''
            ORDER BY id
            LIMIT %s
        """
        cur.execute(query, (limit,))
        return cur.fetchall()


def generate_abstract(llm_classifier, title: str, content: str) -> Optional[str]:
    """
    LLM kullanarak makale için abstract oluştur.
    
    Args:
        llm_classifier: LLM classifier instance
        title: Makale başlığı
        content: Makale içeriği
        
    Returns:
        Abstract metni veya None
    """
    # İçeriği sınırla (token limiti için)
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
        # OpenAI API kullan (yeni versiyon)
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
            max_tokens=150  # 50-100 kelime için yeterli
        )
        
        abstract = response.choices[0].message.content.strip()
        return abstract
        
    except Exception as e:
        print(f"  HATA: {e}")
        return None


def save_abstract(article_id: int, abstract: str):
    """Abstract'ı veritabanına kaydet"""
    with get_db_cursor() as cur:
        cur.execute("""
            UPDATE articles 
            SET abstract = %s 
            WHERE id = %s
        """, (abstract, article_id))


def main():
    """Main function"""
    print("=" * 70)
    print("LLM API ile Abstract Oluşturma")
    print("=" * 70)
    print()
    
    # Veritabanı bağlantısını kontrol et
    if not test_connection():
        print("ERROR: Veritabanına bağlanılamıyor.")
        print("Docker container'ların çalıştığından emin olun: docker-compose ps")
        return
    
    # Abstract kolonunu ekle
    ensure_abstract_column()
    
    # LLM classifier'ı hazırla
    try:
        classifier = get_classifier()
        print(f"LLM Provider: {classifier.provider}, Model: {classifier.model}")
    except Exception as e:
        print(f"ERROR: LLM classifier hazırlanamadı: {e}")
        return
    
    # Abstract'ı olmayan makaleleri getir
    print("\nAbstract'ı olmayan makaleler getiriliyor...")
    articles = get_articles_without_abstract(limit=10)
    
    if not articles:
        print("Tüm makalelerin abstract'ı var veya makale bulunamadı.")
        return
    
    print(f"{len(articles)} makale bulundu.\n")
    
    # Her makale için abstract oluştur
    success_count = 0
    fail_count = 0
    
    for idx, article in enumerate(articles, 1):
        article_id = article['id']
        title = article['title'] or 'Başlık yok'
        content = article.get('full_text') or article.get('content') or article.get('description') or ''
        
        print(f"[{idx}/{len(articles)}] İşleniyor: {title[:60]}...")
        
        # Abstract oluştur
        abstract = generate_abstract(classifier, title, content)
        
        if abstract:
            # Veritabanına kaydet
            save_abstract(article_id, abstract)
            print(f"  [OK] Abstract olusturuldu ve kaydedildi")
            print(f"  Abstract: {abstract[:100]}...")
            success_count += 1
        else:
            print(f"  [HATA] Abstract olusturulamadi")
            fail_count += 1
        
        print()
    
    # Özet
    print("=" * 70)
    print("ÖZET")
    print("=" * 70)
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {fail_count}")
    print(f"Toplam: {len(articles)}")
    print("=" * 70)
    
    # Sonuçları göster
    if success_count > 0:
        print("\nOluşturulan abstract'ları görmek için:")
        print("  python -c \"from database.db_config import get_db_cursor; cur = get_db_cursor(); cur.execute('SELECT id, title, abstract FROM articles WHERE abstract IS NOT NULL LIMIT 5'); [print(f'{r[\\\"id\\\"]}: {r[\\\"title\\\"][:50]}...\\n  Abstract: {r[\\\"abstract\\\"][:100]}...') for r in cur.fetchall()]\"")
        print("\nVEYA pgAdmin'de articles tablosunu açın ve abstract kolonunu görün.")


if __name__ == "__main__":
    main()

