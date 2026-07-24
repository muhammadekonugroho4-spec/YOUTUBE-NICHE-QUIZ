import asyncio
import edge_tts
import os

# ==========================================
# KONFIGURASI SUARA (Pilih Karakter Suara)
# ==========================================
# Opsi Suara Indonesia Neural:
# 1. "id-ID-GadisNeural" -> Suara perempuan ceria & natural
# 2. "id-ID-ArdiNeural" -> Suara laki-laki berwibawa
VOICE = "id-ID-GadisNeural"

async def generate_tts(text: str, output_filename: str):
    """
    Fungsi dasar untuk memanggil Edge-TTS dan menyimpan file MP3.
    """
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_filename)
    print(f"🎵 Tersimpan: {output_filename}")

async def process_quiz_audio(question_data: dict, index: int, output_dir: str = "assets_audio"):
    """
    Mengubah satu dict soal kuis menjadi 2 file MP3: 
    1. File pembacaan soal + pilihan
    2. File pembacaan jawaban + fun fact
    """
    # Buat folder penyimpanan jika belum ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ---------------------------------------------------------
    # BAGIAN 1: TEKS SOAL (Contoh: "Pertanyaan pertama... A, B, C...")
    # ---------------------------------------------------------
    soal_text = f"Pertanyaan ke {index}. {question_data['question']} "
    
    # Tambahkan abjad A, B, C, D di depan opsi jawaban
    abjad = ["A", "B", "C", "D"]
    for i, opsi in enumerate(question_data['options']):
        # Beri koma agar AI memberi jeda (pause) saat membaca
        soal_text += f"{abjad[i]}, {opsi}. "

    # ---------------------------------------------------------
    # BAGIAN 2: TEKS JAWABAN (Contoh: "Waktu habis! Jawabannya...")
    # ---------------------------------------------------------
    jawaban_text = f"Waktu habis! Jawabannya adalah, {question_data['correct_answer']}. {question_data['fun_fact']}"

    # Penamaan File
    file_soal = os.path.join(output_dir, f"soal_{index}.mp3")
    file_jawaban = os.path.join(output_dir, f"jawaban_{index}.mp3")

    print(f"⏳ Sedang memproses audio untuk soal ke-{index}...")
    
    # Eksekusi pembuatan suara
    await generate_tts(soal_text, file_soal)
    await generate_tts(jawaban_text, file_jawaban)

# ==========================================
# TEST RUN (UJI COBA SCRIPT)
# ==========================================
async def main():
    # Contoh data yang didapatkan dari Tahap 2 (Gemini API)
    sample_question = {
        "question": "Negara manakah yang memiliki ibukota bernama Helsinki?",
        "options": ["Norwegia", "Swedia", "Finlandia", "Denmark"],
        "correct_answer": "Finlandia",
        "time_limit": 5,
        "fun_fact": "Helsinki memiliki julukan Kota Putih dari Utara karena banyak bangunan terbuat dari granit terang."
    }

    print("Memulai Tahap 3: Text-to-Speech (TTS) Generation...\n")
    
    # Proses soal nomor 1
    await process_quiz_audio(sample_question, index=1)
    
    print("\n✅ Tahap 3 Selesai! Cek folder 'assets_audio' untuk melihat hasilnya.")

if __name__ == "__main__":
    # Menjalankan fungsi asynchronous di Python
    asyncio.run(main())