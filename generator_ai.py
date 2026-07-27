import os
import json
import re
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# ==========================================
# 1. SKEMA DATA DRAMA SHORTS
# ==========================================
class DramaScene(BaseModel):
    scene_number: int = Field(description="Nomor adegan (1, 2, 3, dst).")
    visual_description: str = Field(description="Deskripsi visual adegan dalam bahasa Inggris (karakter berwajah Asia/China, ekspresi, suasana).")
    narration_dialogue: str = Field(description="Dialog atau narasi bahasa Indonesia yang dramatis dan emosional.")
    character_speaking: str = Field(description="Nama/peran karakter yang berbicara (misal: 'Pria Kaya', 'Wanita Protagonis', 'Narator').")

class ShortDramaStory(BaseModel):
    title: str = Field(description="Judul drama yang menarik dan penasaran.")
    genre: str = Field(description="Genre drama (misal: Balas Dendam, CEO Kaya, Pengkhianatan).")
    scenes: List[DramaScene] = Field(description="Daftar adegan drama.")

# ==========================================
# 2. FUNGSI UTAMA MEMANGGIL GEMINI
# ==========================================
def generate_drama_script(topic: str, num_scenes: int, api_key: str) -> dict:
    clean_api_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_api_key)
    
    prompt_text = f"""
    Kamu adalah penulis naskah profesional untuk Short Drama China (C-Drama Shorts) yang viral di TikTok dan Shorts.
    Buatkan alur cerita drama pendek dengan tema/topik: '{topic}'.
    Jumlah adegan/scene: {num_scenes}.
    
    ATURAN PENULISAN:
    1. Cerita harus memiliki konflik yang cepat, dramatis, dan bikin penasaran (gaya Short Drama China).
    2. Dialog/Narasi WAJIB menggunakan BAHASA INDONESIA yang emosional dan mudah dipahami penonton Indonesia.
    3. 'visual_description' WAJIB dalam BAHASA INGGRIS, mendeskripsikan penampilan fisik karakter Tionghoa/China modern, ekspresi wajah, dan latar tempat.
    
    PENTING: Jawab HANYA menggunakan format JSON yang valid sesuai skema.
    """
    
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=ShortDramaStory
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
        raise Exception(f"Gagal menghubungi server AI. Error: {last_error}")

    raw_text = response.text
    clean_text = re.sub(r'```json\s*', '', raw_text)
    clean_text = re.sub(r'```', '', clean_text)
    clean_text = clean_text.strip()
    
    try:
        drama_data = json.loads(clean_text)
    except json.JSONDecodeError:
        raise Exception("AI memberikan jawaban yang terpotong. Silakan klik tombol buat naskah lagi.")
    
    return drama_data