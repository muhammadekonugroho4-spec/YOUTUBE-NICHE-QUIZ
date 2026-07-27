import os
import json
import re
import time
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
    character_speaking: str = Field(description="Nama/peran karakter yang berbicara.")

class ShortDramaStory(BaseModel):
    title: str = Field(description="Judul drama yang menarik.")
    genre: str = Field(description="Genre drama.")
    scenes: List[DramaScene] = Field(description="Daftar adegan drama.")

# ==========================================
# 2. FUNGSI GENERATE (DENGAN AUTO-SCAN MODEL)
# ==========================================
def generate_drama_script(topic: str, num_scenes: int, api_key: str, max_retries: int = 3) -> dict:
    clean_api_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_api_key)
    
    # ---------------------------------------------------------
    # FITUR BARU: RADAR PEMINDAI MODEL OTOMATIS DARI GOOGLE
    # ---------------------------------------------------------
    try:
        # Meminta Google memberikan daftar semua model yang aktif untuk API Key ini
        available_models = [
            m.name.replace("models/", "") 
            for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
    except Exception as e:
        raise Exception(f"Gagal memindai daftar model dari Google. Cek validitas API Key. Error: {str(e)}")

    if not available_models:
        raise Exception("API Key Anda valid, tetapi akun ini tidak memiliki akses ke model teks apapun.")

    # Mengurutkan daftar model agar memprioritaskan yang terbaru (gemini-1.5 / flash)
    models_to_try = sorted(available_models, key=lambda x: ("1.5" in x, "flash" in x), reverse=True)
    # ---------------------------------------------------------

    prompt_text = f"""
    Kamu adalah penulis naskah profesional untuk Short Drama China (C-Drama Shorts).
    Buatkan alur cerita dengan topik: '{topic}'.
    Jumlah adegan: {num_scenes}.
    
    ATURAN:
    1. Konflik dramatis, cepat, bikin penasaran.
    2. Dialog WAJIB Bahasa Indonesia.
    3. visual_description WAJIB Bahasa Inggris (deskripsi karakter Asia, latar, ekspresi).
    """
    
    # PERBAIKAN: Menghapus schema strict (response_schema) jika menggunakan model bebas
    # karena beberapa model Google yang didapat dari scan mungkin belum support strict schema.
    # Kita pancing manual lewat prompt agar formatnya tetap JSON.
    prompt_text += """
    
    PENTING: Kamu WAJIB merespon HANYA menggunakan format JSON valid persis seperti ini:
    {
      "title": "Judul Drama",
      "genre": "Genre",
      "scenes": [
        {
          "scene_number": 1,
          "visual_description": "English description...",
          "narration_dialogue": "Dialog bahasa Indonesia...",
          "character_speaking": "Nama Karakter"
        }
      ]
    }
    """

    generation_config = genai.GenerationConfig(
        response_mime_type="application/json"
    )
    
    last_error = ""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            
            for attempt in range(max_retries):
                try:
                    print(f"Mencoba AI model: {model_name} (Percobaan {attempt+1})")
                    response = model.generate_content(prompt_text, generation_config=generation_config)
                    
                    clean_text = re.sub(r'```json\s*', '', response.text)
                    clean_text = re.sub(r'```', '', clean_text).strip()
                    
                    drama_data = json.loads(clean_text)
                    
                    # SISIPKAN CATATAN: Model AI mana yang berhasil digunakan
                    drama_data["model_used"] = model_name
                    
                    # AUTO-SAVE
                    with open("naskah_terakhir.json", "w", encoding="utf-8") as f:
                        json.dump(drama_data, f, ensure_ascii=False, indent=4)
                        
                    return drama_data 
                    
                except json.JSONDecodeError:
                    last_error = f"[{model_name}] Teks AI terpotong."
                    time.sleep(2) 
                    continue
                except Exception as e:
                    error_msg = str(e)
                    last_error = f"[{model_name}] Error: {error_msg}"
                    
                    if "404" in error_msg or "not found" in error_msg.lower() or "not supported" in error_msg.lower():
                        break 
                        
                    time.sleep(2)
                    continue
                    
        except Exception as e:
            last_error = str(e)
            continue
            
    raise Exception(f"Gagal membuat naskah. Radar menemukan model ini: {available_models}. Tapi semuanya error. Detail Terakhir: {last_error}")