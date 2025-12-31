import streamlit as st
import requests, random, os
from google import genai
from moviepy.editor import *
from elevenlabs.client import ElevenLabs
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- CONFIGURATION ---
PEXELS_KEY = "b88Ldc0xcVaGbF3g5znBOiurvWee3OG5SvIcZuOoyQP2ZrYcG9IIGItp"
GEMINI_KEY = "AIzaSyB1ZVl788k7MYLs7bt9aF3P2rH6cV4TFvw"
ELEVEN_KEY = "b9ec07e05734006eeef408d7b07cfb69e8eec34e7bcf87e8bbdf026e51f169c3"

# --- FIX IMAGEMAGICK POLICY (Critical for Streamlit Cloud) ---
if os.path.exists("/etc/ImageMagick-6/policy.xml"):
    os.system("sed -i 's/none/read,write/g' /etc/ImageMagick-6/policy.xml")

st.set_page_config(page_title="Hadith Automator", page_icon="🌙")
st.title("🎥 Viral Hadith Shorts Creator")

def fix_text(text):
    return get_display(reshape(text))

def check_assets():
    fonts = {
        "Jameel.ttf": "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNastaliqUrdu/NotoNastaliqUrdu-Regular.ttf",
        "Amiri.ttf": "https://github.com/googlefonts/amiri/raw/main/Amiri-Regular.ttf"
    }
    for name, url in fonts.items():
        if not os.path.exists(name):
            with open(name, "wb") as f:
                f.write(requests.get(url).content)

check_assets()

if st.button("🚀 Generate Viral Hadith Short"):
    with st.status("Automating Work...", expanded=True) as status:
        # 1. Fetch Hadith
        st.write("📖 Fetching Sahih Hadith...")
        res = requests.get("https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/urd-bukhari.json").json()
        hadith = random.choice(res['hadiths'])
        urdu_text = hadith['text']
        
        # 2. Gemini Viral Hook (With Safety Fallback)
        st.write("🧠 Gemini is creating a viral title...")
        try:
            client_gemini = genai.Client(api_key=GEMINI_KEY)
            gem_res = client_gemini.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"Short viral YouTube title in Urdu for: {urdu_text}"
            )
            viral_title = gem_res.text
        except Exception:
            viral_title = "بہت پیاری حدیث مبارکہ ✨ #Shorts #Hadith"

        # 3. ElevenLabs Voiceover (Updated for v1.5+)
        st.write("🎙️ Generating soulful Urdu voice...")
        client_eleven = ElevenLabs(api_key=ELEVEN_KEY)
        audio_stream = client_eleven.text_to_speech.convert(
            text=urdu_text,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        with open("voice.mp3", "wb") as f:
            for chunk in audio_stream:
                if chunk: f.write(chunk)

        # 4. Background from Pexels
        st.write("🎬 Downloading 4K Background...")
        headers = {"Authorization": PEXELS_KEY}
        px_res = requests.get("https://api.pexels.com/v1/videos/search?query=nature&orientation=portrait&per_page=1", headers=headers).json()
        video_url = px_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f: 
            f.write(requests.get(video_url).content)

        # 5. Assemble Video
        st.write("🛠️ Finalizing Video...")
        clip = VideoFileClip("bg.mp4").subclip(0, 30).resize(height=1920).crop(width=1080, height=1920, x_center=540)
        
        ready_text = fix_text(urdu_text)
        txt = TextClip(ready_text, font="Jameel.ttf", fontsize=55, color='white', method='caption', size=(900, None)).set_duration(clip.duration).set_position(('center', 1100))
        
        final = CompositeVideoClip([clip, txt]).set_audio(AudioFileClip("voice.mp3"))
        final.write_videofile("short.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        status.update(label="Short Ready!", state="complete")

    st.success(f"Viral Title: {viral_title}")
    st.video("short.mp4")
    with open("short.mp4", "rb") as f:
        st.download_button("📥 Download MP4", f, "Viral_Hadith.mp4")
