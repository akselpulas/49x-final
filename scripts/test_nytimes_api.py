"""NYTimes API key test scripti"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NYTIMES_API_KEY", "")

if not API_KEY:
    print("ERROR: NYTIMES_API_KEY environment variable not set!")
    print("Please add it to your .env file:")
    print("NYTIMES_API_KEY=your_api_key_here")
    sys.exit(1)

print("="*70)
print("NYTIMES API KEY TEST")
print("="*70)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
print()

# Test query: construction AND "artificial intelligence"
url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
params = {
    "q": 'construction AND "artificial intelligence"',
    "begin_date": "20240101",
    "end_date": "20241224",
    "page": 0,
    "api-key": API_KEY
}

print("Testing API connection...")
print(f"Query: construction AND \"artificial intelligence\"")
print()

try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    
    # Check for errors
    if "fault" in data:
        print("ERROR: API returned a fault:")
        print(data["fault"])
        sys.exit(1)
    
    # Get response
    response_obj = data.get("response", {})
    meta = response_obj.get("meta", {})
    hits = meta.get("hits", 0)
    docs = response_obj.get("docs", [])
    
    print("[OK] API connection successful!")
    print(f"Total results found: {hits}")
    print(f"Articles in this page: {len(docs)}")
    print()
    
    if docs:
        print("Sample articles:")
        print("-"*70)
        for i, article in enumerate(docs[:3], 1):
            headline = article.get("headline", {})
            title = headline.get("main", "No title")
            web_url = article.get("web_url", "")
            pub_date = article.get("pub_date", "")
            
            print(f"{i}. {title[:60]}...")
            print(f"   Date: {pub_date[:10]}")
            print(f"   URL: {web_url[:70]}...")
            print()
    
    print("="*70)
    print("[SUCCESS] NYTimes API key is working correctly!")
    print("="*70)
    print()
    print("You can now run the collection script:")
    print("  python scripts/collect_nytimes.py --target 100")
    
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            error_data = e.response.json()
            print(f"API Error: {error_data}")
        except:
            print(f"HTTP Status: {e.response.status_code}")
            print(f"Response: {e.response.text[:200]}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)

