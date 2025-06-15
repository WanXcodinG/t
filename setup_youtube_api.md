# Setup YouTube Data API v3

## 🔧 Langkah-langkah Setup

### 1. Buat Project di Google Cloud Console

1. **Buka Google Cloud Console**
   - Kunjungi: https://console.cloud.google.com/
   - Login dengan akun Google Anda

2. **Buat Project Baru**
   - Klik "Select a project" di bagian atas
   - Klik "New Project"
   - Masukkan nama project (contoh: "YouTube Uploader")
   - Klik "Create"

### 2. Enable YouTube Data API v3

1. **Buka API Library**
   - Di sidebar kiri, pilih "APIs & Services" > "Library"
   - Atau kunjungi: https://console.cloud.google.com/apis/library

2. **Cari YouTube Data API**
   - Ketik "YouTube Data API v3" di search box
   - Klik pada "YouTube Data API v3"
   - Klik "Enable"

### 3. Buat OAuth 2.0 Credentials

1. **Buka Credentials**
   - Di sidebar kiri, pilih "APIs & Services" > "Credentials"
   - Atau kunjungi: https://console.cloud.google.com/apis/credentials

2. **Configure OAuth Consent Screen** (jika belum)
   - Klik "OAuth consent screen" di sidebar
   - Pilih "External" untuk user type
   - Isi informasi aplikasi:
     - App name: "YouTube Uploader"
     - User support email: email Anda
     - Developer contact: email Anda
   - Klik "Save and Continue"
   - Di "Scopes", klik "Add or Remove Scopes"
   - Cari dan tambahkan: `https://www.googleapis.com/auth/youtube.upload`
   - Klik "Save and Continue"
   - Di "Test users", tambahkan email Anda sebagai test user
   - Klik "Save and Continue"

3. **Buat OAuth 2.0 Client ID**
   - Kembali ke "Credentials"
   - Klik "Create Credentials" > "OAuth client ID"
   - Pilih "Desktop application"
   - Masukkan nama: "YouTube Uploader Desktop"
   - Klik "Create"

4. **Download Credentials**
   - Setelah dibuat, klik tombol download (ikon panah ke bawah)
   - Simpan file JSON yang didownload
   - Rename file menjadi `youtube_credentials.json`
   - Pindahkan ke folder `credentials/` di project ini

### 4. Struktur Folder

Pastikan struktur folder seperti ini:
```
project/
├── youtube_api_uploader.py
├── credentials/
│   └── youtube_credentials.json  ← File yang didownload dari Google Cloud
└── requirements.txt
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Test Upload

```bash
python youtube_api_uploader.py --video "test_video.mp4" --title "Test Upload"
```

## 🔐 Proses Autentikasi

### Pertama Kali
1. Jalankan script
2. Browser akan terbuka otomatis
3. Login dengan akun Google Anda
4. Klik "Allow" untuk memberikan permission
5. Token akan disimpan otomatis untuk penggunaan selanjutnya

### Selanjutnya
- Script akan menggunakan token yang tersimpan
- Tidak perlu login ulang kecuali token expired

## 📊 Quota dan Limits

### Daily Quota
- **Default**: 10,000 units per hari
- **Upload video**: 1,600 units per upload
- **Maksimal upload per hari**: ~6 video

### Request Quota
- Bisa request peningkatan quota di Google Cloud Console
- Untuk production use, pertimbangkan quota yang lebih tinggi

## 🔧 Troubleshooting

### Error: "The request cannot be completed because you have exceeded your quota"
- Quota harian habis
- Tunggu sampai reset (midnight Pacific Time)
- Atau request peningkatan quota

### Error: "Access blocked: This app's request is invalid"
- OAuth consent screen belum dikonfigurasi dengan benar
- Pastikan scope `youtube.upload` sudah ditambahkan
- Pastikan email Anda ada di test users

### Error: "invalid_client: Unauthorized"
- File credentials.json tidak valid
- Download ulang dari Google Cloud Console
- Pastikan project yang benar

### Error: "insufficient_scope"
- Scope tidak mencukupi
- Hapus token: `python youtube_api_uploader.py --clear-credentials`
- Autentikasi ulang dengan scope yang benar

## 🎯 Tips Penggunaan

### Optimasi untuk Shorts
- Gunakan video dengan aspek rasio 9:16 (vertical)
- Durasi maksimal 60 detik
- Tambahkan #Shorts di title atau description
- Script otomatis mendeteksi dan mengoptimasi untuk Shorts

### Best Practices
- Upload di jam-jam optimal (sesuai audience)
- Gunakan title yang menarik dan SEO-friendly
- Tambahkan description yang informatif
- Gunakan tags yang relevan

### Monitoring
- Cek quota usage di Google Cloud Console
- Monitor upload success rate
- Backup credentials file

## 🚀 Keunggulan YouTube API vs Selenium

### ✅ YouTube Data API v3
- **Reliable**: Tidak terpengaruh perubahan UI
- **Fast**: Upload langsung tanpa browser
- **Stable**: Tidak ada masalah verifikasi
- **Official**: Didukung resmi oleh Google
- **Scalable**: Bisa handle banyak upload

### ❌ Selenium (masalah yang dihindari)
- Verifikasi Google yang sering muncul
- Perubahan UI YouTube Studio
- Browser overhead
- Deteksi bot
- Tidak stabil untuk automation

Dengan YouTube Data API v3, upload menjadi lebih reliable dan professional! 🎉