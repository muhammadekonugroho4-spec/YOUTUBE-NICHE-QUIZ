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