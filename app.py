import streamlit as st
import PIL.Image

# --- THE COMPATIBILITY BRIDGE ---
# Fixes the 'ANTIALIAS' error for modern Python/Pillow versions
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

import asyncio
import edge_tts
import requests, random, os
import google.generativeai as genai
from moviepy.editor import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# Cloud rendering fix
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# API Configuration
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"

st.set_page_config(page_title="Hadith Viral Creator", page_icon="🕋")
st.title("🕋 Viral Hadith Shorts Creator")

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

if st.button("🚀 Generate Viral Hadith Short"):
    with st.status("Automating Work...", expanded=True) as status:
        # 1. Fetch
        st.write("📖 Fetching Hadith...")
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Title
        st.write("🧠 Gemini generating title...")
        viral_title = "بہت پیاری حدیث مبارکہ ✨ #Shorts #Hadith"
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gem_res = model.generate_content(f"Urdu viral title for: {urdu_text}")
            if gem_res.text: viral_title = gem_res.text
        except: pass

        # 3. Voice
        st.write("🎙️ Generating Voice...")
        asyncio.run(generate_free_voice(urdu_text, "voice.mp3"))

        # 4. Background
        st.write("🎬 Downloading Video...")
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble (Permission-Proof logic)
        st.write("🛠️ Rendering Final Video...")
        clip = VideoFileClip("bg.mp4").subclip(0, 15).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        
        # Text Overlay
        ready_text = fix_text(urdu_text)
        txt = TextClip(ready_text, font="Jameel.ttf", fontsize=45, color='white', method='caption', size=(850, None)).set_duration(clip.duration).set_position(('center', 1000))
        
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        status.update(label="Short Ready!", state="complete")

    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
    with open("short.mp4", "rb") as f:
        st.download_button("📥 Download MP4", f, "Viral_Hadith.mp4")
