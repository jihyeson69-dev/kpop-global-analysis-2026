"""
Firecrawl Data Collector for K-Pop Idol Global & Domestic Ranking Analysis
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw_firecrawl"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Read API Key
API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not API_KEY:
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("FIRECRAWL_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip()

if not API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment or .env file.")

print(f"[Firecrawl] API Key detected: {API_KEY[:6]}...{API_KEY[-4:]}")

SEARCH_URL = "https://api.firecrawl.dev/v1/search"
SCRAPE_URL = "https://api.firecrawl.dev/v1/scrape"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def firecrawl_search(query: str, limit: int = 5):
    """Search web using Firecrawl search API"""
    payload = json.dumps({"query": query, "limit": limit}).encode("utf-8")
    req = urllib.request.Request(SEARCH_URL, data=payload, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"[Firecrawl Search Error] {query}: {e}")
        return {"success": False, "error": str(e)}

def firecrawl_scrape(target_url: str):
    """Scrape web page markdown using Firecrawl scrape API"""
    payload = json.dumps({"url": target_url, "formats": ["markdown"]}).encode("utf-8")
    req = urllib.request.Request(SCRAPE_URL, data=payload, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"[Firecrawl Scrape Error] {target_url}: {e}")
        return {"success": False, "error": str(e)}

def run_collection():
    queries = [
        ("korea_rankings", "2025 2026 kpop idol group brand reputation ranking circle chart melon"),
        ("western_rankings", "kpop billboard 200 hot 100 stray kids bts ateez spotify us 2025"),
        ("asia_rankings", "kpop seventeen twice aespa oricon japan qq music asia 2025"),
        ("europe_rankings", "kpop uk official chart lollapalooza hyde park festival europe 2025"),
        ("core_members", "kpop individual member brand reputation karina wonyoung felix mingyu jungkook")
    ]

    all_results = {}
    for key, q in queries:
        print(f"\n[Collecting] Firecrawl searching: '{q}'...")
        res = firecrawl_search(q, limit=4)
        all_results[key] = res
        output_path = DATA_DIR / f"{key}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f" -> Saved to {output_path.name} (Found {len(res.get('data', []))} items)")

    print("\n[Firecrawl Collection Completed Successfully!]")
    return all_results

if __name__ == "__main__":
    run_collection()
