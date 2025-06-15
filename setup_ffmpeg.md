# Setup FFmpeg untuk Video Editing

## 🎬 Instalasi FFmpeg

### Windows:

#### Option 1: Download Manual
1. **Download FFmpeg**
   - Kunjungi: https://ffmpeg.org/download.html
   - Pilih "Windows" → "Windows builds by BtbN"
   - Download versi "release" (bukan git)
   - Extract ke `C:\ffmpeg\`

2. **Add to PATH**
   ```cmd
   # Buka Command Prompt sebagai Administrator
   setx /M PATH "%PATH%;C:\ffmpeg\bin"
   ```

3. **Test Installation**
   ```cmd
   ffmpeg -version
   ```

#### Option 2: Chocolatey
```cmd
# Install Chocolatey dulu jika belum ada
choco install ffmpeg
```

#### Option 3: Winget
```cmd
winget install ffmpeg
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

### Linux (CentOS/RHEL):
```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

### macOS:
```bash
# Menggunakan Homebrew
brew install ffmpeg
```

## 🔧 Verifikasi Instalasi

```bash
# Cek versi FFmpeg
ffmpeg -version

# Cek codec yang tersedia
ffmpeg -codecs

# Test FFmpeg dengan script
python ffmpeg_video_editor.py --help
```

## 🎯 Fitur FFmpeg Video Editor

### 1. **Video Enhancement**
- ✅ **Quality Enhancement** - Brightness, contrast, saturation, sharpness
- ✅ **Noise Reduction** - Light, medium, heavy noise reduction
- ✅ **Color Enhancement** - Vibrance, color correction
- ✅ **Sharpening** - Unsharp mask filter

### 2. **Anti-Detection Modifications**
- 🕵️ **Speed Variation** - Subtle speed changes (0.98x - 1.02x)
- 🎨 **Color Adjustment** - Hue shifts, brightness variations
- ✂️ **Crop & Resize** - Minimal cropping with resize back
- 🔄 **Horizontal Flip** - Mirror video horizontally
- 🔊 **Audio Pitch** - Subtle pitch modifications
- 📊 **Frame Interpolation** - Add/remove frames
- 🌟 **Noise Addition** - Add subtle noise
- 💡 **Brightness/Contrast** - Random adjustments

### 3. **Platform Optimization**
- 📱 **TikTok**: 1080x1920 (9:16), 30fps, max 60s
- 📘 **Facebook**: 1080x1080 (1:1) atau 1080x1920 (9:16)
- 📺 **YouTube Shorts**: 1080x1920 (9:16), 30fps, max 60s
- 📸 **Instagram Reels**: 1080x1920 (9:16), 30fps, max 90s

### 4. **Advanced Features**
- 🏷️ **Watermark** - Text watermark dengan posisi custom
- 🗜️ **Compression** - Target file size compression
- 🎭 **Video Variations** - Multiple variations dengan modifikasi berbeda
- 📦 **Batch Processing** - Process multiple videos sekaligus
- 🎵 **Audio Extraction** - Extract audio ke MP3/AAC

## 🚀 Cara Penggunaan

### 1. **Interactive Mode**
```bash
python ffmpeg_video_editor.py
```

### 2. **Command Line Mode**
```bash
# Enhance video quality
python ffmpeg_video_editor.py --input video.mp4 --operation enhance --preset medium

# Anti-detection modifications
python ffmpeg_video_editor.py --input video.mp4 --operation anti_detection --preset heavy

# Optimize for platform
python ffmpeg_video_editor.py --input video.mp4 --operation optimize --platform tiktok

# Create variations
python ffmpeg_video_editor.py --input video.mp4 --operation variations --variations 5

# Batch process
python ffmpeg_video_editor.py --input /path/to/videos/ --operation batch
```

### 3. **Integrated dengan Social Media Uploader**
```bash
# Upload dengan video enhancement
python social_media_uploader.py --platform ai-all-video --video video.mp4 --enhance-video

