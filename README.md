# Social Media Uploader - SIMPLIFIED VERSION

Script Python untuk mengupload video ke TikTok, Facebook, YouTube, Instagram secara otomatis dengan dukungan AI content generation dan video enhancement.

## 🚀 Fitur Utama

### 📱 **Platform Support**
- ✅ **TikTok** - Video upload dengan viral optimization
- ✅ **Facebook** - Status text, media posts, dan Reels
- ✅ **YouTube** - Shorts dengan API resmi
- ✅ **Instagram** - Reels dan Posts

### 🤖 **AI-Powered Features**
- ✅ **AI Content Generation** - Generate konten dengan Gemini AI
- ✅ **Smart Captions** - Caption otomatis untuk setiap platform
- ✅ **Trending Hashtags** - Hashtag yang relevan dan trending

### 🎬 **Video Features**
- ✅ **Video Download** - Download dari YouTube, TikTok, dll dengan yt-dlp
- ✅ **Video Enhancement** - Improve quality dengan FFmpeg
- ✅ **Platform Optimization** - Optimasi untuk setiap platform

## 📦 Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Chrome Browser
- **Windows**: Download dari https://www.google.com/chrome/
- **Linux**: `sudo apt install google-chrome-stable`
- **macOS**: `brew install --cask google-chrome`

### 3. Setup API Keys (Optional)
```bash
# Untuk AI features
set GEMINI_API_KEY=your_gemini_api_key

# Untuk YouTube API
# Download youtube_credentials.json dari Google Cloud Console
# Simpan di folder credentials/
```

### 4. Test Setup
```bash
python test_complete_system.py
```

## 🎯 Penggunaan

### **Interactive Mode (Recommended)**
```bash
python social_media_uploader.py
```

**Menu Options:**
```
🚀 SUPER ADVANCED SOCIAL MEDIA UPLOADER
======================================================================

📋 MENU UTAMA:
1. 🚀 Smart Upload Pipeline (Video/Text/Media)
2. 📊 System Status & Diagnostics  
3. 🧹 System Cleanup
4. ❌ Exit
```

### **Smart Upload Pipeline**
```
📹 PILIH JENIS KONTEN:
1. 🎬 Video Content (TikTok, Facebook Reels, YouTube Shorts, Instagram Reels)
2. 📝 Text Status (Facebook Status)
3. 🖼️ Image/Media (Facebook Post, Instagram Post)
```

## 📋 Examples

### **1. Video Upload ke Semua Platform**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 1 (Video Content)
Pilih: 1 (File video lokal) atau 2 (Download dari URL)
Pilih: 5 (Semua Platform)
```

### **2. Text Status dengan AI**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 2 (Text Status)
Pilih: 2 (Generate dengan AI)
Prompt: "motivasi untuk hari senin"
```

### **3. Image/Media Upload**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 3 (Image/Media)
Path: C:\Photos\image.jpg
Caption: "Amazing photo!"
Pilih: 3 (Kedua platform - Facebook & Instagram)
```

## 🔧 Troubleshooting

### **Chrome Issues**
```bash
# Fix Chrome detection
python fix_all_drivers.py

# Check Chrome version
google-chrome --version
```

### **ChromeDriver Issues**
```bash
# Auto-fix ChromeDriver
python fix_all_drivers.py

# Manual download
# Download dari https://chromedriver.chromium.org/
```

### **Login Issues**
```bash
# Clear cookies untuk login ulang
# Pilih menu: System Status & Diagnostics
# Browser akan terbuka untuk login manual
```

### **AI Issues**
```bash
# Set API key
set GEMINI_API_KEY=your_api_key

# Install AI package
pip install google-generativeai
```

## 📊 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10, Ubuntu 18.04+, macOS 10.14+
- **RAM**: 2GB
- **Storage**: 1GB free space
- **Browser**: Google Chrome
- **Python**: 3.8+

### **Recommended**
- **RAM**: 4GB+
- **Storage**: 5GB+ free space
- **Internet**: Stable connection

## 🎉 Success Tips

### **1. First Time Setup**
1. Install Chrome browser
2. Run `python test_complete_system.py`
3. Login manually pertama kali (cookies akan disimpan)
4. Set API keys untuk fitur AI

### **2. Upload Tips**
- Gunakan video format MP4 untuk compatibility terbaik
- File size < 100MB untuk upload yang stabil
- Caption yang engaging meningkatkan reach

### **3. AI Content Tips**
- Gunakan prompt dalam bahasa Indonesia
- Specific prompt = better results
- Experiment dengan berbagai style

## 📁 File Structure

```
social-media-uploader/
├── social_media_uploader.py      # Main script ⭐
├── tiktok_uploader.py            # TikTok uploader
├── facebook_uploader.py          # Facebook uploader
├── youtube_api_uploader.py       # YouTube API uploader
├── instagram_uploader.py         # Instagram uploader
├── video_downloader.py           # Video downloader (yt-dlp)
├── gemini_ai_assistant.py        # AI assistant
├── ffmpeg_video_editor.py        # Video editor
├── driver_manager.py             # Universal driver manager
├── fix_all_drivers.py            # Driver fix script
├── test_complete_system.py       # System test script
├── requirements.txt              # Dependencies
├── cookies/                      # Auto-created
├── credentials/                  # Auto-created
├── downloads/                    # Auto-created
├── edited_videos/                # Auto-created
└── screenshots/                  # Auto-created
```

## 🔒 Privacy & Security

- **Cookies**: Disimpan lokal untuk auto-login
- **API Keys**: Tidak disimpan di cloud
- **Videos**: Processed lokal, tidak diupload ke server lain
- **Safe**: Menggunakan browser automation yang aman

## ⚖️ Disclaimer

Script ini dibuat untuk tujuan edukasi dan otomasi personal. Pastikan mematuhi Terms of Service dari semua platform yang digunakan. Gunakan dengan bijak dan respect copyright.

---

**Ready to automate your social media? Let's go! 🚀**