import streamlit as st
import json
import os
from generator_ai import generate_drama_script

# Konfigurasi Halaman
st.set_page_config(page_title="AI Chinese Drama Shorts Generator", page_icon="🎭", layout="centered")

st.title("🎭 AI Short Drama China Generator")
st.write("Buat naskah & alur drama pendek bergaya Short Drama China dengan mudah!")

if "drama_data" not in st.session_state:
    st.session_state.drama_data = None

# Sidebar
with st.sidebar:
    st.header("⚙️ Pengaturan Naskah")
    
    api_key = ""
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"].strip() != "":
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("🔑 API Key Terdeteksi!")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
    
    topik = st.text_input("Topik / Ide Cerita Drama", placeholder="Contoh: Istri yang diremehkan ternyata pewaris kaya")
    jumlah_scene = st.slider("Jumlah Adegan (Scene)", min_value=3, max_value=6, value=4)

# ==========================================
# LANGKAH 1: GENERATE ALUR DRAMA
# ==========================================
st.subheader("Langkah 1: Buat Alur Drama & Dialog")

if st.button("🎬 Buat Naskah Drama dengan AI", type="primary"):
    if not api_key:
        st.error("❌ Masukkan API Key terlebih dahulu!")
    elif not topik:
        st.warning("⚠️ Masukkan ide cerita drama di sidebar.")
    else:
        st.toast("🚀 Merancang alur drama...", icon="🎭")
        with st.status("Sedang membuat naskah drama emosional...", expanded=True) as status:
            try:
                hasil = generate_drama_script(topic=topik, num_scenes=jumlah_scene, api_key=api_key)
                if hasil:
                    st.session_state.drama_data = hasil
                    status.update(label="✅ Naskah Drama Berhasil Dibuat!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="❌ Kesalahan!", state="error")
                st.error(f"Error: {str(e)}")

# Tampilkan Hasil Naskah
if st.session_state.drama_data:
    data = st.session_state.drama_data
    
    # MENAMPILKAN CATATAN AI YANG BERHASIL
    if "model_used" in data:
        st.info(f"🤖 Naskah ini sukses dibuat menggunakan model AI: **{data['model_used']}**")
        
    st.success(f"📌 Judul Drama: **{data.get('title', 'Tanpa Judul')}** ({data.get('genre', 'Drama')})")
    
    st.write("---")
    for scene in data.get("scenes", []):
        with st.container():
            st.markdown(f"### 🎬 Scene {scene['scene_number']}")
            st.markdown(f"**🗣️ Dialog ({scene['character_speaking']}):** *\"{scene['narration_dialogue']}\"*")
            st.info(f"🎨 **Deskripsi Visual AI Video:** {scene['visual_description']}")
            st.write("---")

# ==========================================
# LANGKAH 2: PEMBUATAN VIDEO AI
# ==========================================
st.subheader("Langkah 2: Generate Video & Suara")
if st.session_state.drama_data:
    st.info("💡 Naskah siap! Silakan klik tombol di bawah untuk membuat video.")
    
    if st.button("🎬 Render Video Drama Sekarang", type="primary"):
        with st.status("Memproses Video Drama...", expanded=True) as status:
            try:
                from audio_generator import generate_drama_audio
                from video_generator import create_drama_video
                
                st.write("🔊 1. Mengisi Suara Karakter (Voiceover)...")
                generate_drama_audio(st.session_state.drama_data)
                
                st.write("🎞️ 2. Merender Video (Ini butuh waktu beberapa menit, jangan ditutup)...")
                output_file = create_drama_video(st.session_state.drama_data)
                
                status.update(label="✅ Video Berhasil Dibuat!", state="complete")
                
                # Menampilkan Video di Layar Web
                st.success("Yeay! Videomu sudah siap ditonton:")
                st.video(output_file)
                
                # Memunculkan Tombol Download
                with open(output_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Video ke Komputer/HP",
                        data=file,
                        file_name="Drama_China_Shorts.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                status.update(label="❌ Render Gagal", state="error")
                st.error(f"Error: {str(e)}")
else:
    st.warning("Selesaikan Langkah 1 untuk membuka kunci fitur video.")