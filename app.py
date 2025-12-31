import streamlit as st
import asyncio
import edge_tts
import requests, random, os
import google.generativeai as genai
from moviepy.editor import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- STABILITY FIX: Tell MoviePy to bypass ImageMagick policies ---
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

# API Configuration
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"

st.set_page_config(page_title="Hadith Viral Creator", page_icon="🌙")
st.title("🕋 Viral Hadith Shorts Creator")

def fix_text(text):
    return get_display(reshape(text))

def check_fonts():
    if not os.path.exists("Jameel.ttf"):
        url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNastaliqUrdu/NotoNastaliqUrdu-Regular.ttf"
        with open("Jameel.ttf", "wb") as f: f.write(requests.get(url).content)

check_fonts()

# --- FREE VOICE GENERATOR (2026 FIX) ---
async def generate_free_voice(text, output_file):
    # 'ur-PK-ImranNeural' is a deep, stable Urdu voice
    communicate = edge_tts.Communicate(text, "ur-PK-ImranNeural")
    await communicate.save(output_file)

if st.button("🚀 Generate Viral Hadith Short"):
    with st.status("Automating Work...", expanded=True) as status:
        # 1. Fetch Hadith
        st.write("📖 Fetching Sahih Hadith...")
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Viral Hook
        st.write("🧠 Gemini is creating a viral title...")
        viral_title = "بہت پیاری حدیث مبارکہ ✨ #Shorts #Hadith"
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gem_res = model.generate_content(f"Convert this into a very short viral YouTube title in Urdu: {urdu_text}")
            if gem_res.text: viral_title = gem_res.text
        except: pass

        # 3. FREE Edge-TTS Voiceover
        st.write("🎙️ Generating free neural Urdu voice...")
        try:
            asyncio.run(generate_free_voice(urdu_text, "voice.mp3"))
        except Exception as e:
            st.error(f"Voice generation failed: {e}")
            st.stop()

        # 4. Background from Pexels
        st.write("🎬 Downloading 4K Background...")
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble Video (Simplified to avoid PIL/ANTIALIAS errors)
        st.write("🛠️ Finalizing Video...")
        clip = VideoFileClip("bg.mp4").subclip(0, 15).resize(height=1280) # Resize to 720p vertical for speed
        
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=40, color='white', 
                       method='caption', size=(700, None)).set_duration(clip.duration).set_position('center')
        
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        status.update(label="Short Ready!", state="complete")

    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
    with open("short.mp4", "rb") as f:
        st.download_button("📥 Download MP4", f, "Viral_Hadith.mp4")
