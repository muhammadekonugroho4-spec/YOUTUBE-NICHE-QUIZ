from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import urllib.request
import textwrap

FONT_PATH = "Roboto-Bold.ttf"
if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", FONT_PATH)

def create_text_clip(text, fontsize, color, max_chars=35, align="center"):
    lines = []
    for line in text.split('\n'):
        if line.strip() == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line, width=max_chars))
    wrapped_text = "\n".join(lines)
    font = ImageFont.truetype(FONT_PATH, fontsize)
    dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    try:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align=align)
        text_width = int(bbox[2] - bbox[0])
        text_height = int(bbox[3] - bbox[1])
    except AttributeError:
        text_width, text_height = draw.multiline_textsize(wrapped_text, font=font)
    text_width = max(text_width, 1)
    text_height = max(text_height, 1)
    img = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.multiline_text((20, 20), wrapped_text, font=font, fill=color, align=align)
    return ImageClip(np.array(img))

WIDTH, HEIGHT = 1080, 1920
BG_COLOR = (25, 25, 35)

def create_drama_video(drama_data, audio_dir="assets_audio", output_dir="output_videos"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print("🎬 Mulai merender video drama...")
    title = drama_data.get("title", "Drama Shorts")
    scenes = drama_data.get("scenes", [])
    
    final_clips = []
    
    for i, scene in enumerate(scenes):
        scene_num = i + 1
        audio_path = os.path.join(audio_dir, f"scene_{scene_num}.mp3")
        if not os.path.exists(audio_path):
            continue
            
        audio_clip = AudioFileClip(audio_path)
        bg = ColorClip(size=(WIDTH, HEIGHT), color=BG_COLOR)
        
        # Teks Judul Drama di atas
        txt_title = create_text_clip(title, fontsize=50, color="yellow", max_chars=35)
        txt_title = txt_title.set_position(('center', 150))
        
        # Nama Karakter
        char_name = scene.get("character_speaking", "Karakter")
        txt_char = create_text_clip(f"[{char_name}]", fontsize=60, color="#00FFFF", max_chars=30)
        txt_char = txt_char.set_position(('center', 600))
        
        # Teks Dialog
        dialogue = scene.get("narration_dialogue", "")
        txt_dialogue = create_text_clip(f'"{dialogue}"', fontsize=75, color="white", max_chars=25)
        txt_dialogue = txt_dialogue.set_position(('center', 800))
        
        # Teks Visual AI (Bisa ditutupi video asli nanti di CapCut)
        vis = scene.get("visual_description", "")
        txt_vis = create_text_clip(f"Visual AI: {vis}", fontsize=40, color="gray", max_chars=45)
        txt_vis = txt_vis.set_position(('center', 1600))
        
        scene_clip = CompositeVideoClip([bg, txt_title, txt_char, txt_dialogue, txt_vis])
        scene_clip = scene_clip.set_duration(audio_clip.duration).set_audio(audio_clip)
        
        final_clips.append(scene_clip)
        
    final_video = concatenate_videoclips(final_clips)
    output_filename = os.path.join(output_dir, "hasil_drama_shorts.mp4")
    
    print("⏳ Menyimpan file MP4 (Tunggu beberapa menit)...")
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    return output_filename