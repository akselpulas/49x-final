"""NYTimes toplama ilerlemesini kontrol et"""
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

from database.db_config import get_db_cursor

print("NYTimes API ile toplama ilerlemesi kontrol ediliyor...\n")

with get_db_cursor() as cur:
    # Başlangıç sayısını al (NYTimes kaynaklı makaleler)
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM filtered_ai_ce_articles 
        WHERE source LIKE 'NYTimes%'
    """)
    nytimes_count = cur.fetchone()['count']
    
    # Toplam filtered makale
    cur.execute("SELECT COUNT(*) as count FROM filtered_ai_ce_articles")
    total_filtered = cur.fetchone()['count']
    
    # Son 10 dakikada eklenen NYTimes makaleleri
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM filtered_ai_ce_articles 
        WHERE source LIKE 'NYTimes%' 
        AND created_at > NOW() - INTERVAL '10 minutes'
    """)
    recent_10min = cur.fetchone()['count']
    
    print("="*70)
    print("NYTIMES API TOPLAMA İLERLEMESİ")
    print("="*70)
    print(f"NYTimes makaleleri: {nytimes_count}")
    print(f"Toplam filtered makale: {total_filtered}")
    print(f"Son 10 dakikada eklenen: {recent_10min}")
    print("="*70)
    
    # Son eklenen NYTimes makaleleri
    if nytimes_count > 0:
        cur.execute("""
            SELECT id, title, ai_keywords_found, ce_keywords_found, created_at
            FROM filtered_ai_ce_articles
            WHERE source LIKE 'NYTimes%'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        articles = cur.fetchall()
        print(f"\nSon eklenen 5 NYTimes makalesi:")
        print("-"*70)
        
        for i, article in enumerate(articles, 1):
            title = article['title'][:60] + "..." if len(article['title']) > 60 else article['title']
            ai_kw = ', '.join(article['ai_keywords_found'][:2]) if article['ai_keywords_found'] else 'Yok'
            ce_kw = ', '.join(article['ce_keywords_found'][:2]) if article['ce_keywords_found'] else 'Yok'
            created = article['created_at'].strftime('%H:%M:%S') if article['created_at'] else 'N/A'
            
            print(f"{i}. [{created}] {title}")
            print(f"   AI: {ai_kw} | CE: {ce_kw}")

