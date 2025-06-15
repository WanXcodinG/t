# 📁 Folder Structure - Social Media Uploader Super Advanced

## 🗂️ **Required Folder Structure:**

```
social-media-uploader/
├── 📄 **Main Files**
│   ├── social_media_uploader.py           # Main uploader dengan AI & FFmpeg terintegrasi ⭐
│   ├── tiktok_uploader.py                 # TikTok uploader
│   ├── facebook_uploader.py               # Facebook uploader (Status & Reels) ✅
│   ├── youtube_api_uploader.py            # YouTube API uploader
│   ├── gemini_ai_assistant.py             # Advanced Gemini AI assistant ⭐ ENHANCED!
│   ├── ffmpeg_video_editor.py             # Advanced FFmpeg video editor ⭐ ENHANCED!
│   ├── requirements.txt                   # Dependencies dengan AI & CV libraries
│   └── README.md                          # Dokumentasi lengkap
│
├── 📚 **Documentation**
│   ├── setup_gemini_api.md               # Gemini API setup guide
│   ├── setup_ffmpeg.md                   # FFmpeg setup guide
│   ├── setup_youtube_api.md              # YouTube API setup guide
│   └── folder_structure.md               # This file
│
├── 🍪 **cookies/** (Auto-created)
│   ├── tiktok_cookies.json               # TikTok login cookies
│   ├── facebook_cookies.json             # Facebook login cookies
│   └── youtube_cookies.json              # YouTube login cookies (legacy)
│
├── 🔑 **credentials/** (Auto-created)
│   ├── youtube_credentials.json          # YouTube API credentials (download from Google Cloud)
│   └── youtube_token.json                # YouTube API token (auto-generated)
│
├── 🎬 **edited_videos/** (Auto-created)
│   ├── enhanced/                          # Enhanced videos
│   ├── anti_detection/                    # Anti-detection modified videos
│   ├── platform_optimized/               # Platform-specific optimized videos
│   ├── variations/                        # Video variations
│   └── final_output/                      # Final processed videos
│
├── 🗂️ **temp/** (Auto-created)
│   ├── frames/                            # Extracted video frames for AI analysis
│   ├── audio/                             # Extracted audio files
│   └── processing/                        # Temporary processing files
│
├── ⚙️ **temp_ffmpeg/** (Auto-created)
│   ├── intermediate/                      # Intermediate processing files
│   ├── filters/                           # Filter processing files
│   └── encoding/                          # Encoding temporary files
│
├── 🤖 **ai_cache/** (Auto-created)
│   ├── video_analysis/                    # Cached AI video analysis
│   ├── content_generation/                # Cached AI content generation
│   └── performance_predictions/           # Cached performance predictions
│
├── 📝 **content_library/** (Auto-created)
│   ├── generated_titles/                  # AI-generated titles library
│   ├── generated_descriptions/            # AI-generated descriptions library
│   ├── hashtag_collections/               # Hashtag collections per platform
│   └── content_templates/                 # Content templates
│
├── 🎛️ **ffmpeg_presets/** (Auto-created)
│   ├── enhancement/                       # Video enhancement presets
│   ├── anti_detection/                    # Anti-detection presets
│   ├── platform_optimization/             # Platform optimization presets
│   └── custom/                            # Custom user presets
│
├── 💾 **ffmpeg_cache/** (Auto-created)
│   ├── processed_videos/                  # Cache of processed videos
│   ├── filter_cache/                      # Filter processing cache
│   └── encoding_profiles/                 # Encoding profiles cache
│
├── 📸 **screenshots/** (Auto-created)
│   ├── tiktok/                            # TikTok error screenshots
│   ├── facebook/                          # Facebook error screenshots
│   ├── youtube/                           # YouTube error screenshots
│   └── debug/                             # General debug screenshots
│
├── 📋 **logs/** (Auto-created)
│   ├── upload_logs/                       # Upload operation logs
│   ├── ai_logs/                           # AI processing logs
│   ├── ffmpeg_logs/                       # FFmpeg processing logs
│   └── error_logs/                        # Error logs
│
└── 💾 **backups/** (Auto-created)
    ├── original_videos/                   # Backup of original videos
    ├── cookies_backup/                    # Backup of cookies
    ├── credentials_backup/                # Backup of credentials
    └── config_backup/                     # Backup of configurations
```

## 📋 **Folder Descriptions:**

### 🍪 **cookies/**
- **Purpose:** Store login cookies untuk auto-login ke platform
- **Files:** JSON files dengan session cookies
- **Auto-managed:** Ya, otomatis dibuat dan diupdate
- **Backup:** Recommended untuk cookies yang valid

### 🔑 **credentials/**
- **Purpose:** Store API credentials dan tokens
- **Important:** `youtube_credentials.json` harus didownload manual dari Google Cloud Console
- **Security:** Jangan commit ke git, add ke .gitignore
- **Auto-managed:** Token auto-generated, credentials manual

### 🎬 **edited_videos/**
- **Purpose:** Output semua video yang sudah diproses
- **Subfolders:** Organized by processing type
- **Size:** Bisa besar, monitor disk space
- **Cleanup:** Auto-cleanup old files (configurable)

