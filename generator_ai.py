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
    # Konfigurasi API Key
    genai.configure(api_key=api_key)
    
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
    
    try:
        # Kita paksa output AI menjadi JSON menggunakan response_schema
        response = model.generate_content(
            prompt_text,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=QuizBatch
            )
        )
        
        # Ubah string JSON dari AI menjadi Python Dictionary
        quiz_data = json.loads(response.text)
        return quiz_data
        
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat menghubungi API: {e}")
        return None

# ==========================================
# 3. TEST RUN (UJI COBA SCRIPT)
# ==========================================
if __name__ == "__main__":
    # Ganti dengan API Key milikmu sendiri
    MY_API_KEY = "MASUKKAN_API_KEY_GEMINI_DI_SINI"
    
    # Kita tes membuat 3 soal tentang Misteri Laut Dalam
    TOPIK = "Misteri Hewan Laut Dalam"
    JUMLAH_SOAL = 3
    
    hasil_kuis = generate_quiz(topic=TOPIK, num_questions=JUMLAH_SOAL, api_key=MY_API_KEY)
    
    if hasil_kuis:
        print("✅ Berhasil! Berikut hasil naskah kuis dari Gemini:\n")
        # Print hasil dalam bentuk JSON yang rapi
        print(json.dumps(hasil_kuis, indent=2, ensure_ascii=False))