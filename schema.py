from pydantic import BaseModel, Field
from typing import List

# ==========================================
# TAHAP 1: DEFINISI STRUKTUR DATA (SCHEMA)
# ==========================================

class QuizQuestion(BaseModel):
    """
    Schema untuk satu pertanyaan kuis.
    Ini adalah cetak biru yang akan dipatuhi oleh Gemini AI.
    """
    question: str = Field(
        ..., 
        description="Teks pertanyaan kuis yang menarik dan memancing rasa penasaran."
    )
    options: List[str] = Field(
        ..., 
        description="Daftar 3 atau 4 pilihan jawaban.",
        min_length=2,
        max_length=4
    )
    correct_answer: str = Field(
        ..., 
        description="Jawaban yang benar. Harus sama persis dengan salah satu teks di 'options'."
    )
    time_limit: int = Field(
        default=5, 
        description="Waktu hitung mundur dalam detik (standar YouTube Shorts adalah 5-7 detik)."
    )
    fun_fact: str = Field(
        ..., 
        description="Fakta unik 1 kalimat tentang jawaban yang benar. Berguna untuk menahan penonton di akhir video."
    )
    visual_prompt: str = Field(
        ..., 
        description="Ide atau deskripsi gambar latar belakang (background) yang cocok untuk soal ini. (Contoh: 'Pemandangan kota Tokyo malam hari')."
    )

class QuizBatch(BaseModel):
    """
    Schema untuk satu set/batch kuis dalam satu video (misal: 1 video Shorts berisi 3-5 pertanyaan).
    """
    topic: str = Field(
        ..., 
        description="Topik utama dari kuis ini."
    )
    language: str = Field(
        default="id", 
        description="Kode bahasa yang digunakan (contoh: 'id' untuk Indonesia)."
    )
    questions: List[QuizQuestion] = Field(
        ..., 
        description="Daftar pertanyaan dalam satu video."
    )

# ==========================================
# CONTOH PENGGUNAAN (TESTING LOKAL)
# ==========================================
if __name__ == "__main__":
    # Mensimulasikan data yang nanti akan dihasilkan oleh Gemini AI
    sample_data = {
        "topic": "Ibukota Negara di Dunia",
        "language": "id",
        "questions": [
            {
                "question": "Negara manakah yang memiliki ibukota bernama Helsinki?",
                "options": ["Norwegia", "Swedia", "Finlandia", "Denmark"],
                "correct_answer": "Finlandia",
                "time_limit": 5,
                "fun_fact": "Helsinki memiliki julukan 'Kota Putih dari Utara' karena banyak bangunan terbuat dari granit terang.",
                "visual_prompt": "Landmark kota Helsinki bersalju dengan langit biru."
            }
        ]
    }

    # Memasukkan data mentah ke dalam schema untuk divalidasi
    try:
        quiz_video = QuizBatch(**sample_data)
        print("✅ Data Schema Berhasil Dibuat dan Divalidasi!\n")
        
        # Output format JSON yang rapi (Siap dilempar ke mesin pembuat video)
        print(quiz_video.model_dump_json(indent=2))
        
    except Exception as e:
        print("❌ Terjadi kesalahan validasi data:")
        print(e)