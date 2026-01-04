"""Quick system test"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("SISTEM TESTI")
print("=" * 50)

# Test 1: Database
try:
    from database.db_config import test_connection, get_db_cursor
    if test_connection():
        with get_db_cursor() as cur:
            cur.execute("SELECT COUNT(*) as count FROM articles")
            count = cur.fetchone()['count']
        print(f"[OK] Veritabani: Baglanti basarili - {count} makale var")
    else:
        print("[HATA] Veritabani: Baglanti basarisiz")
except Exception as e:
    print(f"[HATA] Veritabani: {e}")

# Test 2: API Key
try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    key = os.getenv('OPENAI_API_KEY')
    if key and key.startswith('sk-'):
        print(f"[OK] API Anahtari: Bulundu ({key[:20]}...)")
    else:
        print("[HATA] API Anahtari: Bulunamadi")
except Exception as e:
    print(f"[HATA] API Anahtari: {e}")

# Test 3: LLM API
try:
    from scripts.llm_api import get_classifier
    classifier = get_classifier()
    print(f"[OK] LLM API: {classifier.provider} - {classifier.model}")
except Exception as e:
    print(f"[HATA] LLM API: {e}")

# Test 4: Docker
try:
    import subprocess
    result = subprocess.run(['docker-compose', 'ps', '--format', '{{.Name}}'], 
                          capture_output=True, text=True, cwd=Path(__file__).parent)
    if 'ce49x_postgres' in result.stdout and 'ce49x_pgadmin' in result.stdout:
        print("[OK] Docker: Container'lar calisiyor")
    else:
        print("[HATA] Docker: Container'lar calismiyor")
except Exception as e:
    print(f"[HATA] Docker: {e}")

print("=" * 50)

