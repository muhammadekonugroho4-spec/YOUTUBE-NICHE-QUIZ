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
# 2. FUNGSI GENERATE (DENGAN AUTO-RETRY & AUTO-SAVE)
# ==========================================
def generate_drama_script(topic: str, num_scenes: int, api_key: str, max_retries: int = 3) -> dict:
    clean_api_key = api_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_api_key)
    
    prompt_text = f"""
    Kamu adalah penulis naskah profesional untuk Short Drama China (C-Drama Shorts).
    Buatkan alur cerita dengan topik: '{topic}'.
    Jumlah adegan: {num_scenes}.
    
    ATURAN:
    1. Konflik dramatis, cepat, bikin penasaran.
    2. Dialog WAJIB Bahasa Indonesia.
    3. visual_description WAJIB Bahasa Inggris (deskripsi karakter Asia, latar, ekspresi).
    """
    
    generation_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=ShortDramaStory
    )
    
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash-latest"]
    
    # SISTEM LOOPING: Mencoba berulang kali jika AI terpotong/gagal
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(models_to_try[0])
            response = model.generate_content(prompt_text, generation_config=generation_config)
            
            # Membersihkan teks
            clean_text = re.sub(r'```json\s*', '', response.text)
            clean_text = re.sub(r'```', '', clean_text).strip()
            
            # Jika berhasil dibaca, berarti tidak terpotong
            drama_data = json.loads(clean_text)
            
            # AUTO-SAVE: Menyimpan naskah ke file JSON agar aman
            with open("naskah_terakhir.json", "w", encoding="utf-8") as f:
                json.dump(drama_data, f, ensure_ascii=False, indent=4)
                
            return drama_data # Langsung kembalikan hasil jika sukses
            
        except json.JSONDecodeError:
            # Jika terpotong, diam-diam coba lagi tanpa memunculkan error ke web
            print(f"Percobaan {attempt + 1} gagal (Teks AI terpotong). Mengulang kembali...")
            time.sleep(2) # Jeda 2 detik sebelum mencoba lagi
            continue
        except Exception as e:
            print(f"Percobaan {attempt + 1} error: {str(e)}")
            time.sleep(2)
            continue
            
    # Jika sudah dicoba 3 kali dan masih gagal terus
    raise Exception("Sistem sudah mencoba 3 kali namun AI sedang sibuk/merespon terpotong. Silakan klik tombol buat naskah lagi.")