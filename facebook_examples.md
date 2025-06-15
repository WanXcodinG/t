# Facebook Unified Uploader - Examples & Usage Guide

## 🚀 Facebook Unified Uploader Features

Facebook Uploader yang telah di-upgrade dengan fitur:
- ✅ **Text Status Only** - Post status text saja
- ✅ **Text + Media** - Post dengan gambar/video
- ✅ **AI Generated Content** - Generate konten dengan AI
- ✅ **Random AI Content** - AI generate konten random
- ✅ **Unified Interface** - Satu script untuk semua kebutuhan
- ✅ **Smart Prompting** - AI yang memahami context Indonesia

## 📋 Usage Examples

### **1. Interactive Mode (Recommended)**
```bash
python facebook_uploader.py
```

**Menu Options:**
```
📘 Facebook Unified Uploader
==================================================

Pilih jenis post:
1. 📝 Text Status Only
2. 🖼️ Text + Media (Image/Video)  
3. 🤖 AI Generated Status
4. 🎲 Random AI Content
5. 🍪 Check Cookies Status
6. 🗑️ Clear Cookies
7. ❌ Keluar
```

### **2. Command Line Usage**

#### **Text Status Only:**
```bash
# Simple text status
python facebook_uploader.py --content "Selamat pagi semua! Semoga hari ini penuh berkah 😊"

# Text status dengan type
python facebook_uploader.py --content "Tips produktivitas hari ini" --type status
```

#### **Text + Media:**
```bash
# Image dengan caption
python facebook_uploader.py --media "photo.jpg" --content "Pemandangan indah hari ini! 📸"

# Video dengan caption
python facebook_uploader.py --media "video.mp4" --content "Video menarik yang wajib ditonton! 🎬"

# Media dengan type
python facebook_uploader.py --media "image.png" --content "Amazing content!" --type media
```

#### **AI Generated Content:**
```bash
# AI generate status
python facebook_uploader.py --ai --prompt "motivasi untuk hari senin"

# AI dengan type specific
python facebook_uploader.py --ai --prompt "tips produktivitas kerja" --type status

# AI untuk media caption
python facebook_uploader.py --ai --prompt "caption untuk foto makanan" --type media
```

#### **Random AI Content:**
```bash
# Random AI content
python facebook_uploader.py --ai --type random

# Random dengan custom prompt
python facebook_uploader.py --ai --prompt "konten inspiratif" --type random
```

### **3. Advanced Options**

#### **Headless Mode:**
```bash
# Run tanpa browser window (untuk VPS)
python facebook_uploader.py --headless --content "Status dari VPS!"
```

#### **Debug Mode:**
```bash
# Enable debug logging
python facebook_uploader.py --debug --ai --prompt "test content"
```

#### **Cookie Management:**
```bash
# Check cookies status
python facebook_uploader.py --check-cookies

# Clear cookies
python facebook_uploader.py --clear-cookies
```

## 🤖 AI Prompt Examples

### **Motivational Content:**
```bash
python facebook_uploader.py --ai --prompt "motivasi untuk memulai hari senin"
python facebook_uploader.py --ai --prompt "quote inspiratif tentang kesuksesan"
python facebook_uploader.py --ai --prompt "semangat untuk menghadapi tantangan"
```

### **Tips & Advice:**
```bash
python facebook_uploader.py --ai --prompt "tips produktivitas untuk pekerja kantoran"
python facebook_uploader.py --ai --prompt "cara hidup sehat dan bahagia"
python facebook_uploader.py --ai --prompt "tips mengatur keuangan pribadi"
```

### **Lifestyle Content:**
```bash
python facebook_uploader.py --ai --prompt "review makanan enak di Jakarta"
python facebook_uploader.py --ai --prompt "pengalaman traveling ke Bali"
python facebook_uploader.py --ai --prompt "hobby fotografi untuk pemula"
```

### **Business Content:**
```bash
python facebook_uploader.py --ai --prompt "tips marketing untuk UMKM"
python facebook_uploader.py --ai --prompt "strategi bisnis online"
python facebook_uploader.py --ai --prompt "cara meningkatkan penjualan"
```

### **Educational Content:**
```bash
python facebook_uploader.py --ai --prompt "fakta menarik tentang teknologi"
python facebook_uploader.py --ai --prompt "tips belajar bahasa Inggris"
python facebook_uploader.py --ai --prompt "pengetahuan umum yang berguna"
```

## 📱 Interactive Mode Examples

### **1. Text Status Only:**
```
Pilihan: 1
Masukkan status text: Hari ini adalah hari yang indah untuk memulai sesuatu yang baru! 🌟

✅ Status berhasil dipost!
```

### **2. Text + Media:**
```
Pilihan: 2
Path ke file media: C:\Users\Photos\sunset.jpg
Caption untuk media: Sunset yang menakjubkan dari balkon rumah 🌅

✅ Post dengan media berhasil!
```

