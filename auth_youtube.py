import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Hak akses untuk mengupload video YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def otorisasi():
    print("Membuka jalur login ke Google...")
    flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
    
    # Jalankan server lokal untuk menangkap respon login
    creds = flow.run_local_server(port=8080)
    
    # Simpan token permanen
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("✅ BERHASIL! File token.json telah dibuat. Sekarang aplikasi siap upload otomatis!")

if __name__ == "__main__":
    otorisasi()