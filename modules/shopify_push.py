import os, requests, json

SHOP = os.environ.get("SHOPIFY_SHOP","")
TOKEN = os.environ.get("SHOPIFY_TOKEN","")

def create_or_update_product(title, price_eur, images, description, collection=None):
    if not SHOP or not TOKEN:
        raise RuntimeError("Missing SHOPIFY_SHOP or SHOPIFY_TOKEN.")
    url = f"https://{SHOP}/admin/api/2024-07/products.json"
    headers = {"X-Shopify-Access-Token": TOKEN, "Content-Type":"application/json"}
    payload = {
      "product": {
        "title": title,
        "body_html": description,
        "variants": [{"price": f"{price_eur:.2f}"}],
        "images": [{"src": src} for src in images[:5]]
      }
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    prod = r.json()["product"]
    return f"https://{SHOP}/products/{prod['handle']}"
