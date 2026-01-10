import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /healthz...")
    try:
        r = requests.get(f"{BASE_URL}/healthz")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
        return r.status_code == 200
    except Exception as e:
        print(f"Failed: {e}")
        return False

def test_scrape(url, name):
    print(f"\nTesting /scrape with {name} ({url})...")
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/scrape", json={"url": url})
        elapsed = time.time() - start
        print(f"Status: {r.status_code} (took {elapsed:.2f}s)")
        if r.status_code == 200:
            data = r.json()
            res = data.get("result", {})
            print(f"Title: {res.get('meta', {}).get('title')}")
            print(f"Sections: {len(res.get('sections', []))}")
            print(f"Interactions: {res.get('interactions')}")
            
            # Checks
            if not res.get("sections"):
                print("FAIL: No sections found")
            
            if name == "Vercel" and not res.get("interactions", {}).get("clicks"):
                print("WARN: No clicks recorded for JS heavy site")
                
            if name == "Hacker News" and len(res.get("interactions", {}).get("pages", [])) < 2:
                print("WARN: Pagination depth < 2")
                
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    if test_health():
        # Stage 2
        test_scrape("https://en.wikipedia.org/wiki/Artificial_intelligence", "Wikipedia")
        # Stage 3
        test_scrape("https://vercel.com/", "Vercel")
        # Stage 4
        test_scrape("https://news.ycombinator.com/", "Hacker News")
    else:
        print("Server not healthy, skipping scrape tests.")
