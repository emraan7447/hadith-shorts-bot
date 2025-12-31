import streamlit as st
import PIL.Image

# --- THE STABLE FIX ---
# This line prevents the 'ANTIALIAS' error before any other library loads
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'LANCZOS', PIL.Image.BICUBIC)

import asyncio
import edge_tts
import requests, random, os
import google.generativeai as genai
from moviepy.editor import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Cloud rendering settings
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# Your Verified Keys
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"

st.set_page_config(page_title="Hadith Viral Creator", page_icon="🕋")

def fix_text(text):
    return get_display(reshape(text))

def check_assets():
    if not os.path.exists("Jameel.ttf"):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNastaliqUrdu/NotoNastaliqUrdu-Regular.ttf"
        with open("Jameel.ttf", "wb") as f: f.write(requests.get(url).content)

check_assets()

async def generate_free_voice(text, output_file):
    communicate = edge_tts.Communicate(text, "ur-PK-ImranNeural")
    await communicate.save(output_file)

st.title("🕋 Stable Hadith Creator")

if st.button("🚀 Start Final Build"):
    with st.status("Building Video...", expanded=True):
        # 1. Fetch Hadith
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Title (Classic Stable)
        viral_title = "بہت پیاری حدیث مبارکہ ✨"
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gem_res = model.generate_content(f"Urdu viral title for: {urdu_text}")
            if gem_res.text: viral_title = gem_res.text
        except: pass

        # 3. Free Voice (No Blocks)
        asyncio.run(generate_free_voice(urdu_text, "voice.mp3"))

        # 4. Background
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble
        clip = VideoFileClip("bg.mp4").subclip(0, 15).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        
        # Urdu text with shadow for clarity
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=45, color='white', 
                       method='caption', size=(850, None)).set_duration(clip.duration).set_position(('center', 1000))
        
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")
        
    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
