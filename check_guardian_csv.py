"""Guardian CSV dosyalarını kontrol et"""
import sys
from pathlib import Path
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

print("="*70)
print("GUARDIAN CSV DOSYALARI")
print("="*70)

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("data/ klasörü oluşturuldu.")
    print("Script çalışıyor, CSV dosyası oluşturulacak...")
    sys.exit(0)

# Find all Guardian CSV files
csv_files = list(DATA_DIR.glob("guardian_articles_*.csv"))

if not csv_files:
    print("\nHenüz CSV dosyası oluşturulmamış.")
    print("Script çalışıyor olabilir, biraz bekleyin...")
else:
    # Sort by modification time (newest first)
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\nBulunan CSV dosyaları: {len(csv_files)}")
    print("-"*70)
    
    for i, csv_file in enumerate(csv_files[:5], 1):  # Show latest 5
        size_kb = csv_file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)
        
        print(f"{i}. {csv_file.name}")
        print(f"   Boyut: {size_kb:.1f} KB")
        print(f"   Oluşturulma: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Count lines (rough estimate)
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
                print(f"   Satır sayısı: {lines} (yaklaşık {lines-1} makale)")
        except:
            pass
        print()
    
    # Show latest file path
    if csv_files:
        latest = csv_files[0]
        print(f"En son dosya: {latest}")
        print(f"Tam yol: {latest.absolute()}")

