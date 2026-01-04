"""Basit veri görüntüleme - pgAdmin gerekmez"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_config import get_db_cursor

print("\n" + "="*70)
print("VERITABANI VERILERI")
print("="*70)

with get_db_cursor() as cur:
    # İstatistikler
    cur.execute("SELECT COUNT(*) as count FROM articles")
    total = cur.fetchone()['count']
    print(f"\nToplam Makale: {total}")
    
    cur.execute("SELECT COUNT(DISTINCT article_id) as count FROM classifications")
    classified = cur.fetchone()['count']
    print(f"Sınıflandırılmış: {classified}")
    print(f"Sınıflandırılmamış: {total - classified}")
    
    # İlk 5 makale
    print("\n" + "-"*70)
    print("ILK 5 MAKALE:")
    print("-"*70)
    cur.execute("""
        SELECT id, title, source 
        FROM articles 
        ORDER BY id 
        LIMIT 5
    """)
    for i, row in enumerate(cur.fetchall(), 1):
        title = row['title'][:60] + "..." if len(row['title']) > 60 else row['title']
        print(f"{i}. [{row['id']}] {title}")
        print(f"   Kaynak: {row['source']}")
    
    # Sınıflandırmalar
    print("\n" + "-"*70)
    print("SINIFLANDIRMALAR (Ilk 5):")
    print("-"*70)
    cur.execute("""
        SELECT a.id, a.title, c.ce_areas, c.ai_technologies
        FROM articles a
        JOIN classifications c ON a.id = c.article_id
        LIMIT 5
    """)
    for i, row in enumerate(cur.fetchall(), 1):
        title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
        ce = ', '.join(row['ce_areas']) if row['ce_areas'] else 'Yok'
        ai = ', '.join(row['ai_technologies']) if row['ai_technologies'] else 'Yok'
        print(f"{i}. [{row['id']}] {title}")
        print(f"   CE: {ce}")
        print(f"   AI: {ai}")

print("\n" + "="*70)
print("Tum veriler veritabaninda!")
print("pgAdmin gerekmez, Python scriptleri yeterli.")
print("="*70 + "\n")

