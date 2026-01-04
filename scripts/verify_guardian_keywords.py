"""Guardian CSV'deki makalelerin keyword uyumluluğunu kontrol et"""
import sys
import pandas as pd
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

# Base keywords
CE_KEYWORDS = [
    "construction",
    "structural",
    "geotechnical",
    "transportation",
    "infrastructure",
    "concrete",
    "bridge",
    "tunnel"
]

AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "computer vision",
    "generative AI",
    "neural networks",
    "robotics",
    "automation"
]

def find_keywords_in_text(text: str, keywords: list) -> list:
    """Metinde hangi keyword'lerin geçtiğini bul"""
    if not text or pd.isna(text):
        return []
    
    text_lower = str(text).lower()
    found = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    
    return list(set(found))

def has_both_ai_and_ce(title: str, description: str, ai_found_str: str, ce_found_str: str) -> tuple:
    """Makalenin hem AI hem CE keyword'leri içerip içermediğini kontrol et"""
    # Önce CSV'deki keyword kolonlarını kontrol et
    ai_found_csv = [kw.strip() for kw in str(ai_found_str).split(',') if kw.strip()] if pd.notna(ai_found_str) else []
    ce_found_csv = [kw.strip() for kw in str(ce_found_str).split(',') if kw.strip()] if pd.notna(ce_found_str) else []
    
    # CSV'deki keyword'ler base keyword listesinde mi kontrol et
    ai_valid = [kw for kw in ai_found_csv if kw in AI_KEYWORDS]
    ce_valid = [kw for kw in ce_found_csv if kw in CE_KEYWORDS]
    
    # Eğer CSV'de keyword yoksa, title ve description'da kontrol et
    if not ai_valid or not ce_valid:
        combined_text = f"{title} {description}".lower()
        ai_found_text = find_keywords_in_text(combined_text, AI_KEYWORDS)
        ce_found_text = find_keywords_in_text(combined_text, CE_KEYWORDS)
        
        if ai_found_text:
            ai_valid = ai_found_text
        if ce_found_text:
            ce_valid = ce_found_text
    
    has_both = len(ai_valid) >= 1 and len(ce_valid) >= 1
    
    return (has_both, ai_valid, ce_valid)

print("="*70)
print("GUARDIAN CSV KEYWORD UYUMLULUK KONTROLÜ")
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

# Check each article
relevant_count = 0
irrelevant_count = 0
missing_ai = 0
missing_ce = 0
missing_both = 0

results = []

for idx, row in df.iterrows():
    title = row.get('title', '')
    description = row.get('description', '')
    ai_keywords = row.get('ai_keywords_found', '')
    ce_keywords = row.get('ce_keywords_found', '')
    
    has_both, ai_found, ce_found = has_both_ai_and_ce(title, description, ai_keywords, ce_keywords)
    
    if has_both:
        relevant_count += 1
        status = "ALAKALI"
    else:
        irrelevant_count += 1
        status = "ALAKASIZ"
        if not ai_found:
            missing_ai += 1
        if not ce_found:
            missing_ce += 1
        if not ai_found and not ce_found:
            missing_both += 1
    
    results.append({
        'index': idx + 1,
        'title': title[:60] + "..." if len(str(title)) > 60 else title,
        'status': status,
        'ai_keywords': ', '.join(ai_found) if ai_found else 'YOK',
        'ce_keywords': ', '.join(ce_found) if ce_found else 'YOK',
        'ai_csv': str(ai_keywords)[:30] if pd.notna(ai_keywords) else 'YOK',
        'ce_csv': str(ce_keywords)[:30] if pd.notna(ce_keywords) else 'YOK'
    })

# Print summary
print("="*70)
print("ÖZET")
print("="*70)
print(f"Toplam makale: {len(df)}")
print(f"Alakalı (hem AI hem CE): {relevant_count} ({relevant_count/len(df)*100:.1f}%)")
print(f"Alakasız: {irrelevant_count} ({irrelevant_count/len(df)*100:.1f}%)")
print()
print("Alakasız nedenleri:")
print(f"  - AI keyword yok: {missing_ai}")
print(f"  - CE keyword yok: {missing_ce}")
print(f"  - Her ikisi de yok: {missing_both}")
print("="*70)

# Show sample of irrelevant articles
irrelevant_samples = [r for r in results if r['status'] == 'ALAKASIZ'][:10]
if irrelevant_samples:
    print("\nAlakasız makale örnekleri (ilk 10):")
    print("-"*70)
    for r in irrelevant_samples:
        print(f"\n{r['index']}. {r['title']}")
        print(f"   AI Keywords: {r['ai_keywords']}")
        print(f"   CE Keywords: {r['ce_keywords']}")
        print(f"   CSV'de AI: {r['ai_csv']}")
        print(f"   CSV'de CE: {r['ce_csv']}")

# Show sample of relevant articles
relevant_samples = [r for r in results if r['status'] == 'ALAKALI'][:5]
if relevant_samples:
    print("\n\nAlakalı makale örnekleri (ilk 5):")
    print("-"*70)
    for r in relevant_samples:
        print(f"\n{r['index']}. {r['title']}")
        print(f"   AI Keywords: {r['ai_keywords']}")
        print(f"   CE Keywords: {r['ce_keywords']}")

print("\n" + "="*70)

