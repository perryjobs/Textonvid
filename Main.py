import cv2
import numpy as np
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def typewriter_effect(text, duration, fps=24):
    clip = TextClip(text, fontsize=70, color='white', bg_color='black', size=(640, 480))
    clip = clip.set_duration(duration).set_fps(fps)
    return clip

def overlay_text_on_video(video_path, output_path, text, duration):
    video = VideoFileClip(video_path)
    text_clip = typewriter_effect(text, duration)
    text_clip = text_clip.set_position('center').set_start(0)

    final_clip = CompositeVideoClip([video, text_clip])
    final_clip.write_videofile(output_path, codec='libx264', fps=video.fps)

video_path = 'input_video.mp4'
output_path = 'output_video.mp4'
text = 'Hello, World!'
duration = 5  # Duration for the text overlay in seconds

overlay_text_on_video(video_path, output_path, text, duration)