### **3. AI Generated Status:**
```
Pilihan: 3

Contoh prompt:
• motivasi untuk hari senin
• tips produktivitas kerja  
• cerita inspiratif tentang kesuksesan
• review makanan enak
• sharing pengalaman traveling

Masukkan prompt untuk AI: tips hidup sehat dan bahagia

✅ AI status berhasil dipost!

📋 AI Generated Content:
Title: Tips Hidup Sehat
Content: 💡 Tips: tips hidup sehat dan bahagia

Hal kecil yang bisa membuat perbedaan besar dalam hidup kita...
Hashtags: #tips, #lifehacks, #productivity, #lifestyle, #sharing
```

### **4. Random AI Content:**
```
Pilihan: 4
AI akan generate konten random yang menarik...
Generate random AI content? (Y/n): y

✅ Random AI content berhasil dipost!

📋 Generated Content:
Topic: motivasi untuk memulai hari
Title: Motivasi Hari Ini
Content: 🌟 motivasi untuk memulai hari

Setiap hari adalah kesempatan baru untuk menjadi versi terbaik...
```

## 🎯 AI Content Types

### **Status Type:**
- Optimized untuk text status Facebook
- Focus pada engagement dan shareability
- Include hashtag trending Indonesia
- Call-to-action yang natural

### **Media Type:**
- Optimized untuk caption media
- Visual storytelling approach
- Encourage interaction dengan media
- Hashtag yang relevan dengan visual

### **Random Type:**
- Konten spontan tapi berkualitas
- Topik yang dipilih secara random
- Surprise element untuk audience
- Variety content untuk feed

## 🔧 Configuration & Setup

### **Environment Variables:**
```bash
# Set Gemini API key untuk AI features
set GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Force headless mode
set HEADLESS=true
```

### **Dependencies:**
```bash
# Install required packages
pip install selenium webdriver-manager colorama google-generativeai

# Or install all requirements
pip install -r requirements.txt
```

### **Chrome Setup:**
```bash
# Auto-install Chrome (Ubuntu)
python driver_manager.py --install-chrome

# Fix all drivers
python fix_all_drivers.py

# Test setup
python test_facebook_unified.py
```

## 📊 Expected Output Examples

### **Successful Text Status:**
```
ℹ️ Setting up browser for Facebook...
✅ Browser ready for Facebook
ℹ️ Navigating to Facebook...
✅ Cookies loaded: 45/50
✅ Element found
ℹ️ Adding text content...
✅ Text content added
ℹ️ Looking for post button...
✅ Element found
✅ Post button clicked
✅ Facebook post created successfully!
ℹ️ Closing browser...
🎉 Facebook post berhasil!
```

### **Successful AI Generated Content:**
```
🤖 Generating AI content untuk: motivasi hari senin...
✅ AI content generated successfully
ℹ️ Setting up browser for Facebook...
✅ Browser ready for Facebook
✅ Text content added
✅ Facebook post created successfully!
🎉 Facebook post berhasil!
🤖 AI Content: Motivasi Hari Senin
```

### **Successful Media Post:**
```
ℹ️ Adding media to post...
✅ Element found
✅ Media uploaded successfully
✅ Text content added
✅ Post button clicked
✅ Facebook post created successfully!
🎉 Facebook post berhasil!
```

## 🚨 Troubleshooting

### **Common Issues:**

#### **1. ChromeDriver Error:**
```bash
# Fix driver issues
python fix_all_drivers.py

# Test driver
python driver_manager.py --test
```

#### **2. AI Not Working:**
```bash
# Check API key
echo %GEMINI_API_KEY%

# Set API key
set GEMINI_API_KEY=your_api_key

# Install AI package
pip install google-generativeai
```

#### **3. Login Required:**
```bash
# Clear cookies and login manually
python facebook_uploader.py --clear-cookies

# Then run normally - browser will open for manual login
python facebook_uploader.py
```

#### **4. Element Not Found:**
```bash
# Run with debug mode
python facebook_uploader.py --debug --content "test"

# Check screenshots in screenshots/ folder
```

### **VPS/Headless Issues:**
```bash
# Force headless mode
python facebook_uploader.py --headless --content "test from VPS"

# Check VPS setup
python driver_manager.py --diagnostics
```

## 🎉 Success Tips

### **1. Cookie Management:**
- Login manually pertama kali untuk save cookies
- Cookies akan auto-load untuk session berikutnya
- Clear cookies jika ada masalah login

### **2. AI Content:**
- Gunakan prompt dalam bahasa Indonesia
- Specific prompt menghasilkan content yang lebih baik
- Experiment dengan berbagai jenis prompt

### **3. Media Upload:**
- Gunakan format yang didukung: JPG, PNG, MP4, MOV
- File size tidak terlalu besar (< 100MB)
- Path file harus benar dan accessible

### **4. Reliability:**
- Gunakan headless mode untuk VPS
- Enable debug mode untuk troubleshooting
- Regular update ChromeDriver

Dengan Facebook Unified Uploader ini, posting ke Facebook menjadi **super flexible**, **AI-powered**, dan **fully automated**! 🚀📘✨