import os
import asyncio
import edge_tts

async def generate_audio_async(text, filename, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

def generate_drama_audio(drama_data, output_dir="assets_audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("🔊 Memulai proses Voiceover (Edge-TTS)...")
    
    scenes = drama_data.get("scenes", [])
    for i, scene in enumerate(scenes):
        dialogue = scene.get("narration_dialogue", "")
        character = scene.get("character_speaking", "").lower()
        
        # Logika otomatis Laki-laki / Perempuan berdasarkan nama karakter
        voice = "id-ID-GadisNeural" # Default suara cewek
        kata_kunci_cowok = ['pria', 'suami', 'ayah', 'bos', 'kakek', 'laki', 'boy', 'man']
        if any(word in character for word in kata_kunci_cowok):
            voice = "id-ID-ArdiNeural" # Ubah ke suara cowok

        filename = os.path.join(output_dir, f"scene_{i+1}.mp3")
        asyncio.run(generate_audio_async(dialogue, filename, voice))
        print(f"✅ Audio scene {i+1} selesai: {filename}")