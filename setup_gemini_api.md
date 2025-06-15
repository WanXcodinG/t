# Setup Gemini AI API

## 🔧 Langkah-langkah Setup Gemini API

### 1. Dapatkan Gemini API Key

1. **Buka Google AI Studio**
   - Kunjungi: https://makersuite.google.com/app/apikey
   - Login dengan akun Google Anda

2. **Buat API Key**
   - Klik "Create API Key"
   - Pilih project Google Cloud (atau buat baru)
   - Copy API key yang dihasilkan

### 2. Set Environment Variable

#### Windows:
```cmd
set GEMINI_API_KEY=your_api_key_here
```

#### Linux/Mac:
```bash
export GEMINI_API_KEY=your_api_key_here
```

#### Permanent (Windows):
```cmd
setx GEMINI_API_KEY "your_api_key_here"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Gemini AI Assistant

```bash
python gemini_ai_assistant.py --api-key your_api_key_here
```

## 🤖 Fitur AI Assistant

### 1. **Video Analysis & Content Generation**
- 🎬 **Frame-by-frame analysis** - Ekstrak dan analisis frame video
- 🔍 **Object detection** - Deteksi objek, aktivitas, setting
- 🎨 **Visual analysis** - Analisis warna, mood, komposisi
- 📝 **Auto content generation** - Generate judul, deskripsi, hashtag
- 🎯 **Platform optimization** - Konten dioptimasi per platform

### 2. **Platform-Specific Content**
- 📱 **TikTok**: Viral, trendy, youth-focused content
- 📘 **Facebook**: Engaging, shareable, community-focused
- 📺 **YouTube**: SEO-optimized, searchable, informative

### 3. **Text Content Generation**
- ✍️ **Smart text posts** - Generate post berdasarkan topik
- 🔧 **Content optimization** - Optimasi konten existing
- 📈 **Trending suggestions** - Saran konten trending
- 🕵️ **Competitor analysis** - Analisis konten kompetitor

### 4. **Advanced Features**
- 🎯 **Multi-platform targeting** - Satu video, konten untuk semua platform
- 🔄 **Content variations** - Multiple angle untuk satu topik
- 📊 **SEO optimization** - Keywords dan hashtag optimal
- 🎪 **Engagement hooks** - Opening yang menarik perhatian

## 🚀 Cara Penggunaan

### 1. **AI-Powered Upload (Recommended)**
```bash
# Interactive mode
python social_media_uploader.py

# Pilih opsi 7: AI-Powered Upload ke SEMUA Platform
```

### 2. **Video Analysis Only**
```bash
python gemini_ai_assistant.py --video "path/to/video.mp4"
```

### 3. **Generate Text Post**
```bash
python gemini_ai_assistant.py --topic "tips produktivitas" --platform facebook
```

### 4. **Command Line AI Upload**
```bash
python social_media_uploader.py --platform ai-all-video --video "video.mp4" --gemini-api-key "your_key"
```

## 📋 AI Analysis Output

### Video Metadata:
- ✅ Durasi, resolusi, format
- ✅ Aspect ratio detection
- ✅ Shorts suitability check
- ✅ File size optimization

### Content Analysis:
- 🎯 **Objects**: Objek utama dalam video
- 🎬 **Activities**: Aktivitas yang terjadi
- 🏠 **Setting**: Indoor/outdoor, lokasi
- 🎨 **Mood**: Suasana dan emosi
- 🌈 **Colors**: Warna dominan
- 🪝 **Hooks**: Elemen menarik untuk engagement
- 📈 **Viral Potential**: Potensi viral content

### Generated Content:
- 📝 **Title**: Judul SEO-friendly per platform
- 📄 **Description**: Deskripsi engaging dan informatif
- #️⃣ **Hashtags**: 10-15 hashtag trending dan relevan
- 🪝 **Hook**: Opening line yang menarik
- 📢 **CTA**: Call-to-action yang sesuai platform
- 🔍 **Keywords**: Keywords untuk discoverability

## 🎯 Platform Optimization

### TikTok:
- **Style**: Viral, trendy, engaging, youth-focused
- **Tone**: Casual, energetic, fun
- **Hashtags**: #fyp #viral #trending #foryou
- **Max Title**: 150 characters

### Facebook:
- **Style**: Engaging, shareable, community-focused
- **Tone**: Friendly, conversational, inclusive
- **Hashtags**: #facebook #social #share
- **Max Title**: 255 characters

### YouTube:
- **Style**: SEO-optimized, searchable, informative
- **Tone**: Informative, engaging, searchable
- **Hashtags**: #Shorts #YouTube #viral
- **Max Title**: 100 characters

## 🔧 Troubleshooting

### Error: "API key not found"
```bash
# Set environment variable
set GEMINI_API_KEY=your_api_key_here

# Or pass directly
python gemini_ai_assistant.py --api-key your_api_key_here
```

### Error: "Video analysis failed"
- Pastikan video format didukung (MP4, AVI, MOV)
- Cek ukuran file (max 100MB recommended)
- Pastikan video tidak corrupt

### Error: "OpenCV not found"
```bash
pip install opencv-python
```

### Error: "Pillow not found"
```bash
pip install pillow
```

## 💡 Tips Penggunaan

### 1. **Optimal Video Format**
- Format: MP4, MOV, AVI
- Durasi: 15-60 detik untuk Shorts
- Resolusi: 1080x1920 (9:16) untuk Shorts
- Ukuran: < 100MB untuk analysis cepat

### 2. **Best Practices**
- Gunakan video dengan visual yang jelas
- Pastikan ada aktivitas/gerakan dalam video
- Video dengan objek yang mudah diidentifikasi
- Hindari video yang terlalu gelap/blur

### 3. **Content Strategy**
- Gunakan AI suggestions sebagai starting point
- Customize sesuai brand voice Anda
- Test different variations
- Monitor performance dan adjust

## 🎉 Keunggulan AI Assistant

### ✅ **Intelligent Analysis**
- Frame-by-frame video analysis
- Object dan activity detection
- Mood dan visual analysis
- Viral potential assessment

### ✅ **Platform Optimization**
- Content disesuaikan per platform
- SEO-friendly titles dan descriptions
- Trending hashtags dan keywords
- Engagement-focused hooks

### ✅ **Time Saving**
- Otomatis generate semua konten
- Tidak perlu riset manual
- Konsisten quality output
- Scalable untuk banyak video

### ✅ **Professional Quality**
- AI-powered content generation
- Data-driven recommendations
- Trend-aware suggestions
- Multi-language support

Dengan Gemini AI Assistant, content creation menjadi **super intelligent** dan **highly optimized**! 🚀🤖✨