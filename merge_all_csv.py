"""Tüm CSV dosyalarını birleştir ve tek bir CSV oluştur"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

print("="*70)
print("CSV DOSYALARINI BİRLEŞTİRME")
print("="*70)

# Find all article CSV files
csv_files = []
for pattern in ["guardian_articles_*.csv", "nytimes_articles_*.csv", "newsapi_articles.csv"]:
    csv_files.extend(list(DATA_DIR.glob(pattern)))

if not csv_files:
    print("\nHenüz CSV dosyası bulunamadı!")
    sys.exit(1)

print(f"\nBulunan CSV dosyaları: {len(csv_files)}")
for csv_file in csv_files:
    print(f"  - {csv_file.name}")

# Read and merge all CSV files
all_articles = []
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"\n{csv_file.name}: {len(df)} makale")
        all_articles.append(df)
    except Exception as e:
        print(f"  [ERROR] {csv_file.name} okunamadı: {e}")

if not all_articles:
    print("\nHiç makale bulunamadı!")
    sys.exit(1)

# Merge all dataframes
merged_df = pd.concat(all_articles, ignore_index=True)

# Remove duplicates based on URL
print(f"\nBirleştirme öncesi: {len(merged_df)} makale")
merged_df = merged_df.drop_duplicates(subset=['url'], keep='first')
print(f"Birleştirme sonrası (duplicate'ler çıkarıldı): {len(merged_df)} makale")

# Save merged CSV
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = DATA_DIR / f"all_articles_merged_{timestamp}.csv"
merged_df.to_csv(output_file, index=False, encoding='utf-8')

print("\n" + "="*70)
print("BİRLEŞTİRME TAMAMLANDI")
print("="*70)
print(f"Çıktı dosyası: {output_file.name}")
print(f"Toplam makale: {len(merged_df)}")
print(f"Tam yol: {output_file.absolute()}")
print("="*70)

# Show source distribution
if 'source' in merged_df.columns:
    print("\nKaynak dağılımı:")
    print(merged_df['source'].value_counts().head(10))

