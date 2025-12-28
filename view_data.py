"""View data in database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_config import get_db_cursor

print("=" * 70)
print("VERITABANI VERILERI")
print("=" * 70)

with get_db_cursor() as cur:
    # Toplam makale sayısı
    cur.execute("SELECT COUNT(*) as count FROM articles")
    total = cur.fetchone()['count']
    print(f"\nToplam Makale: {total}")
    
    # Sınıflandırılmış makale sayısı
    cur.execute("""
        SELECT COUNT(DISTINCT article_id) as count 
        FROM classifications
    """)
    classified = cur.fetchone()['count']
    print(f"Sınıflandırılmış Makale: {classified}")
    
    # Son 10 makale
    print("\n" + "-" * 70)
    print("SON 10 MAKALE:")
    print("-" * 70)
    cur.execute("""
        SELECT id, title, source, published_at, created_at
        FROM articles
        ORDER BY created_at DESC
        LIMIT 10
    """)
    for row in cur.fetchall():
        title = row['title'][:60] + "..." if len(row['title']) > 60 else row['title']
        print(f"\nID: {row['id']}")
        print(f"Baslik: {title}")
        print(f"Kaynak: {row['source']}")
        print(f"Tarih: {row['published_at']}")
    
    # Sınıflandırmalar
    print("\n" + "-" * 70)
    print("SINIFLANDIRMALAR:")
    print("-" * 70)
    cur.execute("""
        SELECT 
            a.id,
            a.title,
            c.ce_areas,
            c.ai_technologies,
            c.confidence_score
        FROM articles a
        JOIN classifications c ON a.id = c.article_id
        ORDER BY c.created_at DESC
        LIMIT 10
    """)
    for row in cur.fetchall():
        title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
        ce = ', '.join(row['ce_areas']) if row['ce_areas'] else 'Yok'
        ai = ', '.join(row['ai_technologies']) if row['ai_technologies'] else 'Yok'
        print(f"\nID: {row['id']} - {title}")
        print(f"  CE Alanlari: {ce}")
        print(f"  AI Teknolojileri: {ai}")
        print(f"  Confidence: {row['confidence_score']:.2f}" if row['confidence_score'] else "  Confidence: -")

print("\n" + "=" * 70)
print("pgAdmin ile gormek icin: http://localhost:5050")
print("Email: admin@ce49x.com, Sifre: admin")
print("=" * 70)

