import os, requests, datetime, csv, re
from typing import List, Dict

BASE = "https://graph.facebook.com/v18.0/ads_archive"
TOKEN = os.environ.get("FB_GRAPH_TOKEN", "").strip()

EU_COUNTRIES = "RO,IT,FR,DE,ES,PT,NL,BE,AT,PL,SE,DK,IE"
KEYWORDS = "clothing OR apparel OR dress OR hoodie OR jacket OR t-shirt OR skirt OR blouse OR pants"

def _try_api() -> List[Dict]:
    if not TOKEN:
        return []
    since = (datetime.datetime.utcnow() - datetime.timedelta(days=14)).date().isoformat()
    params = {
        "access_token": TOKEN,
        "ad_reached_countries": EU_COUNTRIES,
        "search_terms": KEYWORDS,
        "ad_active_status": "ACTIVE",
        "ad_delivery_date_min": since,
        "limit": 200
    }
    try:
        r = requests.get(BASE, params=params, timeout=60)
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception:
        return []

    by_lp = {}
    for x in data:
        snap = x.get("ad_snapshot_url") or ""
        if not snap:
            continue
        by_lp.setdefault(snap, []).append(x)

    out = []
    for lp, items in by_lp.items():
        if len(items) < 3:
            continue
        out.append({"landing_url": lp, "ads_count": len(items)})
    return out

def _guess_landing_from_snapshot(snapshot_url: str) -> str:
    try:
        html = requests.get(snapshot_url, timeout=30, headers={"User-Agent":"Mozilla/5.0"}).text
        m = re.search(r'https?://[^\s"\']+', html)
        if m:
            return m.group(0)
    except Exception:
        pass
    return snapshot_url

def fetch_ads() -> List[Dict]:
    via_api = _try_api()
    out = []
    for item in via_api:
        out.append({
            "landing_url": _guess_landing_from_snapshot(item["landing_url"]),
            "ads_count": item["ads_count"]
        })
    return out

def seed_urls() -> List[str]:
    path = "data/seed_urls.csv"
    urls = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].startswith("http"):
                    urls.append(row[0].strip())
    return urls
