import streamlit as st
import asyncio
import edge_tts
import requests, random, os
import google.generativeai as genai
from moviepy.editor import *
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- CONFIGURATION ---
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"

# --- FIX IMAGEMAGICK (Streamlit Cloud) ---
if os.path.exists("/etc/ImageMagick-6/policy.xml"):
    os.system("sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml")

st.title("🎥 Zero-Limit Hadith Creator")

def fix_text(text):
    return get_display(reshape(text))

# --- NEW: FREE VOICE GENERATOR ---
async def generate_free_voice(text, output_file):
    # 'ur-PK-ImranNeural' is a deep, respectful Urdu voice
    voice = "ur-PK-ImranNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

if st.button("🚀 Generate Viral Short"):
    with st.status("Automating Work...", expanded=True):
        # 1. Fetch Hadith
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Viral Title
        try:
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            gem_res = model.generate_content(f"Urdu viral title for: {urdu_text}")
            viral_title = gem_res.text
        except:
            viral_title = "بہت پیاری حدیث مبارکہ ✨"

        # 3. FREE Edge-TTS Voiceover (No Blocks!)
        st.write("🎙️ Generating free neural Urdu voice...")
        asyncio.run(generate_free_voice(urdu_text, "voice.mp3"))

        # 4. Background from Pexels
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble Video
        clip = VideoFileClip("bg.mp4").subclip(0, 25).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=50, color='white', method='caption', size=(800, None)).set_duration(clip.duration).set_position(('center', 1100))
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264")

    st.success(f"Title: {viral_title}")
    st.video("short.mp4")
