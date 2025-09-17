# app.py
"""
Streamlit app: Text → Speech → Voiceover Video
Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import asyncio
import tempfile
import time
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
import edge_tts
from PIL import Image

# ---------------- Config ---------------- #
VOICE_PRESETS = [
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-GB-LibbyNeural",
    "en-GB-RyanNeural",
    "en-AU-NatashaNeural",
    "en-CA-ClaraNeural",
    "en-IN-PrabhatNeural",
    "en-IN-NeerjaNeural",
]

# ---------------- Utils ---------------- #
def safe_filename(base: str, ext: str) -> str:
    ts = int(time.time())
    safe = "".join(c if c.isalnum() else "_" for c in base)[:40]
    return f"{safe}_{ts}.{ext}"


async def _synthesize(text: str, voice: str, outfile: str, rate: Optional[str], pitch: Optional[str]):
    prosody = ""
    if rate:
        prosody += f' rate="{rate}"'
    if pitch:
        prosody += f' pitch="{pitch}"'

    if prosody:
        ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"><voice name="{voice}"><prosody{prosody}>{text}</prosody></voice></speak>'
        communicate = edge_tts.Communicate(ssml, voice=voice)
    else:
        communicate = edge_tts.Communicate(text, voice=voice)

    await communicate.save(outfile)


def synthesize_tts(text: str, voice: str, out_path: Path, rate_pct: int, pitch_pct: int):
    rate = f"{rate_pct}%" if rate_pct else None
    pitch = f"{pitch_pct}%" if pitch_pct else None
    asyncio.run(_synthesize(text, voice, str(out_path), rate, pitch))


def create_video_with_voiceover(audio_path: str, video_path: Optional[str], image_path: Optional[str], out_path: str) -> Tuple[str, float]:
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    if video_path:
        video = VideoFileClip(video_path)
        if video.duration < duration:
            n = int(duration // video.duration) + 1
            video = concatenate_videoclips([video] * n).subclip(0, duration)
        else:
            video = video.subclip(0, duration)
        video = video.set_audio(audio_clip)
        video.write_videofile(out_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        video.close()
    else:
        if image_path:
            clip = ImageClip(image_path)
        else:
            img = Image.new("RGB", (1280, 720), color=(0, 0, 0))
            tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.save(tmp_img.name)
            clip = ImageClip(tmp_img.name)

        clip = clip.set_duration(duration).resize(height=720)
        clip = clip.set_audio(audio_clip)
        clip.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()

    audio_clip.close()
    return out_path, duration


# ---------------- Streamlit UI ---------------- #
st.set_page_config(page_title="Text → Voiceover Video", layout="centered")
st.title("🗣️ Text → 🎥 Video with Voiceover")

text_input = st.text_area("Enter narration text", height=200)

col1, col2 = st.columns(2)
with col1:
    voice = st.selectbox("Select Voice", VOICE_PRESETS)
with col2:
    rate = st.slider("Rate (%)", -40, 60, 0, step=5)
    pitch = st.slider("Pitch (%)", -20, 40, 0, step=5)

upload = st.file_uploader("Upload a video (mp4/mov/webm) or image (jpg/png).", type=["mp4", "mov", "webm", "jpg", "jpeg", "png"])

if st.button("Generate Video"):
    if not text_input.strip():
        st.error("Please enter some text.")
    else:
        with st.spinner("Generating speech..."):
            tmp_dir = Path(tempfile.mkdtemp())
            audio_file = tmp_dir / "voice.mp3"
            synthesize_tts(text_input, voice, audio_file, rate, pitch)

        video_path, image_path = None, None
        if upload:
            file_path = tmp_dir / upload.name
            with open(file_path, "wb") as f:
                f.write(upload.getbuffer())
            if file_path.suffix.lower() in [".mp4", ".mov", ".webm"]:
                video_path = str(file_path)
            else:
                image_path = str(file_path)

        out_video = tmp_dir / "output.mp4"
        with st.spinner("Composing video..."):
            final_video, dur = create_video_with_voiceover(str(audio_file), video_path, image_path, str(out_video))

        st.success("✅ Done!")
        st.video(final_video)

        with open(final_video, "rb") as f:
            st.download_button("Download MP4", f, file_name="voiceover_video.mp4", mime="video/mp4")
        with open(audio_file, "rb") as f:
            st.download_button("Download MP3", f, file_name="voiceover_audio.mp3", mime="audio/mpeg")
