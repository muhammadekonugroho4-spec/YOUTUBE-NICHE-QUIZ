import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Tentukan izin akses (hanya untuk upload video)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """
    Fungsi ini akan membuka tab browser untuk login akun Google.
    Setelah login berhasil, ia akan menyimpan file 'token.json' 
    agar kamu tidak perlu login ulang untuk upload selanjutnya.
    """
    credentials = None
    
    # Cek apakah kita sudah pernah login dan punya token
    import google.oauth2.credentials
    if os.path.exists("token.json"):
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # Jika belum ada token, mulai proses login
    if not credentials or not credentials.valid:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", SCOPES
        )
        # Codespaces butuh pengaturan port agar login browser bisa diteruskan
        credentials = flow.run_local_server(port=8080)
        
        # Simpan token untuk pemakaian selanjutnya
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list):
    """
    Mengeksekusi proses unggah video ke channel YouTube.
    """
    youtube = get_authenticated_service()

    print(f"🚀 Memulai upload video: {title}...")

    # Struktur metadata video (Judul, deskripsi, dll)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22", # Kategori 22 = People & Blogs, 24 = Entertainment
        },
        "status": {
            "privacyStatus": "private", # Wajib private jika aplikasi belum diaudit Google
            "selfDeclaredMadeForKids": False
        }
    }

    # Menyiapkan file media mp4
    media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")

    # Membuat antrean permintaan (request)
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    try:
        response = request.execute()
        print(f"✅ Upload Sukses! Video ID: {response['id']}")
        return response['id']
    except googleapiclient.errors.HttpError as e:
        print(f"❌ Terjadi kesalahan saat upload: {e}")
        return None

# ==========================================
# TEST RUN LOKAL
# ==========================================
if __name__ == "__main__":
    # Pastikan file video_soal_1.mp4 ada dan file client_secrets.json sudah dimasukkan
    if os.path.exists("output_videos/video_soal_1.mp4"):
        upload_video_to_youtube(
            video_path="output_videos/video_soal_1.mp4",
            title="Tebak Ibukota Negara Ini! #shorts #quiz",
            description="Seberapa pintar kamu menebak ibukota negara ini? Tulis jawabanmu di kolom komentar! \n\n#quiz #tebaktebakan #pengetahuanumum",
            tags=["quiz", "tebak tebakan", "pengetahuan", "shorts"]
        )
    else:
        print("File video tidak ditemukan!")