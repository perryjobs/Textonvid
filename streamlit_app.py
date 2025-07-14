import streamlit as st
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import tempfile
import numpy as np
import os

def generate_typewriter_clips(text, duration, fps=24, font_size=60, size=(640, 480), color='white'):
    num_chars = len(text)
    char_duration = duration / max(1, num_chars)
    clips = []

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for i in range(1, num_chars + 1):
        # Transparent RGBA image
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text[:i], font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((size[0] - w) // 2, (size[1] - h) // 2), text[:i], font=font, fill=color)

        frame = np.array(img)
        clip = ImageClip(frame, ismask=False).set_duration(char_duration)
        clips.append(clip)

    return clips

def overlay_text_on_video(input_path, output_path, text, animation_duration):
    try:
        video = VideoFileClip(input_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load video: {e}")

    text_clips = generate_typewriter_clips(text, animation_duration)
    text_anim = concatenate_videoclips(text_clips)

    if video.duration > animation_duration:
        last_frame = text_clips[-1].set_duration(video.duration - animation_duration)
        text_anim = concatenate_videoclips([text_anim, last_frame])

    text_anim = text_anim.set_position('center').set_start(0)
    final = CompositeVideoClip([video, text_anim])
    final.write_videofile(output_path, codec='libx264', fps=video.fps)

# --- Streamlit UI ---
st.title("📝 Typewriter Text on Video (No TextClip)")

uploaded_file = st.file_uploader("Upload a video (.mp4)", type=["mp4"])
text_input = st.text_input("Enter text for animation")
duration = st.slider("Text animation duration (seconds)", 1, 10, 5)

if uploaded_file and text_input:
    # Save video safely
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input.flush()
        input_path = temp_input.name

    # Validate file size
    if os.path.getsize(input_path) == 0:
        st.error("❌ Uploaded video file is empty or corrupted.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
            output_path = temp_output.name

        with st.spinner("🔄 Generating video..."):
            try:
                overlay_text_on_video(input_path, output_path, text_input, duration)
                st.success("✅ Video ready!")
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download video", f, file_name="output_video.mp4")
            except Exception as e:
                st.error(f"❌ Processing failed: {e}")
