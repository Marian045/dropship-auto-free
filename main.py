from modules.facebook_ads import fetch_ads, seed_urls
from modules.extract_product import parse_product
from modules.pricing_filter import keep_under_39_eur, to_eur
from modules.copy_emotions import make_emotional_copy
from modules.shopify_push import create_or_update_product
from modules.video_make import make_tiktok_video
from modules.deliver import push_telegram

import os

MAX_PER_RUN = 3  # how many products per run

def run():
    os.makedirs("out/videos", exist_ok=True)
    os.makedirs("out/captions", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    ads = fetch_ads()
    urls = [a["landing_url"] for a in ads]

    # Also process user-provided seeds if exist
    urls += seed_urls()

    winners = []
    for url in urls:
        prod = parse_product(url)
        if not prod:
            continue
        if not keep_under_39_eur(prod["price_value"], prod["price_currency"]):
            continue
        prod["price_eur"] = to_eur(prod["price_value"], prod["price_currency"])
        prod["landing_url"] = url
        winners.append(prod)
        if len(winners) >= MAX_PER_RUN:
            break

    for w in winners:
        desc = make_emotional_copy(w["title"], w.get("raw_desc",""), w.get("benefits",[]))
        product_url = create_or_update_product(
            title=w["title"],
            price_eur=w["price_eur"],
            images=w["image_urls"],
            description=desc,
            collection="New Arrivals"
        )
        video_path, caption_txt = make_tiktok_video(
            title=w["title"],
            benefits=w.get("benefits",[]),
            images=w["image_urls"],
            price_eur=w["price_eur"],
            product_url=product_url
        )
        push_telegram(video_path, caption_txt)

if __name__ == "__main__":
    run()
