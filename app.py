import streamlit as st
import PIL.Image

# --- THE STABILITY PATCH (Do not move or delete) ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import asyncio
import edge_tts
import requests, random, os
import google.generativeai as genai
from moviepy.editor import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Cloud settings
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# Hard-coded Keys (Based on your provided keys)
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"

st.set_page_config(page_title="Hadith Automator", page_icon="🕋")

def fix_text(text):
    return get_display(reshape(text))

def check_fonts():
    if not os.path.exists("Jameel.ttf"):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNastaliqUrdu/NotoNastaliqUrdu-Regular.ttf"
        with open("Jameel.ttf", "wb") as f: f.write(requests.get(url).content)

check_fonts()

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, "ur-PK-ImranNeural")
    await communicate.save("voice.mp3")

st.title("🕋 Stable Hadith Creator")

if st.button("🚀 Generate Viral Short"):
    with st.status("Building Video...", expanded=True):
        # 1. Fetch
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Title
        viral_title = "بہت پیاری حدیث مبارکہ ✨"
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gem_res = model.generate_content(f"Urdu viral title for: {urdu_text}")
            viral_title = gem_res.text
        except: pass

        # 3. Voice
        asyncio.run(generate_voice(urdu_text))

        # 4. Background
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble
        clip = VideoFileClip("bg.mp4").subclip(0, 15).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=45, color='white', method='caption', size=(850, None)).set_duration(clip.duration).set_position(('center', 1000))
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")
        
    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
    with open("short.mp4", "rb") as f:
        st.download_button("📥 Download MP4", f, "Viral_Hadith.mp4")
