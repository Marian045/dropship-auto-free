import os, requests
from moviepy.editor import (
    VideoFileClip, ImageClip, AudioFileClip, CompositeAudioClip,
    CompositeVideoClip, concatenate_videoclips, vfx, ColorClip
)
from gtts import gTTS

PEXELS = os.environ.get("PEXELS_API_KEY","")
PIXABAY = os.environ.get("PIXABAY_API_KEY","")

def _download(url, path):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

def pexels_clip():
    """Try to fetch a short portrait people/fashion clip from Pexels. Return local path or None."""
    if not PEXELS:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS},
            params={"query":"people portrait fashion", "per_page": 1, "orientation":"portrait"},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("videos"):
            return None
        # pick the first file that is mp4
        files = data["videos"][0].get("video_files", [])
        mp4s = [f for f in files if "mp4" in f.get("file_type","").lower() or f.get("link","").endswith(".mp4")]
        if not mp4s:
            return None
        url = sorted(mp4s, key=lambda x: x.get("width",0)*x.get("height",0), reverse=True)[0]["link"]
        path = "out/tmp_broll.mp4"
        _download(url, path)
        return path
    except Exception:
        return None

def pixabay_music():
    if not PIXABAY:
        return None
    try:
        r = requests.get("https://pixabay.com/api/music/",
                         params={"key": PIXABAY, "q":"fashion", "per_page":3},
                         timeout=60)
        r.raise_for_status()
        data = r.json()
        if not data.get("hits"):
            return None
        url = data["hits"][0]["audio"]
        path = "out/tmp_music.mp3"
        _download(url, path)
        return path
    except Exception:
        return None

def tts(text, path):
    gTTS(text).save(path)

def _safe_video_clip(path):
    """Open a VideoFileClip and verify it can return a frame; return clip or None."""
    try:
        clip = VideoFileClip(path, audio=False)
        # sanity: try to read a frame
        t_probe = 0.1 if clip.duration is None else min(0.1, max(0, clip.duration - 0.05))
        _ = clip.get_frame(t_probe)
        return clip
    except Exception:
        try:
            clip.close()
        except Exception:
            pass
        return None

def _fit_1080x1920(clip):
    """
    Return a CompositeVideoClip that is exactly 1080x1920.
    We resize by width to 1080, then pad on a black canvas if needed, or crop center if too tall.
    """
    try:
        scaled = clip.resize(width=1080)
    except Exception:
        # last-ditch: just return original to avoid crash
        scaled = clip
    # Create background canvas
    bg = ColorClip(size=(1080, 1920), color=(0,0,0)).set_duration(scaled.duration)
    # If scaled is shorter than 1920 high, center with padding; if taller, crop
    try:
        if scaled.h <= 1920:
            placed = scaled.set_position(("center", "center"))
            return CompositeVideoClip([bg, placed]).set_duration(scaled.duration)
        else:
            # crop vertically from center
            yc = scaled.h / 2
            cropped = scaled.fx(vfx.crop, width=1080, height=1920, y_center=yc)
            return cropped.set_duration(scaled.duration)
    except Exception:
        # fallback to just background
        return bg

def make_tiktok_video(title, benefits, images, price_eur, product_url):
    os.makedirs("out/videos", exist_ok=True)
    os.makedirs("out/captions", exist_ok=True)

    # --- script / caption ---
    hook = f"{title} — feel it from the first touch."
    body = " / ".join(benefits[:3] or ["Soft", "Effortless", "You"])
    cta  = "Tap to shop. You deserve this."
    script = f"{hook} {body}. Only {price_eur:.0f} euro. {cta}"

    tts_path = "out/voice.mp3"
    tts(script, tts_path)

    # --- try b-roll, verify it works ---
    clips = []
    broll_path = pexels_clip()
    broll = _safe_video_clip(broll_path) if broll_path else None
    if broll:
        dur = min(6, max(1, broll.duration or 6))
        broll_part = broll.subclip(0, dur)
        clips.append(_fit_1080x1920(broll_part))

    # --- add up to 3 product images as 3s slides ---
    for i, url in enumerate(images[:3]):
        try:
            p = f"out/img_{i}.jpg"
            _download(url, p)
            img = ImageClip(p).set_duration(3).resize(width=1080).set_position("center")
            # pad to full frame
            canvas = ColorClip(size=(1080,1920), color=(0,0,0)).set_duration(3)
            slide = CompositeVideoClip([canvas, img])
            clips.append(slide)
        except Exception:
            continue

    # --- if no media, create a simple background to ensure a video is produced ---
    if not clips:
        clips = [ColorClip(size=(1080,1920), color=(20,20,20)).set_duration(12)]

    # --- assemble ---
    seq = concatenate_videoclips(clips, method="compose")
    # normalize duration to 12–15s
    try:
        if seq.duration < 12:
            seq = seq.fx(vfx.loop, duration=12)
        elif seq.duration > 15:
            seq = seq.subclip(0, 15)
    except Exception:
        seq = seq.set_duration(12)

    # --- audio: TTS + optional music ---
    voice = AudioFileClip(tts_path).volumex(1.0)
    music_path = pixabay_music()
    if music_path:
        try:
            music = AudioFileClip(music_path).volumex(0.20)
            audio = CompositeAudioClip([music, voice])
        except Exception:
            audio = voice
    else:
        audio = voice

    video = seq.set_audio(audio)

    safe = "".join([c if c.isalnum() or c in "-_ " else "_" for c in title])[:25].strip().replace(" ","_")
    out_path = f"out/videos/{safe}.mp4"
    # write with safe defaults
    video.write_videofile(out_path, fps=30, codec="libx264", audio_codec="aac", threads=2)

    caption = f"{hook}\nOnly €{price_eur:.0f}\n{product_url}\n#fashion #outfit #ootd #style #comfort #tiktokmademebuyit"
    cap_path = f"out/captions/{safe}.txt"
    with open(cap_path,"w", encoding="utf-8") as f:
        f.write(caption)

    return out_path, caption
