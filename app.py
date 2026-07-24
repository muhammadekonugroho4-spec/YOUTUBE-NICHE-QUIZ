import streamlit as st
import asyncio
import os
import json

# Mengambil fungsi dari file-file yang sudah kita buat sebelumnya
from generator_ai import generate_quiz
from audio_generator import process_quiz_audio
from video_generator import create_quiz_video
from youtube_uploader import upload_video_to_youtube # Import dipindah ke atas

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Auto Quiz Generator", page_icon="🎬", layout="centered")

st.title("🎬 AI Auto Shorts - Niche Quiz")
st.write("Dashboard ini berjalan 100% di cloud. Laptopmu aman dari beban berat!")

# Menyimpan data di memory (Session State) agar tidak hilang saat tombol ditekan
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

# ==========================================
# PANEL KONTROL & INPUT
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    # Cek apakah API Key sudah ada di Secrets Streamlit
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("🔑 API Key terdeteksi otomatis!")
    else:
        # Keamanan: Input API Key bertipe password agar tersembunyi
        api_key = st.text_input("Gemini API Key", type="password")
    
    topik = st.text_input("Topik Kuis", placeholder="Contoh: Misteri Hewan Laut")
    
    # Dibatasi 1-3 dulu agar server gratisan Streamlit tidak kehabisan RAM (1GB) saat render
    jumlah_soal = st.slider("Jumlah Soal per Video", min_value=1, max_value=3, value=1)

# ==========================================
# LANGKAH 1: GENERATE NASKAH (AI)
# ==========================================
st.subheader("Langkah 1: Buat Naskah Kuis")
if st.button("🧠 Buat Naskah dengan Gemini"):
    if not api_key or not topik:
        st.error("API Key dan Topik harus diisi!")
    else:
        with st.spinner("Gemini sedang berpikir..."):
            hasil = generate_quiz(topic=topik, num_questions=jumlah_soal, api_key=api_key)
            if hasil:
                st.session_state.quiz_data = hasil
                st.success("Naskah berhasil dibuat!")

# Menampilkan hasil naskah jika sudah ada
if st.session_state.quiz_data:
    with st.expander("👀 Lihat Detail Naskah (JSON)", expanded=True):
        st.json(st.session_state.quiz_data)

# ==========================================
# LANGKAH 2: GENERATE AUDIO & VIDEO
# ==========================================
st.subheader("Langkah 2: Render Video")
if st.session_state.quiz_data:
    if st.button("🎥 Mulai Proses Render (Audio & Video)"):
        data = st.session_state.quiz_data
        
        # Loop sebanyak jumlah soal yang dihasilkan
        for idx, question in enumerate(data['questions'], start=1):
            st.write(f"⏳ Memproses Soal ke-{idx}...")
            
            # 1. Generate Audio (Menggunakan asyncio karena fungsi edge-tts bersifat async)
            with st.spinner("Membuat suara (Voiceover)..."):
                asyncio.run(process_quiz_audio(question, index=idx))
            
            # 2. Render Video (Proses paling berat)
            with st.spinner("Merender video dengan ImageMagick & MoviePy (Tunggu sebentar)..."):
                create_quiz_video(question, index=idx)
                
            st.success(f"✅ Video soal ke-{idx} selesai!")
            
            # 3. Tampilkan Video di Browser
            video_path = f"output_videos/video_soal_{idx}.mp4"
            if os.path.exists(video_path):
                st.video(video_path)

else:
    st.info("Selesaikan Langkah 1 terlebih dahulu untuk bisa merender video.")

# ==========================================
# LANGKAH 3: UPLOAD KE YOUTUBE
# ==========================================
st.subheader("Langkah 3: Upload ke YouTube")
if st.button("🚀 Upload Video ke YouTube"):
    # Kita ambil data soal pertama sebagai judul (kamu bisa kustomisasi ini nanti)
    if st.session_state.quiz_data:
        topik_judul = st.session_state.quiz_data['topic']
        video_path_upload = "output_videos/video_soal_1.mp4"
        
        if os.path.exists(video_path_upload):
            with st.spinner("Sedang mengunggah ke YouTube..."):
                judul_video = f"Kuis {topik_judul} Paling Susah! #shorts"
                deskripsi_video = f"Bisakah kamu menjawab kuis tentang {topik_judul} ini? \n\n#quiz #shorts"
                
                # Eksekusi fungsi upload
                hasil_id = upload_video_to_youtube(video_path_upload, judul_video, deskripsi_video, ["quiz", "shorts"])
                
                if hasil_id:
                    st.success(f"Berhasil! Buka YouTube Studio untuk mengubah statusnya menjadi Public.")
                    st.write(f"Link Video: https://youtu.be/{hasil_id}")
        else:
            st.error("Video belum dirender. Jalankan Langkah 2 terlebih dahulu.")
    else:
         st.error("Data kuis belum ada. Silakan jalankan Langkah 1 terlebih dahulu.")