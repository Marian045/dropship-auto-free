import os, requests
from moviepy.editor import VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, vfx, ColorClip
from gTTS import gTTS

PEXELS = os.environ.get("PEXELS_API_KEY","")
PIXABAY = os.environ.get("PIXABAY_API_KEY","")

def _download(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def pexels_clip():
    if not PEXELS:
        return None
    r = requests.get("https://api.pexels.com/videos/search",
                     headers={"Authorization": PEXELS},
                     params={"query":"people portrait fashion", "per_page": 1, "orientation":"portrait"})
    r.raise_for_status()
    data = r.json()
    if not data.get("videos"):
        return None
    url = data["videos"][0]["video_files"][0]["link"]
    path = "out/tmp_broll.mp4"
    _download(url, path)
    return path

def pixabay_music():
    if not PIXABAY:
        return None
    r = requests.get("https://pixabay.com/api/music/",
                     params={"key": PIXABAY, "q":"fashion", "per_page":3})
    r.raise_for_status()
    data = r.json()
    if not data.get("hits"):
        return None
    url = data["hits"][0]["audio"]
    path = "out/tmp_music.mp3"
    _download(url, path)
    return path

def tts(text, path):
    gTTS(text).save(path)

def make_tiktok_video(title, benefits, images, price_eur, product_url):
    os.makedirs("out/videos", exist_ok=True)
    os.makedirs("out/captions", exist_ok=True)

    hook = f"{title} — feel it from the first touch."
    body = " / ".join(benefits[:3] or ["Soft", "Effortless", "You"])
    cta  = "Tap to shop. You deserve this."
    script = f"{hook} {body}. Only {price_eur:.0f} euro. {cta}"

    tts_path = "out/voice.mp3"
    tts(script, tts_path)

    clips = []
    broll_path = pexels_clip()
    if broll_path:
        clips.append(VideoFileClip(broll_path).subclip(0,6).resize((1080,1920)))

    # add up to 3 product images
    for i, url in enumerate(images[:3]):
        p = f"out/img_{i}.jpg"
        try:
            _download(url, p)
            img = ImageClip(p).set_duration(3).resize(width=1080).set_position("center")
            clips.append(img)
        except Exception:
            continue

    if not clips:
        clips = [ColorClip(size=(1080,1920), color=(20,20,20)).set_duration(15)]

    seq = concatenate_videoclips(clips, method="compose")
    if seq.duration < 15:
        seq = seq.fx(vfx.loop, duration=15)
    else:
        seq = seq.subclip(0,15)

    voice = AudioFileClip(tts_path).volumex(1.0)
    music_path = pixabay_music()
    if music_path:
        music = AudioFileClip(music_path).volumex(0.20)
        audio = CompositeAudioClip([music, voice])
    else:
        audio = voice
    video = seq.set_audio(audio).set_duration(15)

    safe = "".join([c if c.isalnum() or c in "-_ " else "_" for c in title])[:25].strip().replace(" ","_")
    out_path = f"out/videos/{safe}.mp4"
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac")

    caption = f"{hook}\nOnly €{price_eur:.0f}\n{product_url}\n#fashion #outfit #ootd #style #comfort #tiktokmademebuyit"
    cap_path = f"out/captions/{safe}.txt"
    with open(cap_path,"w", encoding="utf-8") as f:
        f.write(caption)
    return out_path, caption
