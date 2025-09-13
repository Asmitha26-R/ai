import streamlit as st
import tempfile
import os
from pathlib import Path
import base64
from video_generator import VideoGenerator
from audio_generator import AudioGenerator
import time

# Page config
st.set_page_config(
    page_title="AI Video Creator",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        font-weight: 600;
    }
    .success-box {
        background: #d1fae5;
        border: 2px solid #10b981;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎬 AI Video Creator</h1>
    <p>Generate professional videos with AI voiceover from text</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_video' not in st.session_state:
    st.session_state.generated_video = None
if 'generated_audio' not in st.session_state:
    st.session_state.generated_audio = None

# Sidebar for settings
with st.sidebar:
    st.header("🎛️ Video Settings")
    
    # Voice settings
    st.subheader("🎙️ Voice Options")
    voice_type = st.selectbox(
        "Voice Type",
        ["Female Professional", "Male Professional", "Female Casual", "Male Deep", "Energetic Female"]
    )
    
    voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0, 0.1)
    
    # Video settings
    st.subheader("🎥 Video Options")
    video_style = st.selectbox(
        "Video Style",
        ["Modern", "Corporate", "Creative", "Tech", "Minimal", "Dynamic"]
    )
    
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)"]
    )
    
    video_duration = st.selectbox(
        "Duration",
        ["15 seconds", "30 seconds", "60 seconds", "90 seconds"]
    )
    
    video_quality = st.selectbox(
        "Quality",
        ["HD (720p)", "Full HD (1080p)", "4K (2160p)"]
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Script Input")
    
    # Text input
    script_text = st.text_area(
        "Enter your video script:",
        value="Welcome to our revolutionary AI platform! Transform your ideas into stunning videos with just a few clicks. Our advanced technology creates professional content that engages your audience and drives real results.",
        height=200,
        help="Write the script for your video. The AI will generate visuals and voiceover based on this text."
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        background_music = st.checkbox("Add background music")
        auto_captions = st.checkbox("Generate automatic captions", value=True)
        custom_branding = st.checkbox("Add custom branding")
        
        if custom_branding:
            brand_color = st.color_picker("Brand Color", "#4f46e5")
            logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
    
    # Generate button
    if st.button("🎬 Generate Video with AI", type="primary", use_container_width=True):
        if script_text.strip():
            with st.spinner("🎬 Generating your AI video..."):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Generate audio
                    status_text.text("🎙️ Generating AI voiceover...")
                    progress_bar.progress(25)
                    
                    audio_gen = AudioGenerator()
                    audio_file = audio_gen.generate_speech(
                        text=script_text,
                        voice_type=voice_type,
                        speed=voice_speed
                    )
                    st.session_state.generated_audio = audio_file
                    time.sleep(1)
                    
                    # Step 2: Generate video scenes
                    status_text.text("🎨 Creating video scenes...")
                    progress_bar.progress(50)
                    
                    video_gen = VideoGenerator()
                    video_scenes = video_gen.generate_scenes(
                        script=script_text,
                        style=video_style,
                        aspect_ratio=aspect_ratio,
                        duration=int(video_duration.split()[0])
                    )
                    time.sleep(2)
                    
                    # Step 3: Combine audio and video
                    status_text.text("🎬 Combining audio and video...")
                    progress_bar.progress(75)
                    
                    final_video = video_gen.combine_audio_video(
                        video_scenes=video_scenes,
                        audio_file=audio_file,
                        add_captions=auto_captions
                    )
                    time.sleep(1)
                    
                    # Step 4: Final processing
                    status_text.text("✨ Final processing...")
                    progress_bar.progress(100)
                    
                    st.session_state.generated_video = final_video
                    time.sleep(1)
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.success("🎉 Video generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating video: {str(e)}")
                    st.info("💡 Make sure you have all required dependencies installed")
        else:
            st.warning("⚠️ Please enter a script for your video!")

with col2:
    st.header("🎥 Video Preview")
    
    if st.session_state.generated_video:
        # Display video
        st.video(st.session_state.generated_video)
        
        # Video info
        st.markdown("""
        <div class="success-box">
            <h4>✅ Video Generated Successfully!</h4>
            <p><strong>Duration:</strong> {}</p>
            <p><strong>Style:</strong> {}</p>
            <p><strong>Voice:</strong> {}</p>
            <p><strong>Quality:</strong> {}</p>
        </div>
        """.format(video_duration, video_style, voice_type, video_quality), unsafe_allow_html=True)
        
        # Download options
        st.subheader("📥 Download Options")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("📱 Download MP4", use_container_width=True):
                with open(st.session_state.generated_video, "rb") as file:
                    st.download_button(
                        label="💾 Download Video",
                        data=file.read(),
                        file_name=f"ai_video_{int(time.time())}.mp4",
                        mime="video/mp4"
                    )
        
        with col_b:
            if st.button("🎵 Download Audio", use_container_width=True):
                if st.session_state.generated_audio:
                    with open(st.session_state.generated_audio, "rb") as file:
                        st.download_button(
                            label="💾 Download Audio",
                            data=file.read(),
                            file_name=f"ai_audio_{int(time.time())}.mp3",
                            mime="audio/mp3"
                        )
        
        with col_c:
            if st.button("📊 Get Analytics", use_container_width=True):
                st.info("📈 Video analytics would be available in the full version")
        
        # Audio controls
        if st.session_state.generated_audio:
            st.subheader("🎙️ Audio Controls")
            st.audio(st.session_state.generated_audio)
            
            col_x, col_y = st.columns(2)
            with col_x:
                if st.button("🔄 Regenerate Voice"):
                    st.info("🎙️ Regenerating with different voice settings...")
            with col_y:
                if st.button("⚡ Enhance Audio"):
                    st.info("✨ Audio enhancement would be applied")
    
    else:
        # Placeholder
        st.markdown("""
        <div style="
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 3rem;
            text-align: center;
            background: #f8f9fa;
            margin: 2rem 0;
        ">
            <h3>🎬 Video Preview</h3>
            <p>Your AI-generated video will appear here</p>
            <p style="color: #666;">Enter a script and click generate to start</p>
        </div>
        """, unsafe_allow_html=True)

# Footer with instructions
st.markdown("---")
st.markdown("""
### 🚀 How to Use:
1. **Enter your script** in the text area on the left
2. **Customize settings** in the sidebar (voice, style, duration)
3. **Click Generate** to create your AI video with voiceover
4. **Preview and download** your completed video

### 💡 Tips:
- Keep scripts between 50-500 words for best results
- Use clear, conversational language for better voice synthesis
- Choose video styles that match your content theme
- Higher quality settings take longer to process

### 🔧 Technical Requirements:
- Python 3.8+
- FFmpeg installed on your system
- Internet connection for AI services
""")

2. audio_generator.py (Audio Generation):

import os
import tempfile
from pathlib import Path
import pyttsx3
import wave
import numpy as np
from pydub import AudioSegment
import streamlit as st

class AudioGenerator:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.setup_voice_engine()
    
    def setup_voice_engine(self):
        """Configure the TTS engine"""
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def generate_speech(self, text, voice_type="Female Professional", speed=1.0):
        """Generate speech from text"""
        try:
            # Configure voice based on selection
            self.configure_voice(voice_type, speed)
            
            # Create temporary file
            temp_dir = tempfile.mkdtemp()
            audio_file = os.path.join(temp_dir, "generated_audio.wav")
            
            # Generate speech
            self.engine.save_to_file(text, audio_file)
            self.engine.runAndWait()
            
            # Convert to MP3 for better compatibility
            mp3_file = os.path.join(temp_dir, "generated_audio.mp3")
            self.convert_to_mp3(audio_file, mp3_file)
            
            return mp3_file
            
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return None
    
    def configure_voice(self, voice_type, speed):
        """Configure voice settings based on selection"""
        voices = self.engine.getProperty('voices')
        
        # Voice mapping
        voice_config = {
            "Female Professional": {"index": 0, "rate": 160},
            "Male Professional": {"index": 1 if len(voices) > 1 else 0, "rate": 150},
            "Female Casual": {"index": 0, "rate": 170},
            "Male Deep": {"index": 1 if len(voices) > 1 else 0, "rate": 140},
            "Energetic Female": {"index": 0, "rate": 180}
        }
        
        config = voice_config.get(voice_type, voice_config["Female Professional"])
        
        if len(voices) > config["index"]:
            self.engine.setProperty('voice', voices[config["index"]].id)
        
        self.engine.setProperty('rate', int(config["rate"] * speed))
    
    def convert_to_mp3(self, wav_file, mp3_file):
        """Convert WAV to MP3"""
        try:
            if os.path.exists(wav_file):
                audio = AudioSegment.from_wav(wav_file)
                audio.export(mp3_file, format="mp3")
                return mp3_file
            return wav_file
        except Exception as e:
            print(f"Conversion error: {e}")
            return wav_file

3. video_generator.py (Video Generation):

import os
import tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
from moviepy.video.fx import resize
import streamlit as st
import random

class VideoGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.frame_rate = 30
        self.default_duration = 30
    
    def generate_scenes(self, script, style="Modern", aspect_ratio="16:9", duration=30):
        """Generate video scenes based on script"""
        try:
            # Parse aspect ratio
            width, height = self.get_dimensions(aspect_ratio)
            
            # Split script into scenes
            scenes = self.split_into_scenes(script, duration)
            
            # Generate visual scenes
            scene_files = []
            for i, scene_text in enumerate(scenes):
                scene_file = self.create_scene(
                    text=scene_text,
                    style=style,
                    width=width,
                    height=height,
                    duration=len(scenes),
                    scene_number=i
                )
                scene_files.append(scene_file)
            
            return scene_files
            
        except Exception as e:
            st.error(f"Error generating scenes: {str(e)}")
            return []
    
    def get_dimensions(self, aspect_ratio):
        """Get video dimensions based on aspect ratio"""
        ratios = {
            "16:9 (Landscape)": (1920, 1080),
            "9:16 (Portrait)": (1080, 1920),
            "1:1 (Square)": (1080, 1080)
        }
        return ratios.get(aspect_ratio, (1920, 1080))
    
    def split_into_scenes(self, script, duration):
        """Split script into scenes based on duration"""
        words = script.split()
        words_per_second = 2.5  # Average speaking speed
        words_per_scene = int(words_per_second * (duration / 3))  # 3 scenes
        
        scenes = []
        for i in range(0, len(words), words_per_scene):
            scene = " ".join(words[i:i + words_per_scene])
            scenes.append(scene)
        
        return scenes[:3]  # Limit to 3 scenes
    
    def create_scene(self, text, style, width, height, duration, scene_number):
        """Create a single video scene"""
        try:
            # Create background based on style
            background = self.create_background(style, width, height)
            
            # Add text overlay
            scene_image = self.add_text_overlay(background, text, width, height)
            
            # Create video clip from image
            scene_file = os.path.join(self.temp_dir, f"scene_{scene_number}.mp4")
            
            # Convert PIL image to numpy array
            frame = np.array(scene_image)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(scene_file, fourcc, self.frame_rate, (width, height))
            
            # Write frames (create 3-second clip per scene)
            frames_per_scene = self.frame_rate * 3
            for _ in range(frames_per_scene):
                out.write(frame)
            
            out.release()
            return scene_file
            
        except Exception as e:
            st.error(f"Error creating scene: {str(e)}")
            return None
    
    def create_background(self, style, width, height):
        """Create background based on style"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Style-based gradients
        styles = {
            "Modern": [(67, 126, 234), (118, 75, 162)],
            "Corporate": [(102, 126, 234), (118, 75, 162)],
            "Creative": [(250, 112, 154), (254, 225, 64)],
            "Tech": [(79, 172, 254), (0, 242, 254)],
            "Minimal": [(255, 255, 255), (240, 240, 240)],
            "Dynamic": [(255, 154, 158), (250, 208, 196)]
        }
        
        colors = styles.get(style, styles["Modern"])
        
        # Create gradient
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return img
    
    def add_text_overlay(self, background, text, width, height):
        """Add text overlay to background"""
        draw = ImageDraw.Draw(background)
        
        # Try to load a font, fallback to default
        try:
            font_size = max(24, width // 40)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        wrapped_text = self.wrap_text(text, font, width - 200)
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Add text shadow
        draw.text((x + 2, y + 2), wrapped_text, font=font, fill=(0, 0, 0, 128))
        # Add main text
        draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255))
        
        return background
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def combine_audio_video(self, video_scenes, audio_file, add_captions=True):
        """Combine video scenes with audio"""
        try:
            if not video_scenes or not audio_file:
                return None
            
            # Load audio
            audio = mp.AudioFileClip(audio_file)
            
            # Load and concatenate video scenes
            video_clips = []
            for scene_file in video_scenes:
                if scene_file and os.path.exists(scene_file):
                    clip = mp.VideoFileClip(scene_file)
                    video_clips.append(clip)
            
            if not video_clips:
                return None
            
            # Concatenate video clips
            final_video = mp.concatenate_videoclips(video_clips)
            
            # Adjust video duration to match audio
            if final_video.duration < audio.duration:
                # Loop video if it's shorter than audio
                final_video = final_video.loop(duration=audio.duration)
            else:
                # Trim video if it's longer than audio
                final_video = final_video.subclip(0, audio.duration)
            
            # Add audio to video
            final_video = final_video.set_audio(audio)
            
            # Export final video
            output_file = os.path.join(self.temp_dir, "final_video.mp4")
            final_video.write_videofile(
                output_file,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            return output_file
            
        except Exception as e:
            st.error(f"Error combining audio and video: {str(e)}")
            return None

4. requirements.txt:

streamlit==1.28.1
moviepy==1.0.3
opencv-python==4.8.1.78
Pillow==10.0.1
pyttsx3==2.90
pydub==0.25.1
numpy==1.24.3

5. Installation & Run Instructions:

Create a new folder and add all files, then run:

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video processing)
# Windows: Download from https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# Run the app
streamlit run app.py