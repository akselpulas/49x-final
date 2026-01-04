"""Veritabanındaki tabloları ve kayıt sayılarını göster"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_config import get_db_cursor

print("="*70)
print("VERITABANI TABLOLARI VE KAYIT SAYILARI")
print("="*70)

with get_db_cursor() as cur:
    # Tüm tabloları listele
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = [row['table_name'] for row in cur.fetchall()]
    
    print(f"\nToplam {len(tables)} tablo bulundu:\n")
    
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cur.fetchone()['count']
            print(f"  {table:30} : {count:5} kayit")
        except:
            print(f"  {table:30} : (hata)")

print("\n" + "="*70)
print("pgAdmin'de gormek icin:")
print("  Servers -> CE49X Database -> Databases -> ce49x_db")
print("  -> Schemas -> public -> Tables -> articles")
print("  -> articles uzerine SAG TIK -> View/Edit Data -> All Rows")
print("="*70)


