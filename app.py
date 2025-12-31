import streamlit as st
import asyncio
import edge_tts
import requests
import random
import os
import uuid
import google.generativeai as genai
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from proglog import ProgressBarLogger # <--- New Import
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# --- CUSTOM PROGRESS LOGGER ---
class StreamlitProgressLogger(ProgressBarLogger):
    def __init__(self, st_bar, st_text):
        super().__init__()
        self.st_bar = st_bar
        self.st_text = st_text

    def callback(self, **changes):
        # MoviePy's rendering has two main bars: 't' (frames) and 'chunk' (audio)
        if 'bars' in self.state:
            # We track the 't' bar which represents the frames being written
            video_bar = self.state['bars'].get('t')
            if video_bar:
                percentage = video_bar['index'] / video_bar['total']
                self.st_bar.progress(percentage)
                self.st_text.text(f"🎬 Rendering Video: {int(percentage * 100)}%")

# ... (Previous helper functions: fix_text, check_fonts, generate_voice_sync) ...

if st.button("🚀 Generate Viral Hadith Short"):
    # Setup unique IDs and paths
    session_id = str(uuid.uuid4())[:8]
    v_audio = f"voice_{session_id}.mp3"
    v_bg = f"bg_{session_id}.mp4"
    v_final = f"short_{session_id}.mp4"
    
    with st.status("Work in Progress...", expanded=True) as status:
        # [Steps 1-4 remain the same: Hadith, Gemini, Voice, Pexels]
        # ... 

        # --- STEP 5: ASSEMBLE WITH PROGRESS BAR ---
        st.write("🛠️ Initializing Video Engine...")
        
        # Create the UI elements for progress
        render_text = st.empty()
        render_bar = st.progress(0)
        custom_logger = StreamlitProgressLogger(render_bar, render_text)

        audio_clip = AudioFileClip(v_audio)
        clip = VideoFileClip(v_bg).subclip(0, min(audio_clip.duration, 30)).resize(height=1280)
        
        txt = TextClip(fix_text(urdu_text), font="Jameel.ttf", fontsize=45, color='white', 
                       method='caption', size=(clip.w * 0.8, None)).set_duration(clip.duration).set_position('center')

        final_video = CompositeVideoClip([clip, txt]).set_audio(audio_clip)

        # We pass our custom logger here
        final_video.write_videofile(
            v_final, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            logger=custom_logger # <--- The Magic Happens Here
        )

        # Clean up progress bar after completion
        render_text.empty()
        render_bar.empty()
        status.update(label="✅ Video Ready!", state="complete")

    st.video(v_final)
    # ... (Download button and cleanup) ...