# Interactive mode dengan enhancement
python social_media_uploader.py
# Pilih opsi 7: AI-Powered Upload (otomatis enhance)
```

## 🎨 Enhancement Presets

### Light Enhancement:
- Brightness: +5%
- Contrast: +10%
- Saturation: +10%
- Sharpness: 0.3
- Noise Reduction: Light

### Medium Enhancement:
- Brightness: +10%
- Contrast: +20%
- Saturation: +20%
- Sharpness: 0.5
- Noise Reduction: Medium

### Heavy Enhancement:
- Brightness: +15%
- Contrast: +30%
- Saturation: +30%
- Sharpness: 0.7
- Noise Reduction: Heavy

## 🕵️ Anti-Detection Strategies

### Mengapa Perlu Anti-Detection?
- Platform social media menggunakan **content fingerprinting**
- Video yang sama akan dideteksi sebagai **reupload**
- Dapat menyebabkan **shadowban** atau **reduced reach**
- **Copyright claims** untuk konten yang bukan milik sendiri

### Teknik Anti-Detection:
1. **Pixel-level changes** - Subtle modifications yang tidak terlihat mata
2. **Temporal changes** - Speed variations, frame interpolation
3. **Audio modifications** - Pitch shifts, tempo changes
4. **Geometric changes** - Crop, resize, flip
5. **Color space changes** - Hue shifts, brightness variations

### Best Practices:
- Gunakan **kombinasi multiple techniques**
- **Jangan berlebihan** - tetap maintain quality
- **Test hasil** sebelum upload
- **Backup original** video
- **Monitor performance** setelah upload

## 📊 Output Quality Settings

### High Quality (CRF 18):
- Untuk video penting/premium
- File size besar
- Quality terbaik

### Medium Quality (CRF 20):
- Balance quality vs file size
- Recommended untuk most cases
- Good quality, reasonable size

### Compressed (Target Size):
- Untuk platform dengan size limit
- Automatic bitrate calculation
- Maintain quality dalam size limit

## 🔧 Troubleshooting

### Error: "FFmpeg not found"
```bash
# Windows - Add to PATH
setx PATH "%PATH%;C:\ffmpeg\bin"

# Linux - Install FFmpeg
sudo apt install ffmpeg

# Test installation
ffmpeg -version
```

### Error: "Codec not supported"
```bash
# Check available codecs
ffmpeg -codecs | grep h264

# Install additional codecs (Linux)
sudo apt install ubuntu-restricted-extras
```

### Error: "Permission denied"
```bash
# Make sure output directory is writable
chmod 755 edited_videos/

# Run with proper permissions
sudo python ffmpeg_video_editor.py
```

### Error: "Out of memory"
- Reduce video resolution
- Use lower quality settings
- Process shorter segments
- Close other applications

## 💡 Tips & Tricks

### 1. **Optimal Workflow**
```
Original Video → AI Analysis → FFmpeg Enhancement → Platform Upload
```

### 2. **Batch Processing**
- Process multiple videos overnight
- Use consistent settings
- Monitor disk space
- Backup originals

### 3. **Quality vs Size**
- TikTok: Prioritize engagement over quality
- YouTube: Balance quality and upload speed
- Facebook: Optimize for mobile viewing

### 4. **Anti-Detection Best Practices**
- Rotate through different modification sets
- Don't use same modifications repeatedly
- Test with small audience first
- Monitor analytics for shadowban signs

## 🎯 Integration dengan AI Assistant

### Workflow Terintegrasi:
1. **AI Analysis** → Analyze video content
2. **Content Generation** → Generate platform-specific content
3. **Video Enhancement** → Apply FFmpeg modifications
4. **Multi-Platform Upload** → Upload to all platforms

### Command Example:
```bash
# Full AI + FFmpeg workflow
python social_media_uploader.py --platform ai-all-video --video input.mp4 --enhance-video --gemini-api-key your_key
```

Dengan FFmpeg integration, video editing menjadi **professional-grade** dan **anti-detection ready**! 🎬✨🚀