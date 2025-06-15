# Social Media Uploader - ENHANCED WITH GEMINI 2.0-FLASH

Script Python untuk mengupload video ke TikTok, Facebook, YouTube, Instagram secara otomatis dengan dukungan **Gemini 2.0-flash AI** (model terbaru dan tercanggih) untuk content generation dan video enhancement.

## 🚀 Fitur Utama

### 📱 **Platform Support**
- ✅ **TikTok** - Video upload dengan viral optimization
- ✅ **Facebook** - Status text, media posts, dan Reels
- ✅ **YouTube** - Shorts dengan API resmi
- ✅ **Instagram** - Reels dan Posts

### 🤖 **AI-Powered Features (Gemini 2.0-flash)**
- ✅ **Advanced AI Content Generation** - Powered by latest Gemini 2.0-flash
- ✅ **Superior Video Analysis** - Multi-modal understanding
- ✅ **Viral Prediction Engine** - AI-powered viral score prediction
- ✅ **Smart Platform Optimization** - Algorithm-aware content adaptation
- ✅ **Trend Integration** - Real-time trending element detection
- ✅ **Enhanced Hook Creation** - Psychological trigger-based hooks

### 🎬 **Video Features**
- ✅ **Video Download** - Download dari YouTube, TikTok, dll dengan yt-dlp
- ✅ **Video Enhancement** - Improve quality dengan FFmpeg
- ✅ **Platform Optimization** - Optimasi untuk setiap platform
- ✅ **Anti-Detection** - Advanced modifications untuk avoid detection

## 📦 Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Chrome Browser
- **Windows**: Download dari https://www.google.com/chrome/
- **Linux**: `sudo apt install google-chrome-stable`
- **macOS**: `brew install --cask google-chrome`

### 3. Setup Gemini 2.0-flash API (Recommended)
```bash
# Buat file .env
echo "GEMINI_API_KEY=your_gemini_api_key" > .env

# Get API key dari: https://makersuite.google.com/app/apikey
```

### 4. Setup YouTube API (Optional)
```bash
# Download youtube_credentials.json dari Google Cloud Console
# Simpan di folder credentials/
```

### 5. Test Setup
```bash
python test_complete_system.py
```

## 🎯 Penggunaan

### **Interactive Mode (Recommended)**
```bash
python social_media_uploader.py
```

**Enhanced Menu dengan Gemini 2.0-flash:**
```
🚀 SUPER ADVANCED SOCIAL MEDIA UPLOADER
======================================================================
🎯 Powered by Gemini 2.0-flash (Latest & Most Advanced AI)

📋 MENU UTAMA:
1. 🚀 Smart Upload Pipeline (Video/Text/Media) - AI Enhanced
2. 📊 System Status & Diagnostics  
3. 🧹 System Cleanup
4. ❌ Exit
```

### **Smart Upload Pipeline dengan AI**
```
📹 PILIH JENIS KONTEN:
1. 🎬 Video Content (AI-Enhanced Analysis & Optimization)
2. 📝 Text Status (AI-Generated dengan Gemini 2.0-flash)
3. 🖼️ Image/Media (AI-Powered Captions)
```

## 📋 Examples dengan Gemini 2.0-flash

### **1. AI-Enhanced Video Upload**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 1 (Video Content)
Pilih: 1 (File video lokal) atau 2 (Download dari URL)
Pilih: 1 (Generate AI content dengan Gemini 2.0-flash)
Language: English/Indonesian
Pilih: 5 (Semua Platform)

AI akan:
✅ Analyze video dengan advanced multi-modal understanding
✅ Generate viral-optimized content untuk setiap platform
✅ Predict viral potential dan engagement score
✅ Create platform-specific hooks dan descriptions
✅ Suggest optimal hashtags dan posting strategy
```

### **2. Advanced AI Text Status**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 2 (Text Status)
Pilih: 2 (Generate dengan Gemini 2.0-flash)
Prompt: "motivasi untuk entrepreneur muda"
Language: Indonesian

AI akan generate:
✅ Multiple content variations (viral hook, storytelling, educational)
✅ Advanced hashtag strategy (trending, niche, engagement)
✅ Optimal call-to-action suggestions
✅ Best posting time recommendations
✅ Viral potential score dengan reasoning
```

### **3. AI-Powered Image/Media Upload**
```
Pilih: 1 (Smart Upload Pipeline)
Pilih: 3 (Image/Media)
Path: C:\Photos\image.jpg
Pilih: 1 (Generate AI caption dengan Gemini 2.0-flash)
Platform: Instagram
Language: English

AI akan create:
✅ Engaging captions dengan storytelling elements
✅ Platform-optimized descriptions
✅ Strategic hashtag combinations
✅ Engagement-driving call-to-actions
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

### **Gemini 2.0-flash Issues**
```bash
# Check API status
python gemini_ai_assistant.py --check-api

