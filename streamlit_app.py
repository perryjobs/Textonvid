import streamlit as st
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import tempfile
import numpy as np
import os

def generate_typewriter_clips(text, duration, fps=24, font_size=60, size=(640, 480), color='white', bg_color='black'):
    num_chars = len(text)
    char_duration = duration / max(1, num_chars)
    clips = []

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)  # Safe default on many systems
    except:
        font = ImageFont.load_default()

    for i in range(1, num_chars + 1):
        img = Image.new('RGB', size, color=bg_color)
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(text[:i], font=font)
        draw.text(((size[0]-w)//2, (size[1]-h)//2), text[:i], font=font, fill=color)

        frame = np.array(img)
        clip = ImageClip(frame).set_duration(char_duration)
        clips.append(clip)

    return clips

def overlay_text_on_video(input_path, output_path, text, duration):
    video = VideoFileClip(input_path)
    text_clips = generate_typewriter_clips(text, duration)
    from moviepy.editor import concatenate_videoclips
    text_anim = concatenate_videoclips(text_clips).set_position('center').set_start(0)
    final = CompositeVideoClip([video, text_anim.set_duration(video.duration)])
    final.write_videofile(output_path, codec='libx264', fps=video.fps)

st.title("📝 Typewriter Text on Video (No TextClip)")

uploaded_file = st.file_uploader("Upload a video (.mp4)", type=["mp4"])
text_input = st.text_input("Enter text for animation")
duration = st.slider("Text animation duration (seconds)", 1, 10, 5)

if uploaded_file and text_input:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
        output_path = temp_output.name

    with st.spinner("Generating video..."):
        overlay_text_on_video(input_path, output_path, text_input, duration)
        st.success("✅ Video ready!")

    st.video(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download video", f, file_name="output_video.mp4")
