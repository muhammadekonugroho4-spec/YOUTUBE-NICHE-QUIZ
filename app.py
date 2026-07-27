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
    st.info("💡 Naskah siap! Langkah selanjutnya adalah mengolah dialog menjadi voiceover emosional Bahasa Indonesia dan merender video AI adegan karakter China.")
else:
    st.warning("Selesaikan Langkah 1 untuk membuat video.")