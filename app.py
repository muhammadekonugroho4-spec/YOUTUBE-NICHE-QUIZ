import streamlit as st
import asyncio
import os
import json

from generator_ai import generate_quiz
from audio_generator import process_quiz_audio
from video_generator import create_quiz_video
from youtube_uploader import upload_video_to_youtube

# ==========================================
# MEMBANGKITKAN FILE RAHASIA DARI STREAMLIT SECRETS
# ==========================================
if "CLIENT_SECRETS" in st.secrets:
    with open("client_secrets.json", "w") as f:
        f.write(st.secrets["CLIENT_SECRETS"])

if "TOKEN_JSON" in st.secrets:
    with open("token.json", "w") as f:
        f.write(st.secrets["TOKEN_JSON"])

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(page_title="Auto Quiz Generator", page_icon="🎬", layout="centered")

st.title("🎬 AI Auto Shorts - Niche Quiz")
st.write("Dashboard ini berjalan 100% di cloud. Laptopmu aman dari beban berat!")

# Menyimpan data di memory (Session State)
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

# ==========================================
# PANEL KONTROL & INPUT (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    api_key = ""
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip() != "":
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("🔑 API Key terdeteksi otomatis!")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Masukkan API Key dari Google AI Studio")
    
    topik = st.text_input("Topik Kuis", placeholder="Contoh: Misteri Hewan Laut")
    jumlah_soal = st.slider("Jumlah Soal per Video", min_value=1, max_value=3, value=1)

# ==========================================
# LANGKAH 1: GENERATE NASKAH (AI)
# ==========================================
st.subheader("Langkah 1: Buat Naskah Kuis")

if st.button("🧠 Buat Naskah dengan Gemini", type="primary"):
    if not api_key:
        st.error("❌ API Key Gemini belum diisi!")
    elif not topik:
        st.warning("⚠️ Masukkan 'Topik Kuis' terlebih dahulu di sidebar.")
    else:
        st.toast("🚀 Menghubungi Gemini AI...", icon="🧠")
        
        with st.status("Sedang memproses naskah kuis...", expanded=True) as status:
            try:
                st.write("📡 Mengirimkan instruksi ke Google Gemini...")
                hasil = generate_quiz(topic=topik, num_questions=jumlah_soal, api_key=api_key)
                
                if hasil:
                    st.session_state.quiz_data = hasil
                    status.update(label="✅ Naskah kuis berhasil dibuat!", state="complete", expanded=False)
                    st.toast("Naskah Berhasil Dibuat!", icon="🎉")
                else:
                    status.update(label="❌ Gagal membuat naskah.", state="error")
                    st.error("Gemini mengembalikan respon kosong. Periksa topik atau API Key Anda.")
                    
            except Exception as e:
                status.update(label="❌ Terjadi Kesalahan!", state="error")
                st.error(f"Error Teknis: {str(e)}")

if st.session_state.quiz_data:
    st.success("📄 Naskah aktif tersedia. Siap untuk diproses ke Langkah 2.")
    with st.expander("👀 Lihat Detail Naskah (JSON)", expanded=True):
        st.json(st.session_state.quiz_data)

st.divider()

# ==========================================
# LANGKAH 2: GENERATE AUDIO & VIDEO (DIPERBAIKI)
# ==========================================
st.subheader("Langkah 2: Render Video")

if st.session_state.quiz_data:
    if st.button("🎥 Mulai Proses Render (Audio & Video)"):
        data = st.session_state.quiz_data
        
        # PERBAIKAN: Deteksi cerdas untuk mencari daftar soal
        # Mencegah KeyError jika AI memformatnya secara berbeda
        daftar_soal = []
        if isinstance(data, dict):
            # Mencari kunci 'questions', 'Questions', atau langsung pakai list jika ada
            daftar_soal = data.get('questions', data.get('Questions', []))
        elif isinstance(data, list):
            daftar_soal = data
            
        if not daftar_soal:
            st.error("❌ Format data naskah tidak dikenali atau kosong. Silakan klik ulang Langkah 1.")
        else:
            for idx, question in enumerate(daftar_soal, start=1):
                with st.status(f"Merender Video Soal Ke-{idx}...", expanded=True) as status_render:
                    try:
                        st.write("🔊 Membuat suara naskah (Voiceover Edge-TTS)...")
                        asyncio.run(process_quiz_audio(question, index=idx))
                        
                        st.write("🎬 Menggabungkan audio, teks, dan animasi timer (MoviePy)...")
                        create_quiz_video(question, index=idx)
                        
                        status_render.update(label=f"✅ Video Soal Ke-{idx} Selesai!", state="complete", expanded=False)
                        
                        video_path = f"output_videos/video_soal_{idx}.mp4"
                        if os.path.exists(video_path):
                            st.video(video_path)
                            
                    except Exception as e:
                        status_render.update(label=f"❌ Render Soal Ke-{idx} Gagal!", state="error")
                        st.error(f"Error saat merender video: {str(e)}")
else:
    st.info("💡 Selesaikan Langkah 1 terlebih dahulu untuk membuka fitur render video.")

st.divider()

# ==========================================
# LANGKAH 3: UPLOAD KE YOUTUBE
# ==========================================
st.subheader("Langkah 3: Upload ke YouTube")

if st.button("🚀 Upload Video ke YouTube"):
    if st.session_state.quiz_data:
        # Menghindari KeyError saat mencari topik untuk judul
        data = st.session_state.quiz_data
        topik_judul = data.get('topic', 'Kuis Viral') if isinstance(data, dict) else "Kuis Viral"
        
        video_path_upload = "output_videos/video_soal_1.mp4"
        
        if os.path.exists(video_path_upload):
            with st.status("Mengunggah video ke YouTube...", expanded=True) as status_upload:
                try:
                    judul_video = f"Kuis {topik_judul} Paling Susah! #shorts"
                    deskripsi_video = f"Bisakah kamu menjawab kuis tentang {topik_judul} ini? \n\n#quiz #shorts"
                    
                    st.write("📡 Mengirimkan file MP4 ke YouTube Data API...")
                    hasil_id = upload_video_to_youtube(video_path_upload, judul_video, deskripsi_video, ["quiz", "shorts"])
                    
                    if hasil_id:
                        status_upload.update(label="✅ Video Berhasil Diunggah!", state="complete", expanded=False)
                        st.success(f"Video tersimpan sebagai Private di YouTube Studio.")
                        st.write(f"🔗 **Link Video:** https://youtu.be/{hasil_id}")
                    else:
                        status_upload.update(label="❌ Upload Gagal!", state="error")
                except Exception as e:
                    status_upload.update(label="❌ Terjadi Kesalahan Upload!", state="error")
                    st.error(f"Error Teknis Upload: {str(e)}")
        else:
            st.error("File video tidak ditemukan. Silakan jalankan Langkah 2 terlebih dahulu.")
    else:
        st.error("Data kuis belum tersedia. Silakan jalankan Langkah 1 terlebih dahulu.")