### 🗂️ **temp/**
- **Purpose:** Temporary files untuk AI processing
- **Lifecycle:** Auto-cleanup setelah processing selesai
- **Contents:** Frames, audio, intermediate files
- **Performance:** SSD recommended untuk speed

### ⚙️ **temp_ffmpeg/**
- **Purpose:** FFmpeg temporary processing files
- **Lifecycle:** Auto-cleanup setelah encoding selesai
- **Size:** Bisa besar saat processing video besar
- **Performance:** Fast storage recommended

### 🤖 **ai_cache/**
- **Purpose:** Cache AI analysis untuk speed improvement
- **Benefits:** Avoid re-analyzing same videos
- **Size:** Relatif kecil (JSON files)
- **TTL:** Configurable cache expiration

### 📝 **content_library/**
- **Purpose:** Library konten yang sudah digenerate AI
- **Reusability:** Konten bisa digunakan ulang
- **Organization:** Per platform dan kategori
- **Growth:** Akan bertambah seiring waktu

### 🎛️ **ffmpeg_presets/**
- **Purpose:** Preset konfigurasi FFmpeg
- **Customization:** User bisa buat preset sendiri
- **Sharing:** Preset bisa dishare antar user
- **Versioning:** Track changes pada preset

### 💾 **ffmpeg_cache/**
- **Purpose:** Cache hasil processing FFmpeg
- **Speed:** Significant speed improvement
- **Size:** Monitor dan cleanup berkala
- **Efficiency:** Avoid re-processing identical operations

### 📸 **screenshots/**
- **Purpose:** Debug screenshots saat error
- **Debugging:** Essential untuk troubleshooting
- **Organization:** Per platform untuk easy navigation
- **Retention:** Auto-delete old screenshots

### 📋 **logs/**
- **Purpose:** Comprehensive logging system
- **Debugging:** Track semua operations
- **Analytics:** Performance monitoring
- **Retention:** Configurable log rotation

### 💾 **backups/**
- **Purpose:** Backup important files
- **Safety:** Prevent data loss
- **Recovery:** Easy restore functionality
- **Automation:** Auto-backup critical files

## 🚀 **Auto-Creation:**

Semua folder akan **otomatis dibuat** saat pertama kali menjalankan script:

```python
# Folders auto-created by scripts
self.cookies_dir.mkdir(exist_ok=True)
self.credentials_dir.mkdir(exist_ok=True)
self.edited_videos_dir.mkdir(exist_ok=True)
self.temp_dir.mkdir(exist_ok=True)
# ... dan seterusnya
```

## ⚙️ **Configuration:**

Folder paths bisa dikonfigurasi di masing-masing script:

```python
# Customizable paths
self.base_dir = Path(__file__).parent
self.output_dir = self.base_dir / "edited_videos"
self.cache_dir = self.base_dir / "ai_cache"
# ... etc
```

## 🧹 **Maintenance:**

### Auto-Cleanup:
- **Temp files:** Auto-cleanup setelah processing
- **Old screenshots:** Cleanup files > 7 days
- **Cache files:** Cleanup berdasarkan TTL
- **Log rotation:** Keep last 30 days

### Manual Cleanup:
```bash
# Cleanup semua temp files
python social_media_uploader.py --cleanup-temp

# Cleanup cache files
python social_media_uploader.py --cleanup-cache

# Full cleanup (keep only essentials)
python social_media_uploader.py --cleanup-all
```

## 📊 **Disk Space Monitoring:**

### Estimated Sizes:
- **cookies/:** < 1MB
- **credentials/:** < 1MB  
- **edited_videos/:** 100MB - 10GB+ (depends on usage)
- **temp/:** 50MB - 1GB (during processing)
- **ai_cache/:** 10MB - 100MB
- **content_library/:** 10MB - 50MB
- **ffmpeg_cache/:** 100MB - 1GB
- **screenshots/:** 10MB - 100MB
- **logs/:** 10MB - 100MB
- **backups/:** Varies

### Recommendations:
- **Minimum:** 5GB free space
- **Recommended:** 20GB+ free space
- **Heavy usage:** 50GB+ free space
- **SSD:** Recommended untuk temp folders

## 🔒 **Security & Privacy:**

### Sensitive Folders:
- **cookies/:** Contains login sessions
- **credentials/:** Contains API keys
- **backups/:** May contain sensitive data

### .gitignore Recommendations:
```gitignore
cookies/
credentials/
temp/
temp_ffmpeg/
ai_cache/
ffmpeg_cache/
screenshots/
logs/
backups/
*.log
*.tmp
```

## 🎯 **Quick Setup:**

1. **Clone/Download** project files
2. **Run** any script - folders auto-created
3. **Add** YouTube credentials manually ke `credentials/`
4. **Set** Gemini API key environment variable
5. **Install** FFmpeg dan dependencies
6. **Ready** to use! 🚀

Semua folder structure ini dirancang untuk **maximum efficiency**, **easy maintenance**, dan **scalability** untuk sistem super advanced! 📁✨