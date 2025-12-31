import streamlit as st
import requests
import random
import os
from google import genai
from moviepy.editor import *
from elevenlabs import generate, save

# --- AUTOMATION: DOWNLOAD FONTS ---
def download_assets():
    fonts = {
        "Jameel.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNastaliqUrdu/NotoNastaliqUrdu-Regular.ttf",
        "Amiri.ttf": "https://github.com/googlefonts/amiri/raw/main/Amiri-Regular.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            with open(name, "wb") as f:
                f.write(requests.get(url).content)

download_assets()

# --- WEB INTERFACE ---
st.title("🕋 Viral Hadith Shorts Creator")
with st.sidebar:
    gemini_key = st.text_input("Gemini API Key", type="password")
    eleven_key = st.text_input("ElevenLabs Key", type="password")
    pexels_key = st.text_input("Pexels Key", type="password")

if st.button("🚀 Create Viral Short"):
    # 1. Fetch Hadith (Fawaz API)
    res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
    hadith = random.choice(res['hadiths'])
    urdu_text = hadith['text']
    
    # 2. Get Viral Title via Gemini
    client = genai.Client(api_key=gemini_key)
    title_gen = client.models.generate_content(model="gemini-2.0-flash", contents=f"Write a viral curiosity-driven title in Urdu for this Hadith: {urdu_text}")
    
    # 3. Get Audio via ElevenLabs
    audio = generate(text=urdu_text, api_key=eleven_key, voice="Marcus", model="eleven_multilingual_v2")
    save(audio, "voice.mp3")
    
    # 4. Create Video (MoviePy)
    # Note: For Pexels, we fetch a 'nature' vertical video
    px_res = requests.get(f"https://api.pexels.com/v1/search?query=nature&orientation=portrait", headers={"Authorization": pexels_key}).json()
    video_url = px_res['photos'][0]['src']['original'] # Simplified for example
    
    st.success(f"Title: {title_gen.text}")
    st.write("Video is rendering... check back in 1 minute.")
    # (MoviePy rendering logic goes here as per previous steps)
