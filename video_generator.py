from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import urllib.request
import textwrap

# ==========================================
# 1. DOWNLOAD FONT OTOMATIS (ANTI GAGAL)
# ==========================================
FONT_PATH = "Roboto-Bold.ttf"
if not os.path.exists(FONT_PATH):
    print("Mendownload font agar teks bisa dirender di semua server...")
    urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf", FONT_PATH)

# ==========================================
# 2. MESIN TEKS PENGGANTI IMAGEMAGICK (ANTI ERROR)
# ==========================================
def create_text_clip(text, fontsize, color, max_chars=35, align="center"):
    """
    Merender teks menjadi gambar transparan menggunakan Pillow.
    Ini menggantikan TextClip bawaan MoviePy yang sering error di Linux/Cloud.
    """
    # Membungkus teks agar tidak melebar keluar layar video
    lines = []
    for line in text.split('\n'):
        if line.strip() == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line, width=max_chars))
    wrapped_text = "\n".join(lines)
    
    # Inisialisasi font dan kanvas gambar virtual
    font = ImageFont.truetype(FONT_PATH, fontsize)
    dummy_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)
    
    # Menghitung lebar dan tinggi teks
    try:
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align=align)
        text_width = int(bbox[2] - bbox[0])
        text_height = int(bbox[3] - bbox[1])
    except AttributeError:
        # Fallback untuk versi Pillow lama
        text_width, text_height = draw.multiline_textsize(wrapped_text, font=font)
        
    # Pastikan ukuran tidak nol
    text_width = max(text_width, 1)
    text_height = max(text_height, 1)
    
    # Buat gambar asli transparan dengan sedikit ruang tambahan (padding)
    img = Image.new('RGBA', (text_width + 40, text_height + 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.multiline_text((20, 20), wrapped_text, font=font, fill=color, align=align)
    
    # Kembalikan sebagai ImageClip MoviePy
    return ImageClip(np.array(img))


# ==========================================
# PENGATURAN RESOLUSI & WARNA (YOUTUBE SHORTS)
# ==========================================
WIDTH = 1080
HEIGHT = 1920
BG_COLOR = (25, 25, 35)       
TEXT_COLOR = 'white'
HIGHLIGHT_COLOR = '#00FF00'  # Hijau Terang

def create_quiz_video(question_data: dict, index: int, audio_dir: str = "assets_audio", output_dir: str = "output_videos"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🎬 Mulai merender video untuk soal ke-{index}...")

    # 1. Siapkan Audio
    audio_soal = AudioFileClip(os.path.join(audio_dir, f"soal_{index}.mp3"))
    audio_jawaban = AudioFileClip(os.path.join(audio_dir, f"jawaban_{index}.mp3"))

    # 2. Background
    bg_clip = ColorClip(size=(WIDTH, HEIGHT), color=BG_COLOR)

    # 3. Pembuatan Teks Menggunakan Fungsi Pillow (Bebas Error)
    abjad = ["A", "B", "C", "D"]
    teks_pilihan = "\n\n".join([f"{abjad[i]}. {opsi}" for i, opsi in enumerate(question_data['options'])])

    txt_soal = create_text_clip(question_data['question'], fontsize=65, color=TEXT_COLOR, max_chars=30)
    txt_opsi = create_text_clip(teks_pilihan, fontsize=60, color=TEXT_COLOR, max_chars=35, align="left")

    txt_soal = txt_soal.set_position(('center', 400))
    txt_opsi = txt_opsi.set_position(('center', 800))

    # Klip 1: Pembacaan Soal
    clip_1 = CompositeVideoClip([bg_clip, txt_soal, txt_opsi])
    clip_1 = clip_1.set_duration(audio_soal.duration).set_audio(audio_soal)

    # Klip 2: Timer Countdown
    timer_clips = []
    for i in range(question_data['time_limit'], 0, -1):
        txt_angka = create_text_clip(str(i), fontsize=150, color='yellow')
        txt_angka = txt_angka.set_position(('center', 1400)).set_duration(1)
        frame = CompositeVideoClip([bg_clip, txt_soal, txt_opsi, txt_angka]).set_duration(1)
        timer_clips.append(frame)
    
    clip_2 = concatenate_videoclips(timer_clips)

    # Klip 3: Pembacaan Jawaban
    teks_jawaban_benar = f"Jawaban:\n{question_data['correct_answer']}"
    txt_benar = create_text_clip(teks_jawaban_benar, fontsize=80, color=HIGHLIGHT_COLOR, max_chars=25)
    txt_benar = txt_benar.set_position(('center', 800))

    txt_fakta = create_text_clip(question_data['fun_fact'], fontsize=50, color='yellow', max_chars=35)
    txt_fakta = txt_fakta.set_position(('center', 1200))

    clip_3 = CompositeVideoClip([bg_clip, txt_soal, txt_benar, txt_fakta])
    clip_3 = clip_3.set_duration(audio_jawaban.duration).set_audio(audio_jawaban)

    # Gabung Semua Klip
    final_video = concatenate_videoclips([clip_1, clip_2, clip_3])
    
    output_filename = os.path.join(output_dir, f"video_soal_{index}.mp4")
    print("⏳ Sedang memproses dan menyimpan file MP4 (Ini butuh beberapa waktu)...")
    
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video berhasil dirender: {output_filename}")


if __name__ == "__main__":
    sample_question = {
        "question": "Negara manakah yang memiliki ibukota bernama Helsinki?",
        "options": ["Norwegia", "Swedia", "Finlandia", "Denmark"],
        "correct_answer": "Finlandia",
        "time_limit": 5,
        "fun_fact": "Helsinki memiliki julukan Kota Putih dari Utara karena banyak bangunan terbuat dari granit terang."
    }
    create_quiz_video(sample_question, index=1)