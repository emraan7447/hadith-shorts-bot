import streamlit as st
import PIL.Image
# Fix for the 'ANTIALIAS' error
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

async def generate_free_voice(text, output_file):
    communicate = edge_tts.Communicate(text, "ur-PK-ImranNeural")
    await communicate.save(output_file)

if st.button("🚀 Generate Viral Hadith Short"):
    with st.status("Automating Work...", expanded=True):
        # 1. Fetch
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Title
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            viral_title = model.generate_content(f"Urdu viral title for: {urdu_text}").text
        except:
            viral_title = "بہت پیاری حدیث مبارکہ ✨"

        # 3. Voice
        asyncio.run(generate_free_voice(urdu_text, "voice.mp3"))

        # 4. Video
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble (Permission-Proof logic)
        clip = VideoFileClip("bg.mp4").subclip(0, 15).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=45, color='white', method='caption', size=(850, None)).set_duration(clip.duration).set_position(('center', 1000))
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264")

    st.success(f"Title: {viral_title}")
    st.video("short.mp4")
