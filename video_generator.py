from moviepy.editor import *
import os

# --- PATCH KEAMANAN IMAGEMAGICK UNTUK LINUX & STREAMLIT CLOUD ---
if os.path.exists("/etc/ImageMagick-6/policy.xml"):
    with open("/etc/ImageMagick-6/policy.xml", "r") as f:
        policy_data = f.read()
    # Mengubah izin dari 'none' menjadi 'read|write'
    policy_data = policy_data.replace('rights="none" pattern="@*"', 'rights="read|write" pattern="@*"')
    os.makedirs("/tmp/magick", exist_ok=True)
    with open("/tmp/magick/policy.xml", "w") as f:
        f.write(policy_data)
    # Memaksa ImageMagick membaca konfigurasi baru yang sudah diizinkan
    os.environ["MAGICK_CONFIGURE_PATH"] = "/tmp/magick"
# -----------------------------------------------------------------

# ==========================================
# PENGATURAN RESOLUSI & WARNA (YOUTUBE SHORTS)
# ==========================================
# Resolusi vertikal (9:16)
WIDTH = 1080
HEIGHT = 1920

# Warna dasar
BG_COLOR = (25, 25, 35)       # Biru dongker gelap (Background)
TEXT_COLOR = 'white'
HIGHLIGHT_COLOR = 'green'     # Warna jawaban benar

def create_quiz_video(question_data: dict, index: int, audio_dir: str = "assets_audio", output_dir: str = "output_videos"):
    """
    Merender 1 soal kuis menjadi 1 file video .mp4 vertikal.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"🎬 Mulai merender video untuk soal ke-{index}...")

    # 1. SIAPKAN AUDIO (Dari Tahap 3)
    audio_soal = AudioFileClip(os.path.join(audio_dir, f"soal_{index}.mp3"))
    audio_jawaban = AudioFileClip(os.path.join(audio_dir, f"jawaban_{index}.mp3"))

    # 2. BUAT BACKGROUND (Warna Solid)
    # Nanti kamu bisa ganti ColorClip ini dengan ImageClip atau VideoFileClip
    bg_clip = ColorClip(size=(WIDTH, HEIGHT), color=BG_COLOR)

    # 3. BUAT TEKS SOAL & PILIHAN
    # Format pilihan menjadi 1 string panjang dengan baris baru (Enter)
    abjad = ["A", "B", "C", "D"]
    teks_pilihan = "\n\n".join([f"{abjad[i]}. {opsi}" for i, opsi in enumerate(question_data['options'])])

    # TextClip menggunakan method='caption' agar teks otomatis turun ke bawah (wrap) jika kepanjangan
    # PERBAIKAN: Ganti 'Arial-Bold' menjadi 'DejaVu-Sans-Bold'
    txt_soal = TextClip(question_data['question'], fontsize=70, color=TEXT_COLOR, 
                        font='DejaVu-Sans-Bold', size=(WIDTH - 150, None), method='caption', align='center')
    
    # PERBAIKAN: Ganti 'Arial' menjadi 'DejaVu-Sans'
    txt_opsi = TextClip(teks_pilihan, fontsize=60, color=TEXT_COLOR, 
                        font='DejaVu-Sans', size=(WIDTH - 150, None), method='caption', align='West')

    # Atur posisi teks di layar (X, Y)
    txt_soal = txt_soal.set_position(('center', 400))
    txt_opsi = txt_opsi.set_position(('center', 800))

    # ==========================================
    # TIMELINE KLIP 1: PEMBACAAN SOAL
    # ==========================================
    # Tumpuk Background + Teks Soal + Teks Pilihan
    clip_1 = CompositeVideoClip([bg_clip, txt_soal, txt_opsi])
    clip_1 = clip_1.set_duration(audio_soal.duration).set_audio(audio_soal)

    # ==========================================
    # TIMELINE KLIP 2: TIMER (5 DETIK)
    # ==========================================
    timer_clips = []
    # Looping mundur 5, 4, 3, 2, 1
    for i in range(question_data['time_limit'], 0, -1):
        # PERBAIKAN: Ganti 'Arial-Bold' menjadi 'DejaVu-Sans-Bold'
        txt_angka = TextClip(str(i), fontsize=150, color='yellow', font='DejaVu-Sans-Bold')
        txt_angka = txt_angka.set_position(('center', 1400)).set_duration(1)
        
        # Tumpuk: BG + Soal + Pilihan + Angka Timer
        frame = CompositeVideoClip([bg_clip, txt_soal, txt_opsi, txt_angka]).set_duration(1)
        timer_clips.append(frame)
    
    clip_2 = concatenate_videoclips(timer_clips)

    # ==========================================
    # TIMELINE KLIP 3: PEMBACAAN JAWABAN
    # ==========================================
    teks_jawaban_benar = f"Jawaban:\n{question_data['correct_answer']}"
    
    # PERBAIKAN: Ganti 'Arial-Bold' menjadi 'DejaVu-Sans-Bold'
    txt_benar = TextClip(teks_jawaban_benar, fontsize=80, color=HIGHLIGHT_COLOR, 
                         font='DejaVu-Sans-Bold', size=(WIDTH - 150, None), method='caption', align='center')
    txt_benar = txt_benar.set_position(('center', 800))

    # PERBAIKAN: Ganti 'Arial-Italic' menjadi 'DejaVu-Sans' agar aman di Linux
    txt_fakta = TextClip(question_data['fun_fact'], fontsize=50, color='yellow', 
                         font='DejaVu-Sans', size=(WIDTH - 150, None), method='caption', align='center')
    txt_fakta = txt_fakta.set_position(('center', 1200))

    # Saat jawaban muncul, hilangkan pilihan A B C D, ganti dengan jawaban besar & fakta unik
    clip_3 = CompositeVideoClip([bg_clip, txt_soal, txt_benar, txt_fakta])
    clip_3 = clip_3.set_duration(audio_jawaban.duration).set_audio(audio_jawaban)

    # ==========================================
    # GABUNGKAN SEMUA & RENDER
    # ==========================================
    final_video = concatenate_videoclips([clip_1, clip_2, clip_3])
    
    output_filename = os.path.join(output_dir, f"video_soal_{index}.mp4")
    print("⏳ Sedang memproses dan menyimpan file MP4 (Ini butuh beberapa waktu)...")
    
    # fps=24 sudah cukup mulus untuk video teks, fps kecil membuat render lebih cepat
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video berhasil dirender: {output_filename}")


# ==========================================
# TEST RUN (UJI COBA SCRIPT)
# ==========================================
if __name__ == "__main__":
    # Data ini harus sama dengan data di Tahap 3 yang audionya sudah dibuat
    sample_question = {
        "question": "Negara manakah yang memiliki ibukota bernama Helsinki?",
        "options": ["Norwegia", "Swedia", "Finlandia", "Denmark"],
        "correct_answer": "Finlandia",
        "time_limit": 5,
        "fun_fact": "Helsinki memiliki julukan Kota Putih dari Utara karena banyak bangunan terbuat dari granit terang."
    }

    # Pastikan file soal_1.mp3 dan jawaban_1.mp3 ADA di folder assets_audio sebelum menjalankan ini
    create_quiz_video(sample_question, index=1)