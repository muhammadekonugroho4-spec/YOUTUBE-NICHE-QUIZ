import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. BAWA SKEMA DARI TAHAP 1
# ==========================================
class QuizQuestion(BaseModel):
    question: str = Field(description="Teks pertanyaan kuis.")
    options: List[str] = Field(description="Daftar 3 atau 4 pilihan jawaban.")
    correct_answer: str = Field(description="Jawaban yang benar dari pilihan.")
    time_limit: int = Field(default=5, description="Waktu hitung mundur.")
    fun_fact: str = Field(description="Fakta unik 1 kalimat tentang jawaban benar.")
    visual_prompt: str = Field(description="Ide gambar latar belakang.")

class QuizBatch(BaseModel):
    topic: str = Field(description="Topik utama dari kuis.")
    language: str = Field(default="id")
    questions: List[QuizQuestion] = Field(description="Daftar pertanyaan.")

# ==========================================
# 2. FUNGSI UTAMA MEMANGGIL GEMINI
# ==========================================
def generate_quiz(topic: str, num_questions: int, api_key: str) -> dict:
    """
    Meminta Gemini membuat kuis dan memaksanya mematuhi format JSON.
    """
    # PERBAIKAN 1: Bersihkan API Key dari spasi atau tanda kutip tersembunyi
    clean_api_key = api_key.strip().replace('"', '').replace("'", "")
    
    # Konfigurasi API Key
    genai.configure(api_key=clean_api_key)
    
    # Gunakan Gemini 1.5 Flash (Sangat cepat dan gratis untuk penggunaan wajar)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Prompt (Perintah ke AI)
    prompt_text = f"""
    Kamu adalah seorang pembuat konten YouTube Shorts yang viral.
    Buatkan kuis tebak-tebakan tentang topik: '{topic}'.
    Jumlah pertanyaan: {num_questions}.
    Gunakan bahasa Indonesia yang santai, asik, dan kekinian.
    Pastikan tingkat kesulitannya bervariasi agar penonton penasaran.
    """
    
    print("🤖 Sedang meminta Gemini membuat kuis, mohon tunggu...")
    
    # PERBAIKAN 2: Tidak menggunakan try-except kosong agar app.py bisa 
    # menangkap dan menampilkan pesan error asli dari server Google.
    response = model.generate_content(
        prompt_text,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=QuizBatch
        )
    )
    
    # PERBAIKAN 3: Cek jika respon diblokir oleh Safety Filter
    if not response.text:
        raise Exception("Respon AI kosong. Kemungkinan topik kuis diblokir oleh Safety Filter Google.")
        
    # Ubah string JSON dari AI menjadi Python Dictionary
    quiz_data = json.loads(response.text)
    return quiz_data

# ==========================================
# 3. TEST RUN (UJI COBA SCRIPT LOKAL)
# ==========================================
if __name__ == "__main__":
    # Ganti dengan API Key milikmu sendiri saat tes lokal
    MY_API_KEY = "MASUKKAN_API_KEY_GEMINI_DI_SINI"
    
    TOPIK = "Misteri Hewan Laut Dalam"
    JUMLAH_SOAL = 3
    
    try:
        hasil_kuis = generate_quiz(topic=TOPIK, num_questions=JUMLAH_SOAL, api_key=MY_API_KEY)
        print("✅ Berhasil! Berikut hasil naskah kuis dari Gemini:\n")
        print(json.dumps(hasil_kuis, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ GAGAL: {str(e)}")