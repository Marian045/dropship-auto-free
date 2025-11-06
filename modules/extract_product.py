import requests, re
from bs4 import BeautifulSoup

CART_HINTS = ["add to cart", "adauga in cos", "adauga în coș", "add-to-cart", "buy now", "cumpără"]

def parse_product(url):
    try:
        html = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"}).text
    except Exception:
        return None

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True).lower()

    if not any(h in text for h in CART_HINTS):
        return None

    title = soup.title.get_text(strip=True) if soup.title else "New Arrival"

    prices = re.findall(r"([€$£]?\s?\d+[.,]?\d*)\s?(eur|euro|ron|lei|usd|gbp|€|\$|£)?", text, re.I)
    price_val, currency = None, "EUR"
    if prices:
        val, cur = prices[0]
        try:
            val = float(val.replace("€","").replace("$","").replace("£","").replace(",","." ).strip())
            price_val = val
        except Exception:
            price_val = None
        if cur:
            c = cur.upper().replace("EURO","EUR").replace("LEI","RON")
            currency = {"€":"EUR","$":"USD","£":"GBP"}.get(cur, c)

    imgs = [img["src"] for img in soup.select("img[src]") if img["src"].startswith("http")]
    imgs = imgs[:6] if imgs else []

    if not price_val:
        return None

    return {
        "title": title[:80],
        "raw_desc": "",
        "image_urls": imgs,
        "price_value": price_val,
        "price_currency": currency
    }
