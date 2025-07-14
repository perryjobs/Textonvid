import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile

def typewriter_effect(text, duration, fps=24, font_size=70, color='white', bg_color='black', size=(640, 480)):
    num_chars = len(text)
    char_duration = duration / max(1, num_chars)
    clips = []

    for i in range(1, num_chars + 1):
        txt = TextClip(
            text[:i],
            fontsize=font_size,
            color=color,
            bg_color=bg_color,
            size=size,
            method='caption'  # ✅ Uses PIL instead of ImageMagick
        )
        txt = txt.set_duration(char_duration).set_fps(fps)
        clips.append(txt)

    return concatenate_videoclips(clips)

def overlay_text_on_video(input_path, output_path, text, duration):
    video = VideoFileClip(input_path)
    text_clip = typewriter_effect(text, duration).set_position('center').set_start(0)
    final = CompositeVideoClip([video, text_clip.set_duration(video.duration)])
    final.write_videofile(output_path, codec='libx264', fps=video.fps)

st.title("🎬 Typewriter Text on Video")

uploaded_file = st.file_uploader("Upload a video (.mp4)", type=["mp4"])
text_input = st.text_input("Enter text for typewriter animation")
duration = st.slider("Animation duration (seconds)", 1, 10, 5)

if uploaded_file and text_input:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
        output_path = temp_output.name

    with st.spinner("Processing..."):
        overlay_text_on_video(input_path, output_path, text_input, duration)
        st.success("✅ Done!")

    st.video(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download Video", f, file_name="output_video.mp4")
