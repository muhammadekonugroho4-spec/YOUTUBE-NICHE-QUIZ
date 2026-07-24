import os
import json
import re
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. SKEMA DATA
# ==========================================
class QuizQuestion(BaseModel):
    question: str = Field(description="Teks pertanyaan kuis.")
    options: List[str] = Field(description="Daftar 3 atau 4 pilihan jawaban.")
    correct_answer: str = Field(description="Jawaban yang benar dari pilihan.")
    time_limit: int = Field(description="Waktu hitung mundur (selalu isi dengan angka 5).")
    fun_fact: str = Field(description="Fakta unik 1 kalimat tentang jawaban benar.")
    visual_prompt: str = Field(description="Ide gambar latar belakang.")

class QuizBatch(BaseModel):
    topic: str = Field(description="Topik utama dari kuis.")
    language: str = Field(description="Kode bahasa (selalu isi dengan teks 'id').")
    questions: List[QuizQuestion] = Field(description="Daftar pertanyaan.")

# ==========================================
# 2. FUNGSI UTAMA MEMANGGIL GEMINI
# ==========================================
def generate_quiz(topic: str, num_questions: int, api_key: str) -> dict:
    """
    Meminta Gemini membuat kuis dan menangani error JSON yang terpotong.
    """
    clean_api_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_api_key)
    
    prompt_text = f"""
    Kamu adalah seorang pembuat konten YouTube Shorts.
    Buatkan kuis tebak-tebakan tentang topik: '{topic}'.
    Jumlah pertanyaan: {num_questions}.
    Gunakan bahasa Indonesia yang santai.
    
    PENTING: Kamu WAJIB merespon HANYA menggunakan format JSON dengan struktur persis seperti ini:
    {{
      "topic": "{topic}",
      "language": "id",
      "questions": [
        {{
          "question": "pertanyaan disini",
          "options": ["pilihan1", "pilihan2", "pilihan3"],
          "correct_answer": "jawaban yang benar",
          "time_limit": 5,
          "fun_fact": "fakta unik",
          "visual_prompt": "deskripsi gambar"
        }}
      ]
    }}
    """
    
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=QuizBatch
    )
    
    models_to_try = [
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]
    
    response = None
    last_error = ""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt_text,
                generation_config=generation_config
            )
            break  
        except Exception as e:
            last_error = str(e)
            continue
    
    if response is None or not response.text:
        raise Exception(f"Semua versi model Gemini ditolak oleh server. Error terakhir: {last_error}")

    # PERBAIKAN: Membersihkan teks dari blok markdown (```json ... ```)
    raw_text = response.text
    clean_text = re.sub(r'```json\s*', '', raw_text)
    clean_text = re.sub(r'```', '', clean_text)
    clean_text = clean_text.strip()
    
    try:
        # Mencoba membaca string JSON yang sudah dibersihkan
        quiz_data = json.loads(clean_text)
    except json.JSONDecodeError:
        # Menangkap error 'Unterminated string'
        raise Exception("AI memberikan jawaban yang terpotong (Gagal membaca JSON). Jangan panik, cukup klik tombol 'Buat Naskah' sekali lagi.")
    
    if "questions" not in quiz_data or len(quiz_data["questions"]) == 0:
         raise Exception("AI gagal membuat daftar soal. Silakan klik tombol 'Buat Naskah' sekali lagi.")
         
    return quiz_data

# ==========================================
# 3. TEST RUN LOKAL
# ==========================================
if __name__ == "__main__":
    MY_API_KEY = "MASUKKAN_API_KEY_GEMINI_DI_SINI"
    TOPIK = "Misteri Hewan Laut Dalam"
    JUMLAH_SOAL = 3
    
    try:
        hasil_kuis = generate_quiz(topic=TOPIK, num_questions=JUMLAH_SOAL, api_key=MY_API_KEY)
        print("✅ Berhasil! Berikut hasil naskah kuis dari Gemini:\n")
        print(json.dumps(hasil_kuis, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ GAGAL: {str(e)}")