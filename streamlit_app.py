import streamlit as st
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import tempfile
import numpy as np
import os
import textwrap

def generate_typewriter_clips(text, duration, size=(640, 480), font_size=60, color='white', fps=24, font_path="DejaVuSans-Bold.ttf"):
    width, height = size
    num_chars = len(text)
    char_duration = duration / max(1, num_chars)
    clips = []

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # Calculate wrap width with margins
    usable_width = width - 20  # Add small horizontal padding
    avg_char_width = font_size // 1.5
    max_chars_per_line = usable_width // avg_char_width

    # Wrap text
    wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
    full_text = "\n".join(wrapped_lines)


    for i in range(1, len(full_text) + 1):
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        current_text = full_text[:i]
        lines = current_text.split("\n")
        total_text_height = sum([font.getbbox(line)[3] for line in lines])

        y = (height - total_text_height) // 2
        for line in lines:
            if line.strip() == "":
                continue
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) // 2
            draw.text((x, y), line, font=font, fill=color)
            y += bbox[3] - bbox[1]

        frame = np.array(img)
        clip = ImageClip(frame, ismask=False).set_duration(char_duration)
        clips.append(clip)

    return clips

def overlay_text_on_video(input_path, output_path, text, animation_duration):
    try:
        video = VideoFileClip(input_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load video: {e}")

    video_size = video.size
    text_clips = generate_typewriter_clips(text, animation_duration, size=video_size)
    text_anim = concatenate_videoclips(text_clips)

    if video.duration > animation_duration:
        last_frame = text_clips[-1].set_duration(video.duration - animation_duration)
        text_anim = concatenate_videoclips([text_anim, last_frame])

    text_anim = text_anim.set_position('center').set_start(0)
    final = CompositeVideoClip([video, text_anim])
    final.write_videofile(output_path, codec='libx264', fps=video.fps)

# --- Streamlit UI ---
st.title("📝 Typewriter Text on Video (Transparent & Responsive)")

uploaded_file = st.file_uploader("Upload a video (.mp4)", type=["mp4"])
text_input = st.text_area("Enter text for animation")
duration = st.slider("Text animation duration (seconds)", 1, 10, 5)

if uploaded_file and text_input:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input.flush()
        input_path = temp_input.name

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