# Set API key
echo "GEMINI_API_KEY=your_actual_api_key" > .env

# Test AI capabilities
python gemini_ai_assistant.py --topic "test content" --platform tiktok
```

### **Login Issues**
```bash
# Clear cookies untuk login ulang
# Browser akan terbuka untuk login manual
# Cookies akan disimpan otomatis untuk next time
```

## 📊 System Requirements

### **Minimum Requirements**
- **OS**: Windows 10, Ubuntu 18.04+, macOS 10.14+
- **RAM**: 4GB (8GB recommended untuk AI features)
- **Storage**: 2GB free space (5GB+ recommended)
- **Browser**: Google Chrome
- **Python**: 3.8+
- **Internet**: Stable connection untuk AI API calls

### **Recommended untuk AI Features**
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **CPU**: Multi-core processor
- **GPU**: Optional, untuk faster video processing

## 🎉 Success Tips dengan Gemini 2.0-flash

### **1. First Time Setup**
1. Install Chrome browser
2. Run `python test_complete_system.py`
3. Setup Gemini API key di .env file
4. Login manually pertama kali (cookies akan disimpan)
5. Test AI features dengan sample content

### **2. AI-Enhanced Upload Tips**
- Gunakan video berkualitas HD untuk better AI analysis
- Provide specific prompts untuk more targeted content
- Experiment dengan different languages (English/Indonesian)
- Use AI-generated hashtags untuk better reach
- Follow AI posting time recommendations

### **3. Viral Content Strategy dengan AI**
- Analyze successful videos dengan AI untuk pattern recognition
- Use AI viral score predictions untuk content selection
- Implement AI-suggested hooks dan engagement tactics
- Test multiple AI-generated variations
- Monitor performance dan adjust strategy based on AI insights

## 📁 File Structure

```
social-media-uploader/
├── social_media_uploader.py      # Main script dengan AI integration ⭐
├── gemini_ai_assistant.py        # Gemini 2.0-flash AI assistant ⭐ ENHANCED!
├── tiktok_uploader.py            # TikTok uploader
├── facebook_uploader.py          # Facebook uploader
├── youtube_api_uploader.py       # YouTube API uploader
├── instagram_uploader.py         # Instagram uploader
├── video_downloader.py           # Video downloader (yt-dlp)
├── ffmpeg_video_editor.py        # Video editor
├── driver_manager.py             # Universal driver manager
├── fix_all_drivers.py            # Driver fix script
├── test_complete_system.py       # System test script
├── requirements.txt              # Dependencies dengan AI libraries
├── .env                          # Environment variables (API keys)
├── setup_gemini_api.md          # Gemini 2.0-flash setup guide ⭐
├── cookies/                      # Auto-created
├── credentials/                  # Auto-created
├── downloads/                    # Auto-created
├── edited_videos/                # Auto-created
├── ai_cache/                     # Auto-created untuk AI cache ⭐
└── screenshots/                  # Auto-created
```

## 🤖 Gemini 2.0-flash Capabilities

### **Advanced Video Analysis:**
- **Multi-frame Understanding** - Analyze multiple frames untuk context
- **Object & Scene Recognition** - Identify objects, people, settings
- **Emotion Detection** - Recognize emotions dan mood
- **Viral Element Detection** - Identify trending visual elements
- **Platform Optimization** - Suggest platform-specific improvements

### **Superior Content Generation:**
- **Viral Hook Creation** - Generate attention-grabbing hooks
- **Multi-variant Content** - Create multiple content variations
- **Trend Integration** - Incorporate current trends
- **Psychological Triggers** - Use proven engagement tactics
- **Platform Algorithm Awareness** - Optimize untuk each platform's algorithm

### **Enhanced Analytics:**
- **Viral Score Prediction** - Predict viral potential (1-10 scale)
- **Engagement Forecasting** - Estimate engagement rates
- **Audience Analysis** - Understand target demographics
- **Competition Insights** - Analyze competitive landscape
- **Performance Optimization** - Suggest improvements

## 🔒 Privacy & Security

- **API Keys**: Stored locally di .env file, tidak di cloud
- **Cookies**: Disimpan lokal untuk auto-login
- **Videos**: Processed lokal, tidak diupload ke AI servers
- **AI Analysis**: Only metadata sent to Gemini, not full videos
- **Safe**: Menggunakan official APIs dan secure automation

## ⚖️ Disclaimer

Script ini dibuat untuk tujuan edukasi dan otomasi personal. Pastikan mematuhi Terms of Service dari semua platform yang digunakan. Gunakan dengan bijak dan respect copyright. AI-generated content should be reviewed before publishing.

---

**Ready to create viral content dengan AI? Let's go! 🚀🤖✨**

### 🌟 **Powered by Gemini 2.0-flash - The Future of AI Content Creation!**