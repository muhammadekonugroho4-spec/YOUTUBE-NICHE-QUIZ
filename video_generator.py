import os
import re

# ==========================================
# 1. PATCH KEAMANAN IMAGEMAGICK (WAJIB DI PALING ATAS)
# ==========================================
# Patch ini harus dijalankan sebelum MoviePy di-import
try:
    os.makedirs("/tmp/magick", exist_ok=True)
    if os.path.exists("/etc/ImageMagick-6/policy.xml"):
        with open("/etc/ImageMagick-6/policy.xml", "r") as f:
            policy = f.read()
        
        # Memaksa mengubah hak akses dari "none" menjadi "read|write" secara brutal (Anti-Gagal)
        policy = re.sub(r'rights="none"\s+pattern="@\*"', 'rights="read|write" pattern="@*"', policy)
        
        with open("/tmp/magick/policy.xml", "w") as f:
            f.write(policy)
        
        # Paksa server menggunakan konfigurasi yang sudah diizinkan
        os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp/magick"
except Exception as e:
    print(f"Peringatan Patch: {e}")

# ==========================================
# 2. IMPORT MOVIEPY (Setelah Patch Aktif)
# ==========================================
from moviepy.editor import *

# ==========================================
# PENGATURAN RESOLUSI & WARNA (YOUTUBE SHORTS)
# ==========================================
WIDTH = 1080
HEIGHT = 1920
BG_COLOR = (25, 25, 35)       
TEXT_COLOR = 'white'
HIGHLIGHT_COLOR = 'green'     

def create_quiz_video(question_data: dict, index: int, audio_dir: str = "assets_audio", output_dir: str = "output_videos"):
    """
    Merender 1 soal kuis menjadi 1 file video .mp4 vertikal.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🎬 Mulai merender video untuk soal ke-{index}...")

    # Siapkan Audio
    audio_soal = AudioFileClip(os.path.join(audio_dir, f"soal_{index}.mp3"))
    audio_jawaban = AudioFileClip(os.path.join(audio_dir, f"jawaban_{index}.mp3"))

    # Background
    bg_clip = ColorClip(size=(WIDTH, HEIGHT), color=BG_COLOR)

    # Teks Soal & Pilihan
    abjad = ["A", "B", "C", "D"]
    teks_pilihan = "\n\n".join([f"{abjad[i]}. {opsi}" for i, opsi in enumerate(question_data['options'])])

    txt_soal = TextClip(question_data['question'], fontsize=70, color=TEXT_COLOR, 
                        font='DejaVu-Sans-Bold', size=(WIDTH - 150, None), method='caption', align='center')
    
    txt_opsi = TextClip(teks_pilihan, fontsize=60, color=TEXT_COLOR, 
                        font='DejaVu-Sans', size=(WIDTH - 150, None), method='caption', align='West')

    txt_soal = txt_soal.set_position(('center', 400))
    txt_opsi = txt_opsi.set_position(('center', 800))

    # Klip 1: Soal
    clip_1 = CompositeVideoClip([bg_clip, txt_soal, txt_opsi])
    clip_1 = clip_1.set_duration(audio_soal.duration).set_audio(audio_soal)

    # Klip 2: Timer
    timer_clips = []
    for i in range(question_data['time_limit'], 0, -1):
        txt_angka = TextClip(str(i), fontsize=150, color='yellow', font='DejaVu-Sans-Bold')
        txt_angka = txt_angka.set_position(('center', 1400)).set_duration(1)
        frame = CompositeVideoClip([bg_clip, txt_soal, txt_opsi, txt_angka]).set_duration(1)
        timer_clips.append(frame)
    
    clip_2 = concatenate_videoclips(timer_clips)

    # Klip 3: Jawaban & Fakta Unik
    teks_jawaban_benar = f"Jawaban:\n{question_data['correct_answer']}"
    txt_benar = TextClip(teks_jawaban_benar, fontsize=80, color=HIGHLIGHT_COLOR, 
                         font='DejaVu-Sans-Bold', size=(WIDTH - 150, None), method='caption', align='center')
    txt_benar = txt_benar.set_position(('center', 800))

    txt_fakta = TextClip(question_data['fun_fact'], fontsize=50, color='yellow', 
                         font='DejaVu-Sans', size=(WIDTH - 150, None), method='caption', align='center')
    txt_fakta = txt_fakta.set_position(('center', 1200))

    clip_3 = CompositeVideoClip([bg_clip, txt_soal, txt_benar, txt_fakta])
    clip_3 = clip_3.set_duration(audio_jawaban.duration).set_audio(audio_jawaban)

    # Gabung dan Render
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