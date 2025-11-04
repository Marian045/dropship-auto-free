# Dropship Auto (100% Free Stack)

An end-to-end, **free** automation that:
- finds active fashion/clothing ads (≤14 days) with ≥3 creatives,
- extracts *real* product pages (add-to-cart + price),
- keeps items **≤ €39**,
- creates/updates products in **Shopify**,
- auto-generates **emotional descriptions**,
- auto-produces **TikTok-style videos** (MP4) with voiceover + music,
- delivers video + caption to your phone via **Telegram** (so you can post in TikTok in 2 taps).

> ⚠️ TikTok doesn't provide a free/legal API for auto-posting. This repo automates **everything else** and sends you the ready-to-post MP4 + caption.

---

## 🪜 Step-by-step (non-technical)

### 1) Create free accounts / keys
- **Shopify**: In your store admin, create a **Custom App** → get **Admin API access token**.
- **Telegram**: Create a bot with **@BotFather** → get **BOT TOKEN**. Start a chat with your bot, then use `@userinfobot` to get your **CHAT ID**.
- **Pexels**: Create free account → **API Key** (for free B-roll videos).
- **Pixabay**: Create free account → **API Key** (for free music).
- **Facebook Graph (optional)**: If you can create a free developer app + user token for Ad Library, add it. If not, the script still runs but might import fewer products.

### 2) Download this repo and push to your GitHub
- Download the ZIP from ChatGPT (link in the conversation), unzip.
- Create a new GitHub repo (empty), then upload all files.

### 3) Add Secrets in GitHub → Settings → Secrets and variables → **Actions → New repository secret**
Add the following (exact names):
```
FB_GRAPH_TOKEN        # optional but recommended
SHOPIFY_SHOP          # e.g. mybrand.myshopify.com
SHOPIFY_TOKEN         # Shopify Admin API access token
PEXELS_API_KEY
PIXABAY_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID      # e.g. 123456789
```
> You can skip FB_GRAPH_TOKEN if you don't have it. The pipeline will focus on parsing the landing pages you feed it or it discovers via snapshots (limited, but free).

### 4) Enable GitHub Actions
- In your repo → **Actions** → enable workflows.
- The automation runs **every 4 hours**. You can also run it manually: **Actions → dropship-auto → Run workflow**.

### 5) First run checks
- After a run, check **Actions → artifacts → assets**. You should see MP4 videos + captions.
- You will also receive the MP4 + caption via **Telegram** (bot sends to your chat).

### 6) Connect the dots
- New products should appear in **Shopify** automatically (title, images, price, description).
- Videos arrive on your phone via Telegram → **open TikTok and post** (2 taps).

---

## 🔧 Configuration (optional)

- Edit `main.py` → `MAX_PER_RUN = 3` (how many products per run).
- Edit emotional copy template in `copy_emotions.py`.
- Change hashtags in `video_make.py`.

---

## 💡 How it works (short)

1. Search ads (≤14 days, apparel keywords).
2. Visit landing pages → confirm “Add to Cart” & price.
3. Convert currency → keep only ≤ €39.
4. Create emotional copy.
5. Push to Shopify.
6. Make 15s TikTok-style video (MoviePy + gTTS + Pexels + Pixabay).
7. Send MP4 + caption to Telegram + upload as workflow artifact.

---

## ⚠️ Notes

- FB Ad Library has restrictions; if the API is limited for you, the script still tries to use public snapshots and detected links. It won't break, it just may find fewer items.
- For best results, seed the pipeline with a small CSV of landing URLs you like, saved to `data/seed_urls.csv` (one URL per line). The runner will process those too, fully automatically.

---

## 🆘 Troubleshooting

- **No videos?** Check `Actions → logs` for Pexels/Pixabay API keys.
- **No Shopify products?** Check your token scopes: `write_products`.
- **No Telegram delivery?** Verify `TELEGRAM_CHAT_ID` and that you started a chat with your bot first.
- **Long build times?** Movie rendering can take 1–3 minutes per video on the free runner; that’s normal.

Enjoy 🚀
