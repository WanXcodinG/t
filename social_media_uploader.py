#!/usr/bin/env python3
"""
Social Media Uploader - SUPER ENHANCED VERSION
Upload ke TikTok, Facebook, YouTube, Instagram dengan dukungan AI content generation,
video enhancement, dan video downloader terintegrasi
Support untuk FILE VIDEO LOKAL atau LINK VIDEO SOSMED untuk SEMUA pilihan
Enhanced dengan Gemini 2.0-flash AI dan Language Support
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import re
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Import modules dengan error handling
try:
    from tiktok_uploader import TikTokUploader
    from facebook_uploader import FacebookUploader
    from youtube_api_uploader import YouTubeAPIUploader
    from instagram_uploader import InstagramUploader
    from video_downloader import VideoDownloader
    UPLOADERS_AVAILABLE = True
except ImportError as e:
    print(f"{Fore.YELLOW}⚠️ Some modules not available: {e}")
    UPLOADERS_AVAILABLE = False

try:
    from gemini_ai_assistant import GeminiAIAssistant
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from ffmpeg_video_editor import FFmpegVideoEditor
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

class SocialMediaUploader:
    def __init__(self, debug: bool = False):
        """
        Initialize Social Media Uploader
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.temp_dir = self.base_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.downloads_dir = self.base_dir / "downloads"
        self.downloads_dir.mkdir(exist_ok=True)
        self.edited_videos_dir = self.base_dir / "edited_videos"
        self.edited_videos_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        self._load_env_file()
        
        # Initialize components
        self.video_downloader = VideoDownloader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.ai_assistant = GeminiAIAssistant(debug=debug) if AI_AVAILABLE else None
        self.video_editor = FFmpegVideoEditor(debug=debug) if FFMPEG_AVAILABLE else None
        
        # Initialize uploaders dengan proper parameters
        self.tiktok_uploader = TikTokUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.facebook_uploader = FacebookUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.youtube_uploader = YouTubeAPIUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.instagram_uploader = InstagramUploader(debug=debug) if UPLOADERS_AVAILABLE else None

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA,
            "HEADER": Fore.LIGHTBLUE_EX,
            "PIPELINE": Fore.LIGHTMAGENTA_EX,
            "DOWNLOAD": Fore.LIGHTBLUE_EX,
            "AI": Fore.LIGHTMAGENTA_EX
        }
        
        if level == "DEBUG" and not self.debug:
            return
            
        color = colors.get(level, Fore.WHITE)
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍",
            "HEADER": "🚀",
            "PIPELINE": "⚙️",
            "DOWNLOAD": "📥",
            "AI": "🤖"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = self.base_dir / ".env"
        
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                
                if self.debug:
                    self._log("Environment variables loaded from .env file", "SUCCESS")
            except Exception as e:
                if self.debug:
                    self._log(f"Error loading .env file: {e}", "WARNING")

    def is_video_url(self, input_string: str) -> bool:
        """Check if input is a video URL"""
        if not input_string:
            return False
        
        # Check if it's a URL
        try:
            parsed = urlparse(input_string)
            if not parsed.scheme or not parsed.netloc:
                return False
        except:
            return False
        
        # Check for known video platforms
        video_platforms = [
            'youtube.com', 'youtu.be', 'youtube-nocookie.com',
            'tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com',
            'facebook.com', 'fb.watch', 'fb.com',
            'instagram.com', 'instagr.am',
            'twitter.com', 't.co', 'x.com',
            'vimeo.com', 'dailymotion.com', 'twitch.tv'
        ]
        
        return any(platform in input_string.lower() for platform in video_platforms)

    def is_media_file(self, file_path: str) -> tuple:
        """
        Check if file is a valid media file
        
        Returns:
            tuple: (is_valid, media_type) where media_type is 'image' or 'video'
        """
        if not os.path.exists(file_path):
            return False, None
        
        # Image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
        # Video extensions
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        
        file_lower = file_path.lower()
        
        if any(file_lower.endswith(ext) for ext in image_extensions):
            return True, 'image'
        elif any(file_lower.endswith(ext) for ext in video_extensions):
            return True, 'video'
        else:
            return False, None

    def get_media_source(self, prompt_message: str = "Media source", allow_images: bool = True) -> tuple:
        """
        Universal media source getter - mendukung file lokal dan URL untuk video/image
        
        Args:
            prompt_message: Custom prompt message
            allow_images: Whether to allow image files
            
        Returns:
            tuple: (media_path, source_type, media_type) 
            where source_type is 'file' or 'url' and media_type is 'image' or 'video'
        """
        print(f"\n{Fore.YELLOW}📹 {prompt_message}:")
        print("=" * 50)
        
        if allow_images:
            print("1. 📁 File media lokal (image/video)")
            print("2. 🔗 Link video sosmed (YouTube, TikTok, Facebook, Instagram, dll)")
        else:
            print("1. 📁 File video lokal")
            print("2. 🔗 Link video sosmed (YouTube, TikTok, Facebook, Instagram, dll)")
        
        print("3. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-3): ").strip()
        
        if choice == "1":
            # File media lokal
            if allow_images:
                media_path = input(f"{Fore.CYAN}Path ke file media (image/video): ").strip()
            else:
                media_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            
            # Remove quotes if present
            media_path = media_path.strip('"').strip("'")
            
            # Validate media file
            is_valid, media_type = self.is_media_file(media_path)
            
            if not is_valid:
                if allow_images:
                    self._log("File bukan format media yang didukung!", "ERROR")
                    self._log("Format yang didukung: JPG, PNG, GIF, MP4, MOV, AVI, MKV, WebM, dll", "INFO")
                else:
                    self._log("File bukan format video yang didukung!", "ERROR")
                    self._log("Format yang didukung: MP4, MOV, AVI, MKV, WebM, FLV, dll", "INFO")
                return None, None, None
            
            if not allow_images and media_type == 'image':
                self._log("Hanya file video yang diperbolehkan untuk pilihan ini!", "ERROR")
                return None, None, None
            
            file_size = os.path.getsize(media_path) / (1024 * 1024)  # MB
            self._log(f"File {media_type} ditemukan: {os.path.basename(media_path)} ({file_size:.2f}MB)", "SUCCESS")
            
            return media_path, "file", media_type
        
        elif choice == "2":
            # Link video sosmed
            video_url = input(f"{Fore.CYAN}URL video: ").strip()
            
            if not video_url:
                self._log("URL tidak boleh kosong!", "ERROR")
                return None, None, None
            
            if not self.is_video_url(video_url):
                self._log("URL tidak valid atau platform tidak didukung!", "ERROR")
                self._log("Platform yang didukung: YouTube, TikTok, Facebook, Instagram, Twitter, Vimeo, dll", "INFO")
                return None, None, None
            
            if not self.video_downloader:
                self._log("Video downloader tidak tersedia!", "ERROR")
                self._log("Install yt-dlp dengan: pip install yt-dlp", "INFO")
                return None, None, None
            
            # Download video
            self._log("📥 Downloading video dari URL...", "DOWNLOAD")
            
            # Detect platform untuk optimasi download
            platform = self.video_downloader.detect_platform(video_url)
            self._log(f"ℹ️ Platform terdeteksi: {platform}", "INFO")
            
            # Get video info first
            info = self.video_downloader.get_video_info(video_url)
            if "error" not in info:
                self._log(f"ℹ️ Video: {info.get('title', 'Unknown')[:50]}...", "INFO")
                self._log(f"ℹ️ Durasi: {info.get('duration', 0):.0f} detik", "INFO")
                self._log(f"ℹ️ Platform: {info.get('platform', 'unknown')}", "INFO")
            
            # Choose quality
            print(f"\n{Fore.YELLOW}Pilih kualitas download:")
            print("1. 🔥 Best (Kualitas terbaik)")
            print("2. ⚡ High (1080p)")
            print("3. 📱 Medium (720p)")
            print("4. 💾 Low (480p)")
            
            quality_choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 2): ").strip()
            quality_map = {"1": "best", "2": "high", "3": "medium", "4": "low"}
            quality = quality_map.get(quality_choice, "high")
            
            # Download video
            result = self.video_downloader.download_video(video_url, quality=quality)
            
            if result.get("success"):
                video_path = result["file_path"]
                self._log(f"✅ Video berhasil didownload: {result['filename']}", "SUCCESS")
                self._log(f"ℹ️ Size: {result['file_size_mb']:.2f}MB", "INFO")
                return video_path, "url", "video"
            else:
                self._log(f"❌ Download gagal: {result.get('error')}", "ERROR")
                return None, None, None
        
        elif choice == "3":
            return None, None, None
        
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return None, None, None

    def get_ai_language_preference(self) -> str:
        """Get user's language preference for AI content"""
        print(f"\n{Fore.LIGHTMAGENTA_EX}🌍 PILIH BAHASA UNTUK AI CONTENT:")
        print("1. 🇮🇩 Bahasa Indonesia")
        print("2. 🇺🇸 English")
        
        choice = input(f"{Fore.WHITE}Pilihan (1-2, default: 1): ").strip()
        
        if choice == "2":
            self._log("Language selected: English", "AI")
            return "english"
        else:
            self._log("Bahasa dipilih: Indonesia", "AI")
            return "indonesian"

    def check_system_requirements(self):
        """Check system requirements"""
        self._log("Checking system requirements...", "HEADER")
        
        issues = []
        
        # Check Chrome
        try:
            from driver_manager import UniversalDriverManager
            manager = UniversalDriverManager()
            chrome_version = manager.get_chrome_version()
            if chrome_version:
                self._log(f"Chrome: ✅ {chrome_version}", "SUCCESS")
            else:
                self._log("Chrome: ❌ Not found", "ERROR")
                issues.append("Chrome browser not installed")
        except Exception as e:
            self._log(f"Chrome check failed: {e}", "WARNING")
            issues.append("Chrome detection error")
        
        # Check ChromeDriver
        try:
            from driver_manager import UniversalDriverManager
            manager = UniversalDriverManager()
            chromedriver_path = manager.find_existing_chromedriver()
            if chromedriver_path:
                self._log(f"ChromeDriver: ✅ Found", "SUCCESS")
            else:
                self._log("ChromeDriver: ⚠️ Will auto-download", "WARNING")
        except Exception as e:
            self._log(f"ChromeDriver check failed: {e}", "WARNING")
        
        return issues

    def show_main_menu(self):
        """Show main interactive menu"""
        print(f"\n{Fore.LIGHTBLUE_EX}🚀 SUPER ADVANCED SOCIAL MEDIA UPLOADER")
        print("=" * 70)
        print(f"{Fore.LIGHTMAGENTA_EX}🎯 Dengan Video + Text + Media Support + AI + FFmpeg + Instagram Integration")
        print(f"{Fore.LIGHTGREEN_EX}📹 Support: File Lokal & Link Sosmed untuk SEMUA pilihan")
        print(f"{Fore.LIGHTYELLOW_EX}🤖 Enhanced dengan Gemini 2.0-flash AI & Language Support")
        print()
        print(f"{Fore.CYAN}💻 System: {os.name.upper()}")
        print()
        
        print(f"{Fore.YELLOW}📋 MENU UTAMA:")
        print("1. 🚀 Smart Upload Pipeline (Video/Text/Media)")
        print("2. 📊 System Status & Diagnostics")
        print("3. 🧹 System Cleanup")
        print("4. ❌ Exit")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            self._smart_upload_pipeline()
        elif choice == "2":
            self._show_system_status()
        elif choice == "3":
            self._system_cleanup()
        elif choice == "4":
            print(f"{Fore.YELLOW}👋 Sampai jumpa!")
            return False
        else:
            self._log("Pilihan tidak valid!", "ERROR")
        
        return True

    def _smart_upload_pipeline(self):
        """Smart upload pipeline dengan enhanced video input"""
        print(f"\n{Fore.LIGHTMAGENTA_EX}🚀 SMART UPLOAD PIPELINE")
        print("=" * 60)
        
        # Check system requirements first
        issues = self.check_system_requirements()
        
        if issues:
            self._log("System requirements check failed:", "ERROR")
            for issue in issues:
                print(f"  • {issue}")
            
            print(f"\n{Fore.YELLOW}🔧 Quick fixes:")
            print("1. Install Chrome: Download from https://www.google.com/chrome/")
            print("2. Run: python fix_all_drivers.py")
            print("3. Install dependencies: pip install -r requirements.txt")
            return
        
        print(f"\n{Fore.YELLOW}📹 PILIH JENIS KONTEN:")
        print("=" * 50)
        print("1. 🎬 Video Content (File/Link → TikTok, Facebook Reels, YouTube Shorts, Instagram Reels)")
        print("2. 📝 Text Status (Facebook Status)")
        print("3. 🖼️ Image/Media (File/Link → Facebook Post, Instagram Post)")
        print("4. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            self._video_content_pipeline()
        elif choice == "2":
            self._text_status_pipeline()
        elif choice == "3":
            self._image_media_pipeline()
        elif choice == "4":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _video_content_pipeline(self):
        """Enhanced video content upload pipeline dengan file/URL support"""
        print(f"\n{Fore.CYAN}🎬 VIDEO CONTENT PIPELINE")
        print("=" * 40)
        
        # Get video source (file atau URL) - hanya video
        media_path, source_type, media_type = self.get_media_source("PILIH SUMBER VIDEO", allow_images=False)
        
        if not media_path:
            return
        
        self._log(f"✅ Media source: {source_type} - video - {os.path.basename(media_path)}", "SUCCESS")
        
        # Optional: Video enhancement
        enhanced_video_path = media_path
        
        if self.video_editor and self.video_editor.ffmpeg_path:
            print(f"\n{Fore.YELLOW}🎨 Video Enhancement (Optional):")
            print("1. ✨ Enhance video quality")
            print("2. 🕵️ Apply anti-detection")
            print("3. 📱 Optimize for platforms")
            print("4. ⏭️ Skip enhancement")
            
            enhance_choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
            
            if enhance_choice == "1":
                self._log("Enhancing video quality...", "PIPELINE")
                result = self.video_editor.enhance_video(media_path, preset="medium")
                if result.get("success"):
                    enhanced_video_path = result["output_path"]
                    self._log(f"Video enhanced: {result['file_size_mb']:.2f}MB", "SUCCESS")
                else:
                    self._log(f"Enhancement failed: {result.get('error')}", "WARNING")
            
            elif enhance_choice == "2":
                self._log("Applying anti-detection...", "PIPELINE")
                result = self.video_editor.apply_anti_detection(media_path, intensity="medium")
                if result.get("success"):
                    enhanced_video_path = result["output_path"]
                    self._log(f"Anti-detection applied: {result['file_size_mb']:.2f}MB", "SUCCESS")
                else:
                    self._log(f"Anti-detection failed: {result.get('error')}", "WARNING")
            
            elif enhance_choice == "3":
                print(f"\n{Fore.YELLOW}Pilih platform untuk optimasi:")
                print("1. TikTok")
                print("2. Instagram")
                print("3. YouTube")
                print("4. Facebook")
                
                platform_choice = input(f"{Fore.WHITE}Pilihan (1-4): ").strip()
                platform_map = {"1": "tiktok", "2": "instagram", "3": "youtube", "4": "facebook"}
                platform = platform_map.get(platform_choice, "tiktok")
                
                self._log(f"Optimizing for {platform}...", "PIPELINE")
                result = self.video_editor.optimize_for_platform(media_path, platform)
                if result.get("success"):
                    enhanced_video_path = result["output_path"]
                    self._log(f"Platform optimization complete: {result['file_size_mb']:.2f}MB", "SUCCESS")
                else:
                    self._log(f"Optimization failed: {result.get('error')}", "WARNING")
        
        # Select platforms
        platforms = self._select_platforms()
        if not platforms:
            return
        
        # Optional: AI content generation dengan language support
        ai_content = None
        if self.ai_assistant:
            print(f"\n{Fore.YELLOW}🤖 AI Content Generation (Optional):")
            print("1. 🎯 Generate AI content untuk semua platform")
            print("2. ⏭️ Skip AI generation")
            
            ai_choice = input(f"\n{Fore.WHITE}Pilihan (1-2): ").strip()
            
            if ai_choice == "1":
                # Get language preference
                language = self.get_ai_language_preference()
                
                self._log("⚙️ Analyzing video dengan Gemini 2.0-flash...", "AI")
                analysis = self.ai_assistant.analyze_video_content(enhanced_video_path, language=language)
                
                if analysis:
                    self._log("⚙️ Generating platform-specific content...", "AI")
                    ai_content = self.ai_assistant.generate_platform_content(analysis, platforms, language=language)
                    
                    print(f"\n{Fore.GREEN}🎯 AI CONTENT GENERATED:")
                    for platform in platforms:
                        if platform in ai_content:
                            content = ai_content[platform]
                            print(f"\n{platform.upper()}:")
                            if 'title_options' in content:
                                print(f"  Title Options: {content['title_options'][:2]}")
                            else:
                                print(f"  Title: {content.get('title', 'N/A')}")
                            print(f"  Description: {content.get('description', 'N/A')[:100]}...")
                            if 'caption_suggestion' in content:
                                print(f"  Caption: {content.get('caption_suggestion', 'N/A')}")
        
        # Upload to selected platforms
        self._upload_video_to_platforms(enhanced_video_path, platforms, ai_content)

    def _text_status_pipeline(self):
        """Text status pipeline dengan enhanced AI"""
        print(f"\n{Fore.CYAN}📝 TEXT STATUS PIPELINE")
        print("=" * 40)
        
        if not self.facebook_uploader:
            self._log("Facebook uploader tidak tersedia!", "ERROR")
            return
        
        print(f"\n{Fore.YELLOW}Pilih jenis status:")
        print("1. ✍️ Tulis status manual")
        print("2. 🤖 Generate dengan AI")
        print("3. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-3): ").strip()
        
        if choice == "1":
            status_text = input(f"{Fore.CYAN}Tulis status: ").strip()
            if not status_text:
                self._log("Status tidak boleh kosong!", "ERROR")
                return
            
            self._log("Uploading status to Facebook...", "INFO")
            result = self.facebook_uploader.create_facebook_post(content=status_text)
            
            if result.get("success"):
                self._log("Status berhasil dipost!", "SUCCESS")
            else:
                self._log(f"Status gagal: {result.get('message')}", "ERROR")
        
        elif choice == "2":
            if not self.ai_assistant:
                self._log("AI Assistant tidak tersedia!", "ERROR")
                self._log("Buat file .env dengan GEMINI_API_KEY=your_api_key", "INFO")
                return
            
            prompt = input(f"{Fore.CYAN}Prompt untuk AI: ").strip()
            if not prompt:
                self._log("Prompt tidak boleh kosong!", "ERROR")
                return
            
            # Get language preference
            language = self.get_ai_language_preference()
            
            self._log("Generating AI content dengan Gemini 2.0-flash...", "AI")
            
            # Generate text post for Facebook
            ai_post = self.ai_assistant.generate_text_post(prompt, "facebook", language=language)
            
            if ai_post:
                content = ai_post.get('content', prompt)
                
                result = self.facebook_uploader.create_facebook_post(content=content)
                
                if result.get("success"):
                    self._log("AI status berhasil dipost!", "SUCCESS")
                    print(f"\n{Fore.GREEN}📝 Generated Content:")
                    print(f"Title: {ai_post.get('title', 'N/A')}")
                    print(f"Content: {content[:100]}...")
                else:
                    self._log(f"AI status gagal: {result.get('message')}", "ERROR")
            else:
                self._log("AI content generation failed", "ERROR")
        
        elif choice == "3":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _image_media_pipeline(self):
        """Enhanced image/media pipeline dengan file/URL support dan improved AI"""
        print(f"\n{Fore.CYAN}🖼️ IMAGE/MEDIA PIPELINE")
        print("=" * 40)
        
        # Get media source (file atau URL) - support image dan video
        media_path, source_type, media_type = self.get_media_source("PILIH SUMBER MEDIA", allow_images=True)
        
        if not media_path:
            return
        
        self._log(f"✅ Media source: {source_type} - {media_type} - {os.path.basename(media_path)}", "SUCCESS")
        
        # Get caption
        caption = input(f"{Fore.CYAN}Caption (optional): ").strip()
        
        # Optional: AI caption generation dengan language support
        if not caption and self.ai_assistant:
            print(f"\n{Fore.YELLOW}🤖 Generate AI caption?")
            print("1. ✨ Yes, generate AI caption")
            print("2. ⏭️ No, continue without caption")
            
            ai_choice = input(f"\n{Fore.WHITE}Pilihan (1-2): ").strip()
            
            if ai_choice == "1":
                # Get target platform for AI generation
                print(f"\n{Fore.YELLOW}Target platform untuk AI caption:")
                print("1. 📘 Facebook")
                print("2. 📸 Instagram")
                
                platform_choice = input(f"{Fore.WHITE}Pilihan (1-2): ").strip()
                target_platform = "facebook" if platform_choice == "1" else "instagram"
                
                # Get language preference
                language = self.get_ai_language_preference()
                
                if media_type == "video":
                    self._log("⚙️ Analyzing video untuk AI caption...", "AI")
                    analysis = self.ai_assistant.analyze_video_content(media_path, language=language)
                    
                    # Generate caption based on analysis untuk target platform
                    content_topic = f"video about {', '.join(analysis.get('objects', ['content']))}"
                    ai_post = self.ai_assistant.generate_text_post(content_topic, target_platform, language=language)
                    caption = ai_post.get('content', '')
                    
                    if caption:
                        self._log(f"✅ AI caption generated: {caption[:50]}...", "SUCCESS")
                else:
                    # For images, generate generic caption untuk target platform
                    self._log("⚙️ Generating AI caption untuk image...", "AI")
                    ai_post = self.ai_assistant.generate_text_post("amazing image content", target_platform, language=language)
                    caption = ai_post.get('content', '')
                    
                    if caption:
                        self._log(f"✅ AI caption generated: {caption[:50]}...", "SUCCESS")
        
        # Select platforms
        print(f"\n{Fore.YELLOW}Pilih platform:")
        print("1. 📘 Facebook")
        print("2. 📸 Instagram")
        print("3. 🔄 Kedua platform")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-3): ").strip()
        
        if choice == "1":
            # Facebook
            if self.facebook_uploader:
                result = self.facebook_uploader.create_facebook_post(
                    content=caption, 
                    media_path=media_path
                )
                if result.get("success"):
                    self._log("Facebook post berhasil!", "SUCCESS")
                else:
                    self._log(f"Facebook post gagal: {result.get('message')}", "ERROR")
        
        elif choice == "2":
            # Instagram
            if self.instagram_uploader:
                # Auto-detect if video or image untuk Instagram
                is_reel = (media_type == "video")
                
                result = self.instagram_uploader.upload_post(media_path, caption, is_reel)
                if result.get("success"):
                    content_type = "Reel" if is_reel else "Post"
                    self._log(f"Instagram {content_type} berhasil!", "SUCCESS")
                else:
                    self._log(f"Instagram upload gagal: {result.get('message')}", "ERROR")
        
        elif choice == "3":
            # Upload to both platforms
            success_count = 0
            
            # Facebook
            if self.facebook_uploader:
                result = self.facebook_uploader.create_facebook_post(
                    content=caption, 
                    media_path=media_path
                )
                if result.get("success"):
                    self._log("Facebook post berhasil!", "SUCCESS")
                    success_count += 1
                else:
                    self._log(f"Facebook post gagal: {result.get('message')}", "ERROR")
            
            # Instagram
            if self.instagram_uploader:
                is_reel = (media_type == "video")
                
                result = self.instagram_uploader.upload_post(media_path, caption, is_reel)
                if result.get("success"):
                    content_type = "Reel" if is_reel else "Post"
                    self._log(f"Instagram {content_type} berhasil!", "SUCCESS")
                    success_count += 1
                else:
                    self._log(f"Instagram upload gagal: {result.get('message')}", "ERROR")
            
            # Summary
            if success_count == 2:
                self._log("Upload ke kedua platform berhasil!", "SUCCESS")
            elif success_count == 1:
                self._log("Upload berhasil ke 1 dari 2 platform", "WARNING")
            else:
                self._log("Upload gagal ke semua platform", "ERROR")

    def _select_platforms(self) -> List[str]:
        """Select platforms untuk upload"""
        print(f"\n{Fore.YELLOW}📱 PILIH PLATFORM UPLOAD:")
        print("1. 🎵 TikTok")
        print("2. 📘 Facebook (Reels)")
        print("3. 📺 YouTube (Shorts)")
        print("4. 📸 Instagram (Reels)")
        print("5. 🔄 Semua Platform")
        
        choice = input(f"{Fore.WHITE}Pilihan (1-5): ").strip()
        
        if choice == "5":
            return ["tiktok", "facebook", "youtube", "instagram"]
        elif choice == "1":
            return ["tiktok"]
        elif choice == "2":
            return ["facebook"]
        elif choice == "3":
            return ["youtube"]
        elif choice == "4":
            return ["instagram"]
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return []

    def _upload_video_to_platforms(self, video_path: str, platforms: List[str], ai_content: Dict = None):
        """Upload video ke multiple platforms dengan AI content"""
        self._log(f"Uploading video ke {len(platforms)} platform(s)...", "PIPELINE")
        
        results = {}
        
        for platform in platforms:
            self._log(f"Uploading ke {platform.upper()}...", "INFO")
            
            # Get AI-generated content for this platform
            platform_content = ai_content.get(platform, {}) if ai_content else {}
            
            # Use AI content or fallback
            if 'title_options' in platform_content:
                title = platform_content['title_options'][0]  # Use first title option
            else:
                title = platform_content.get('title', f"Amazing Video for {platform.title()}")
            
            if 'caption_suggestion' in platform_content:
                description = platform_content['caption_suggestion']
            else:
                description = platform_content.get('description', f"Check out this amazing content! #{platform} #viral #trending")
            
            try:
                if platform == "tiktok" and self.tiktok_uploader:
                    # Use AI-generated hashtags or default
                    if 'tags' in platform_content:
                        hashtags = " ".join([f"#{tag}" for tag in platform_content['tags'][:5]])
                    else:
                        hashtags = "#fyp #viral #trending"
                    result = self.tiktok_uploader.upload_video(video_path, hashtags)
                
                elif platform == "facebook" and self.facebook_uploader:
                    result = self.facebook_uploader.upload_reels(video_path, description)
                
                elif platform == "youtube" and self.youtube_uploader:
                    if not self.youtube_uploader.initialize_youtube_service():
                        result = {"success": False, "message": "YouTube API initialization failed"}
                    else:
                        result = self.youtube_uploader.upload_shorts(video_path, title, description)
                
                elif platform == "instagram" and self.instagram_uploader:
                    result = self.instagram_uploader.upload_reel(video_path, description)
                
                else:
                    result = {"success": False, "message": f"Platform {platform} tidak tersedia"}
                
                results[platform] = result
                
                if result.get("success"):
                    self._log(f"{platform.upper()} upload berhasil!", "SUCCESS")
                    if "video_url" in result:
                        self._log(f"URL: {result['video_url']}", "INFO")
                else:
                    self._log(f"{platform.upper()} upload gagal: {result.get('message')}", "ERROR")
            
            except Exception as e:
                self._log(f"{platform.upper()} upload error: {str(e)}", "ERROR")
                results[platform] = {"success": False, "message": str(e)}
        
        # Summary
        successful = [p for p, r in results.items() if r.get("success")]
        failed = [p for p, r in results.items() if not r.get("success")]
        
        print(f"\n{Fore.LIGHTBLUE_EX}📊 UPLOAD SUMMARY:")
        print("=" * 40)
        print(f"Successful: {len(successful)}/{len(platforms)}")
        
        if successful:
            print(f"{Fore.GREEN}✅ Berhasil: {', '.join(successful)}")
        
        if failed:
            print(f"{Fore.RED}❌ Gagal: {', '.join(failed)}")
        
        if ai_content:
            print(f"{Fore.LIGHTMAGENTA_EX}🤖 AI Content digunakan untuk optimasi platform")

    def _show_system_status(self):
        """Show system status"""
        print(f"\n{Fore.GREEN}⚙️ SYSTEM STATUS:")
        print("=" * 40)
        
        # Check components
        print(f"Video Downloader: {'✅' if UPLOADERS_AVAILABLE and self.video_downloader else '❌'}")
        print(f"AI Assistant: {'✅' if AI_AVAILABLE and self.ai_assistant else '❌'}")
        print(f"Video Editor: {'✅' if FFMPEG_AVAILABLE and self.video_editor else '❌'}")
        
        # Check uploaders
        print(f"TikTok Uploader: {'✅' if self.tiktok_uploader else '❌'}")
        print(f"Facebook Uploader: {'✅' if self.facebook_uploader else '❌'}")
        print(f"YouTube Uploader: {'✅' if self.youtube_uploader else '❌'}")
        print(f"Instagram Uploader: {'✅' if self.instagram_uploader else '❌'}")
        
        # Check external tools
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            print(f"FFmpeg: {'✅' if result.returncode == 0 else '❌'}")
        except:
            print(f"FFmpeg: ❌")
        
        # Check yt-dlp
        if self.video_downloader and self.video_downloader.ytdlp_path:
            print(f"yt-dlp: ✅")
        else:
            print(f"yt-dlp: ❌")
        
        # Check API keys
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        print(f"Gemini API: {'✅' if gemini_api_key and gemini_api_key != 'your_api_key_here' else '❌'}")
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free / (1024**3)
            print(f"Free disk space: {free_gb:.2f} GB")
        except:
            print(f"Free disk space: Unknown")

    def _system_cleanup(self):
        """System cleanup"""
        print(f"\n{Fore.YELLOW}🧹 SYSTEM CLEANUP:")
        print("1. Cleanup Downloads (>7 days)")
        print("2. Cleanup Temp Files")
        print("3. Cleanup Edited Videos (>7 days)")
        print("4. Cleanup All")
        print("5. Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-5): ").strip()
        
        if choice == "1":
            self._cleanup_downloads()
        elif choice == "2":
            self._cleanup_temp_files()
        elif choice == "3":
            self._cleanup_edited_videos()
        elif choice == "4":
            self._cleanup_downloads()
            self._cleanup_temp_files()
            self._cleanup_edited_videos()
        elif choice == "5":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _cleanup_downloads(self):
        """Cleanup downloads folder"""
        try:
            import time
            cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days
            
            cleaned_files = 0
            freed_space = 0
            
            if self.downloads_dir.exists():
                for file_path in self.downloads_dir.rglob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files += 1
                            freed_space += file_size
                        except Exception as e:
                            self._log(f"Error deleting {file_path}: {e}", "WARNING")
            
            freed_space_mb = freed_space / (1024 * 1024)
            self._log(f"Downloads cleanup: {cleaned_files} files deleted, {freed_space_mb:.2f}MB freed", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error cleaning downloads: {e}", "ERROR")

    def _cleanup_temp_files(self):
        """Cleanup temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
                self._log("Temp files cleaned up", "SUCCESS")
        except Exception as e:
            self._log(f"Error cleaning temp files: {e}", "ERROR")

    def _cleanup_edited_videos(self):
        """Cleanup edited videos"""
        try:
            import time
            cutoff_time = time.time() - (7 * 24 * 60 * 60)  # 7 days
            
            cleaned_files = 0
            freed_space = 0
            
            if self.edited_videos_dir.exists():
                for file_path in self.edited_videos_dir.rglob("*"):
                    if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files += 1
                            freed_space += file_size
                        except Exception as e:
                            self._log(f"Error deleting {file_path}: {e}", "WARNING")
            
            freed_space_mb = freed_space / (1024 * 1024)
            self._log(f"Edited videos cleanup: {cleaned_files} files deleted, {freed_space_mb:.2f}MB freed", "SUCCESS")
            
        except Exception as e:
            self._log(f"Error cleaning edited videos: {e}", "ERROR")

    def run_interactive(self):
        """Run interactive mode"""
        try:
            while True:
                if not self.show_main_menu():
                    break
                
                input(f"\n{Fore.CYAN}Press Enter untuk melanjutkan...")
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
        except Exception as e:
            self._log(f"Error: {str(e)}", "ERROR")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Social Media Uploader")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    uploader = SocialMediaUploader(debug=args.debug)
    uploader.run_interactive()


if __name__ == "__main__":
    main()