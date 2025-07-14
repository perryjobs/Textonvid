import streamlit as st
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile

def typewriter_effect(text, duration, fps=24, font_size=70, color='white', bg_color='black', size=(640, 480)):
    num_chars = len(text)
    char_duration = duration / num_chars
    clips = []

    for i in range(1, num_chars + 1):
        txt = TextClip(text[:i], fontsize=font_size, color=color, bg_color=bg_color, size=size)
        txt = txt.set_duration(char_duration).set_fps(fps)
        clips.append(txt)

    return concatenate_videoclips(clips)

def overlay_text_on_video(input_path, output_path, text, duration):
    video = VideoFileClip(input_path)
    text_clip = typewriter_effect(text, duration).set_position('center').set_start(0)
    final_clip = CompositeVideoClip([video, text_clip.set_duration(video.duration)])
    final_clip.write_videofile(output_path, codec='libx264', fps=video.fps)

st.title("🎞️ Text-on-Video Generator with Typewriter Effect")

uploaded_file = st.file_uploader("Upload a video", type=["mp4"])
text_input = st.text_input("Enter the text to overlay")
duration = st.slider("Duration of text animation (seconds)", 1, 10, 5)

if uploaded_file and text_input:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input_path = temp_input.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
        output_path = temp_output.name

    with st.spinner("Processing video..."):
        overlay_text_on_video(temp_input_path, output_path, text_input, duration)
        st.success("Done!")

    st.video(output_path)
    with open(output_path, "rb") as f:
        st.download_button("Download video", f, file_name="output_video.mp4")
