import streamlit as st
import requests, random, os
from google import genai
from moviepy.editor import *
from elevenlabs import generate, save
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- YOUR API KEYS ---
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"
ELEVEN_KEY = "b9ec07e05734006eeef408d7b07cfb69e8eec34e7bcf87e8bbdf026e51f169c3"

st.set_page_config(page_title="Hadith Automator", page_icon="🌙")
st.title("🎥 Hadith Viral Shorts Creator")

def fix_text(text):
    return get_display(reshape(text))

if st.button("🚀 Generate Viral Hadith Short"):
    with st.status("Work in Progress...", expanded=True) as status:
        # 1. Fetch Random Sahih Hadith
        st.write("📖 Fetching Sahih Hadith...")
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Viral Hook
        st.write("🧠 Gemini is creating a viral title...")
        client = genai.Client(api_key=GEMINI_KEY)
        gem_res = client.models.generate_content(model="gemini-2.0-flash", contents=f"Write a viral curiosity-driven Urdu title for this Hadith: {urdu_text}")
        viral_title = gem_res.text

        # 3. ElevenLabs Voiceover
        st.write("🎙️ Generating soulful Urdu voice...")
        audio = generate(text=urdu_text, api_key=ELEVEN_KEY, voice="Marcus", model="eleven_multilingual_v2")
        save(audio, "voice.mp3")

        # 4. Background from Pexels
        st.write("🎬 Downloading 4K Background...")
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers={"Authorization": PEXELS_KEY}).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: f.write(requests.get(video_url).content)

        # 5. Assemble Video
        st.write("🛠️ Finalizing Video...")
        clip = VideoFileClip("bg.mp4").subclip(0, 30).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        
        # Text Overlay
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=60, color='white', method='caption', size=(900, None)).set_duration(clip.duration).set_position(('center', 1100))
        
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264")
        
        status.update(label="Short Ready!", state="complete")

    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
    with open("short.mp4", "rb") as f:
        st.download_button("📥 Download MP4", f, "Viral_Hadith.mp4")
