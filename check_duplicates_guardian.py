"""Guardian CSV'de duplicate kontrolü"""
import sys
import pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

print("="*70)
print("GUARDIAN CSV DUPLICATE KONTROLÜ")
print("="*70)

# Find latest Guardian CSV
guardian_csvs = list(DATA_DIR.glob("guardian_articles_*.csv"))
if not guardian_csvs:
    print("\nGuardian CSV dosyası bulunamadı!")
    sys.exit(1)

# Get latest CSV
latest_csv = sorted(guardian_csvs, key=lambda x: x.stat().st_mtime, reverse=True)[0]
print(f"\nKontrol edilen dosya: {latest_csv.name}")

# Read CSV
try:
    df = pd.read_csv(latest_csv, encoding='utf-8')
    print(f"Toplam makale: {len(df)}")
    print()
except Exception as e:
    print(f"CSV okunamadı: {e}")
    sys.exit(1)

# Check for duplicates by URL (most reliable)
print("URL bazında duplicate kontrolü:")
url_duplicates = df[df.duplicated(subset=['url'], keep=False)]
if len(url_duplicates) > 0:
    print(f"  [BULUNDU] {len(url_duplicates)} duplicate URL var")
    print("\nDuplicate URL'ler:")
    for idx, row in url_duplicates.iterrows():
        print(f"  - {row['url']}")
        print(f"    Title: {row['title'][:60]}...")
else:
    print("  [OK] URL bazında duplicate yok")

print()

# Check for duplicates by title
print("Title bazında duplicate kontrolü:")
title_duplicates = df[df.duplicated(subset=['title'], keep=False)]
if len(title_duplicates) > 0:
    print(f"  [BULUNDU] {len(title_duplicates)} duplicate title var")
    print("\nDuplicate title'lar:")
    for idx, row in title_duplicates.head(10).iterrows():
        print(f"  - {row['title'][:70]}...")
        print(f"    URL: {row['url']}")
else:
    print("  [OK] Title bazında duplicate yok")

print()

# Check for exact duplicates (all columns)
print("Tam duplicate kontrolü (tüm kolonlar):")
exact_duplicates = df[df.duplicated(keep=False)]
if len(exact_duplicates) > 0:
    print(f"  [BULUNDU] {len(exact_duplicates)} tam duplicate var")
else:
    print("  [OK] Tam duplicate yok")

print()

# Summary
print("="*70)
print("ÖZET")
print("="*70)
print(f"Toplam makale: {len(df)}")
print(f"Unique URL'ler: {df['url'].nunique()}")
print(f"Unique title'lar: {df['title'].nunique()}")

if len(url_duplicates) > 0:
    unique_df = df.drop_duplicates(subset=['url'], keep='first')
    print(f"\nDuplicate'ler çıkarıldıktan sonra: {len(unique_df)} makale")
    print(f"Çıkarılan duplicate: {len(df) - len(unique_df)} makale")
    
    # Save cleaned CSV
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    cleaned_csv = DATA_DIR / f"guardian_articles_cleaned_{timestamp}.csv"
    unique_df.to_csv(cleaned_csv, index=False, encoding='utf-8')
    print(f"\nTemizlenmiş CSV kaydedildi: {cleaned_csv.name}")
else:
    print("\n[OK] Duplicate yok, CSV temiz!")

print("="*70)

