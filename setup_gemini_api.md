# Setup Gemini AI API - Updated untuk .env

## 🔧 Langkah-langkah Setup Gemini API

### 1. Dapatkan Gemini API Key

1. **Buka Google AI Studio**
   - Kunjungi: https://makersuite.google.com/app/apikey
   - Login dengan akun Google Anda

2. **Buat API Key**
   - Klik "Create API Key"
   - Pilih project Google Cloud (atau buat baru)
   - Copy API key yang dihasilkan

### 2. Setup Environment Variable dengan .env File

#### Buat file .env di folder project:
```bash
# File: .env
GEMINI_API_KEY=your_api_key_here
```

**PENTING:** 
- Ganti `your_api_key_here` dengan API key yang sebenarnya
- Jangan commit file .env ke git (sudah ada di .gitignore)
- File .env akan otomatis dibaca oleh semua script

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Gemini AI Assistant

```bash
python gemini_ai_assistant.py --check-api
```

## 🚀 Fitur Gemini 2.0-flash

### ✨ **Model Terbaru:**
- **Primary Model**: `gemini-2.0-flash-exp` (Latest & Most Powerful)
- **Fallback Model**: `gemini-pro` (jika 2.0-flash tidak tersedia)
- **Vision Model**: `gemini-2.0-flash-exp` untuk analisis video

### 🎯 **Enhanced Features:**

#### 1. **Advanced Video Analysis:**
- ✅ **Comprehensive Analysis** dengan 15+ parameter
- ✅ **Viral Score Prediction** (1-10 scale)
- ✅ **Target Audience Detection**
- ✅ **Content Type Classification**
- ✅ **Optimization Tips** yang actionable
- ✅ **Trending Elements** identification
- ✅ **Engagement Potential** assessment

#### 2. **Smart Content Generation:**
- ✅ **Platform-Native Content** untuk setiap platform
- ✅ **Trending Hooks** dan viral formats
- ✅ **SEO-Optimized** titles dan descriptions
- ✅ **Engagement Tactics** yang proven
- ✅ **Emotional Triggers** untuk better reach
- ✅ **Call-to-Action** yang compelling

#### 3. **Enhanced Platform Optimization:**
- 🎵 **TikTok**: Viral hooks, trending slang, youth-focused
- 📸 **Instagram**: Aesthetic, lifestyle, story-worthy
- 📺 **YouTube**: SEO-optimized, educational, retention-focused
- 📘 **Facebook**: Community-focused, discussion-starter

## 📋 **Cara Test:**

#### 1. **Check API Status:**
```bash
python gemini_ai_assistant.py --check-api
```

#### 2. **Test Video Analysis:**
```bash
python gemini_ai_assistant.py --video "path/to/video.mp4" --strategy viral
```

#### 3. **Test Text Generation:**
```bash
python gemini_ai_assistant.py --topic "tips produktivitas" --platform tiktok
```

#### 4. **Interactive Mode:**
```bash
python gemini_ai_assistant.py
```

## 🔧 Troubleshooting

### Error: "API key not found"
- Pastikan file .env ada di folder project
- Pastikan GEMINI_API_KEY sudah diset dengan benar
- Restart terminal/IDE setelah membuat .env

### Error: "google-generativeai not found"
```bash
pip install google-generativeai
```

### Error: "python-dotenv not found"
```bash
pip install python-dotenv
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

## 🎉 Keunggulan Gemini 2.0-flash

### ✅ **Intelligence:**
- **2x Faster** response time
- **Better Understanding** of context
- **More Accurate** content generation
- **Enhanced Creativity** dalam output

### ✅ **Content Quality:**
- **Higher Engagement** potential
- **More Viral** content suggestions
- **Better Platform Optimization**
- **Trending Elements** integration

Dengan Gemini 2.0-flash dan .env configuration, AI Assistant menjadi **super intelligent** dan **highly optimized**! 🚀🤖✨