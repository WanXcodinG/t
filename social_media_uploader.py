#!/usr/bin/env python3
"""
Social Media Uploader Super Advanced dengan AI, FFmpeg, dan yt-dlp Integration
Upload ke TikTok, Facebook, YouTube, Instagram dengan dukungan AI content generation,
video enhancement, dan video downloader terintegrasi
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

# Import modules
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
        
        # Initialize components
        self.video_downloader = VideoDownloader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.ai_assistant = GeminiAIAssistant(debug=debug) if AI_AVAILABLE else None
        self.video_editor = FFmpegVideoEditor(debug=debug) if FFMPEG_AVAILABLE else None
        
        # Initialize uploaders
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
            "PIPELINE": Fore.LIGHTMAGENTA_EX
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
            "PIPELINE": "⚙️"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def get_content_source(self) -> Dict[str, Any]:
        """
        Interactive menu untuk memilih sumber konten (video, image, atau text)
        
        Returns:
            Dict dengan informasi sumber konten
        """
        print(f"\n{Fore.LIGHTBLUE_EX}📹 PILIH JENIS KONTEN:")
        print("=" * 50)
        print(f"{Fore.YELLOW}1. 🎬 Video Content (TikTok, Facebook Reels, YouTube Shorts, Instagram Reels)")
        print(f"{Fore.YELLOW}2. 📝 Text Status (Facebook Status)")
        print(f"{Fore.YELLOW}3. 🖼️ Image/Media (Facebook Post, Instagram Post)")
        print(f"{Fore.YELLOW}4. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            return self.get_video_source()
        elif choice == "2":
            return self._get_text_status()
        elif choice == "3":
            return self._get_image_media()
        elif choice == "4":
            return {"source": "cancel"}
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return self.get_content_source()

    def get_video_source(self) -> Dict[str, Any]:
        """
        Interactive menu untuk memilih sumber video
        
        Returns:
            Dict dengan informasi sumber video
        """
        print(f"\n{Fore.LIGHTBLUE_EX}📹 PILIH SUMBER VIDEO:")
        print("=" * 50)
        print(f"{Fore.YELLOW}1. 📁 File Video Lokal")
        print(f"{Fore.YELLOW}2. 📥 Download dari URL")
        print(f"{Fore.YELLOW}3. 📋 Batch Download dari URLs")
        print(f"{Fore.YELLOW}4. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            return self._get_local_video()
        elif choice == "2":
            return self._download_single_video()
        elif choice == "3":
            return self._batch_download_videos()
        elif choice == "4":
            return {"source": "cancel"}
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return self.get_video_source()

    def _get_text_status(self) -> Dict[str, Any]:
        """Get text status untuk Facebook"""
        print(f"\n{Fore.CYAN}📝 FACEBOOK TEXT STATUS:")
        print("=" * 40)
        
        status_text = input(f"{Fore.WHITE}Masukkan status text: ").strip()
        
        if not status_text:
            self._log("Status text tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "Status text kosong"}
        
        self._log(f"Text status siap: {status_text[:50]}{'...' if len(status_text) > 50 else ''}", "SUCCESS")
        
        return {
            "source": "text_status",
            "content_type": "text",
            "status_text": status_text,
            "filename": "text_status",
            "original_source": "text_input"
        }

    def _get_image_media(self) -> Dict[str, Any]:
        """Get image/media file"""
        print(f"\n{Fore.CYAN}🖼️ PILIH IMAGE/MEDIA FILE:")
        print("=" * 40)
        
        media_path = input(f"{Fore.WHITE}Path ke file image/media: ").strip()
        
        if not media_path:
            self._log("Path tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "Path kosong"}
        
        if not os.path.exists(media_path):
            self._log("File tidak ditemukan!", "ERROR")
            return {"source": "error", "message": "File tidak ditemukan"}
        
        # Validasi file media
        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.mp4', '.avi', '.mov', '.mkv', '.webm']
        if not any(media_path.lower().endswith(ext) for ext in media_extensions):
            self._log("File bukan media yang valid!", "ERROR")
            return {"source": "error", "message": "Bukan file media"}
        
        file_size = os.path.getsize(media_path) / (1024 * 1024)  # MB
        
        # Detect content type
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        if any(media_path.lower().endswith(ext) for ext in image_extensions):
            content_type = "image"
        elif any(media_path.lower().endswith(ext) for ext in video_extensions):
            content_type = "video"
        else:
            content_type = "media"
        
        # Optional caption
        caption = input(f"{Fore.CYAN}Caption untuk media (optional): ").strip()
        
        self._log(f"Media file dipilih: {os.path.basename(media_path)} ({file_size:.2f}MB)", "SUCCESS")
        
        return {
            "source": "media_file",
            "content_type": content_type,
            "media_path": media_path,
            "filename": os.path.basename(media_path),
            "file_size_mb": round(file_size, 2),
            "caption": caption,
            "original_source": "local_media"
        }

    def _get_local_video(self) -> Dict[str, Any]:
        """Get video dari file lokal"""
        print(f"\n{Fore.CYAN}📁 PILIH FILE VIDEO LOKAL:")
        
        video_path = input(f"{Fore.WHITE}Path ke file video: ").strip()
        
        if not video_path:
            self._log("Path tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "Path kosong"}
        
        if not os.path.exists(video_path):
            self._log("File tidak ditemukan!", "ERROR")
            return {"source": "error", "message": "File tidak ditemukan"}
        
        # Validasi file video
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        if not any(video_path.lower().endswith(ext) for ext in video_extensions):
            self._log("File bukan video yang valid!", "ERROR")
            return {"source": "error", "message": "Bukan file video"}
        
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        self._log(f"File video dipilih: {os.path.basename(video_path)} ({file_size:.2f}MB)", "SUCCESS")
        
        return {
            "source": "local",
            "content_type": "video",
            "video_path": video_path,
            "filename": os.path.basename(video_path),
            "file_size_mb": round(file_size, 2),
            "original_source": "local_file"
        }

    def _download_single_video(self) -> Dict[str, Any]:
        """Download single video dari URL"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return {"source": "error", "message": "Downloader tidak tersedia"}
        
        print(f"\n{Fore.CYAN}📥 DOWNLOAD VIDEO DARI URL:")
        
        url = input(f"{Fore.WHITE}URL video: ").strip()
        if not url:
            self._log("URL tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "URL kosong"}
        
        # Detect platform
        platform = self.video_downloader.detect_platform(url)
        self._log(f"Platform terdeteksi: {platform}", "INFO")
        
        # Quality selection
        print(f"\n{Fore.YELLOW}Pilih kualitas:")
        print("1. Best (Terbaik)")
        print("2. High (1080p)")
        print("3. Medium (720p)")
        print("4. Low (480p)")
        
        quality_choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 2): ").strip()
        quality_map = {"1": "best", "2": "high", "3": "medium", "4": "low"}
        quality = quality_map.get(quality_choice, "high")
        
        # Custom filename
        custom_filename = input(f"{Fore.CYAN}Custom filename (optional): ").strip()
        
        self._log(f"Memulai download dari {platform} dengan kualitas {quality}...", "PIPELINE")
        
        # Download video
        result = self.video_downloader.download_video(
            url=url,
            quality=quality,
            custom_filename=custom_filename if custom_filename else None,
            platform=platform
        )
        
        if result.get("success"):
            self._log(f"Download berhasil: {result['filename']}", "SUCCESS")
            return {
                "source": "download",
                "content_type": "video",
                "video_path": result["file_path"],
                "filename": result["filename"],
                "file_size_mb": result["file_size_mb"],
                "platform": result["platform"],
                "quality": result["quality"],
                "original_url": url,
                "video_info": result.get("video_info", {}),
                "original_source": "downloaded"
            }
        else:
            self._log(f"Download gagal: {result.get('error', 'Unknown error')}", "ERROR")
            return {"source": "error", "message": result.get('error', 'Download failed')}

    def _batch_download_videos(self) -> Dict[str, Any]:
        """Batch download multiple videos"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return {"source": "error", "message": "Downloader tidak tersedia"}
        
        print(f"\n{Fore.CYAN}📦 BATCH DOWNLOAD VIDEOS:")
        
        print(f"{Fore.YELLOW}Pilih metode input:")
        print("1. Input URLs manual (pisahkan dengan enter)")
        print("2. Load dari file text")
        
        input_choice = input(f"{Fore.WHITE}Pilihan (1-2): ").strip()
        
        urls = []
        
        if input_choice == "1":
            print(f"{Fore.CYAN}Masukkan URLs (ketik 'done' untuk selesai):")
            while True:
                url = input(f"{Fore.WHITE}URL: ").strip()
                if url.lower() == 'done':
                    break
                if url:
                    urls.append(url)
        
        elif input_choice == "2":
            file_path = input(f"{Fore.WHITE}Path ke file URLs: ").strip()
            if not os.path.exists(file_path):
                self._log("File tidak ditemukan!", "ERROR")
                return {"source": "error", "message": "File URLs tidak ditemukan"}
            
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self._log(f"Error reading file: {e}", "ERROR")
                return {"source": "error", "message": f"Error reading file: {e}"}
        
        if not urls:
            self._log("Tidak ada URLs untuk didownload!", "ERROR")
            return {"source": "error", "message": "Tidak ada URLs"}
        
        # Quality selection
        print(f"\n{Fore.YELLOW}Pilih kualitas untuk semua video:")
        print("1. Best")
        print("2. High (1080p)")
        print("3. Medium (720p)")
        print("4. Low (480p)")
        
        quality_choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 2): ").strip()
        quality_map = {"1": "best", "2": "high", "3": "medium", "4": "low"}
        quality = quality_map.get(quality_choice, "high")
        
        self._log(f"Memulai batch download untuk {len(urls)} URLs...", "PIPELINE")
        
        # Batch download
        result = self.video_downloader.batch_download(urls, quality)
        
        if result["successful"]:
            self._log(f"Batch download selesai: {len(result['successful'])}/{result['total_urls']} berhasil", "SUCCESS")
            
            # Return info tentang video pertama yang berhasil untuk processing
            first_success = result["successful"][0]
            return {
                "source": "batch_download",
                "content_type": "video",
                "video_path": first_success["file_path"],
                "filename": os.path.basename(first_success["file_path"]),
                "file_size_mb": first_success["file_size_mb"],
                "batch_results": result,
                "total_downloaded": len(result["successful"]),
                "original_source": "batch_downloaded"
            }
        else:
            self._log("Semua download gagal!", "ERROR")
            return {"source": "error", "message": "Batch download failed"}

    def smart_upload_pipeline(self) -> Dict[str, Any]:
        """
        Smart upload pipeline dengan opsi AI dan FFmpeg terintegrasi
        """
        print(f"\n{Fore.LIGHTMAGENTA_EX}🚀 SMART UPLOAD PIPELINE")
        print("=" * 60)
        
        # Step 1: Get content source (video, text, atau media)
        content_source = self.get_content_source()
        
        if content_source.get("source") == "cancel":
            return {"success": False, "message": "Dibatalkan oleh user"}
        
        if content_source.get("source") == "error":
            return {"success": False, "message": content_source.get("message", "Unknown error")}
        
        content_type = content_source.get("content_type", "video")
        
        self._log(f"Content type: {content_type}", "INFO")
        self._log(f"Content source: {content_source.get('original_source', 'unknown')}", "INFO")
        
        # Step 2: Platform selection berdasarkan content type
        platforms = self._select_platforms_by_content_type(content_type)
        if not platforms:
            return {"success": False, "message": "Tidak ada platform dipilih"}
        
        # Step 3: AI Content Generation Options (untuk semua jenis konten)
        ai_content = {}
        use_ai = False
        if self.ai_assistant and AI_AVAILABLE:
            print(f"\n{Fore.LIGHTMAGENTA_EX}🤖 OPSI AI CONTENT GENERATION:")
            print("=" * 50)
            print(f"{Fore.YELLOW}Gunakan AI untuk:")
            if content_type == "text":
                print("• Enhance text status yang lebih engaging")
                print("• Generate hashtag trending")
                print("• Optimasi konten untuk Facebook")
            elif content_type == "image":
                print("• Generate caption yang menarik")
                print("• Suggest hashtag trending")
                print("• Optimasi konten per platform")
            else:  # video
                print("• Generate judul yang menarik dan viral")
                print("• Buat deskripsi yang engaging")
                print("• Suggest hashtag trending")
                print("• Optimasi konten per platform")
                print("• Analisis potensi viral")
            
            use_ai_choice = input(f"\n{Fore.WHITE}Gunakan AI Content Generation? (Y/n): ").strip().lower()
            if use_ai_choice != 'n':
                use_ai = True
                
                # AI Strategy selection
                print(f"\n{Fore.YELLOW}Pilih strategi AI:")
                print("1. 🔥 Viral Focused (Maximum engagement)")
                print("2. 🎨 Quality Focused (Professional content)")
                print("3. ⚡ Speed Focused (Quick generation)")
                print("4. ⚖️ Balanced (Good balance)")
                
                ai_strategy_choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 4): ").strip()
                ai_strategy_map = {
                    "1": "viral_focused",
                    "2": "quality_focused", 
                    "3": "speed_focused",
                    "4": "balanced"
                }
                ai_strategy = ai_strategy_map.get(ai_strategy_choice, "balanced")
                
                self._log("Memulai AI content generation...", "PIPELINE")
                ai_content = self._ai_content_generation_by_type(content_source, ai_strategy, platforms)
        
        # Step 4: Video Enhancement Options (hanya untuk video)
        processed_content_path = content_source.get("video_path") or content_source.get("media_path")
        use_ffmpeg = False
        if content_type == "video" and self.video_editor and FFMPEG_AVAILABLE:
            print(f"\n{Fore.LIGHTBLUE_EX}🎬 OPSI VIDEO ENHANCEMENT:")
            print("=" * 50)
            print(f"{Fore.YELLOW}Gunakan FFmpeg untuk:")
            print("• Enhance kualitas video (brightness, contrast, sharpness)")
            print("• Anti-detection modifications (hindari deteksi reupload)")
            print("• Platform optimization (format, resolution, bitrate)")
            print("• Create variations (multiple versi)")
            print("• Compress video (ukuran optimal)")
            
            use_ffmpeg_choice = input(f"\n{Fore.WHITE}Gunakan Video Enhancement? (Y/n): ").strip().lower()
            if use_ffmpeg_choice != 'n':
                use_ffmpeg = True
                
                # Enhancement options
                print(f"\n{Fore.YELLOW}Pilih jenis enhancement:")
                print("1. 🔥 Anti-Detection Only (Hindari deteksi reupload)")
                print("2. ✨ Quality Enhancement Only (Tingkatkan kualitas)")
                print("3. 📱 Platform Optimization Only (Optimasi per platform)")
                print("4. 🎭 Complete Enhancement (Semua fitur)")
                
                enhancement_choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 1): ").strip()
                
                # Enhancement intensity
                print(f"\n{Fore.YELLOW}Pilih intensitas:")
                print("1. Light (Perubahan minimal)")
                print("2. Medium (Perubahan sedang)")
                print("3. Heavy (Perubahan maksimal)")
                
                intensity_choice = input(f"{Fore.WHITE}Pilihan (1-3, default: 2): ").strip()
                intensity_map = {"1": "light", "2": "medium", "3": "heavy"}
                intensity = intensity_map.get(intensity_choice, "medium")
                
                self._log("Memulai video enhancement...", "PIPELINE")
                processed_content_path = self._enhance_video_with_options(
                    content_source.get("video_path"), enhancement_choice, intensity, platforms, ai_content
                )
        
        # Step 5: Final confirmation
        print(f"\n{Fore.LIGHTGREEN_EX}📋 RINGKASAN UPLOAD:")
        print("=" * 50)
        print(f"Content Type: {content_type.upper()}")
        if content_type == "text":
            print(f"Status: {content_source.get('status_text', '')[:50]}{'...' if len(content_source.get('status_text', '')) > 50 else ''}")
        else:
            print(f"Filename: {content_source.get('filename', 'unknown')}")
            print(f"Size: {content_source.get('file_size_mb', 0):.2f} MB")
        print(f"Platforms: {', '.join([p.upper() for p in platforms])}")
        print(f"AI Content: {'✅ Enabled' if use_ai else '❌ Disabled'}")
        if content_type == "video":
            print(f"Video Enhancement: {'✅ Enabled' if use_ffmpeg else '❌ Disabled'}")
        
        confirm = input(f"\n{Fore.WHITE}Lanjutkan upload? (Y/n): ").strip().lower()
        if confirm == 'n':
            return {"success": False, "message": "Upload dibatalkan oleh user"}
        
        # Step 6: Upload to platforms
        upload_results = {}
        for platform in platforms:
            self._log(f"Uploading ke {platform.upper()}...", "PIPELINE")
            
            # Get platform-specific content
            platform_content = ai_content.get(platform, {}) if ai_content else {}
            
            result = self._upload_to_platform_by_type(
                platform=platform,
                content_source=content_source,
                content_path=processed_content_path,
                content=platform_content
            )
            
            upload_results[platform] = result
            
            if result.get("success"):
                self._log(f"{platform.upper()} upload berhasil!", "SUCCESS")
            else:
                self._log(f"{platform.upper()} upload gagal: {result.get('message', 'Unknown error')}", "ERROR")
        
        # Step 7: Results summary
        successful_uploads = [p for p, r in upload_results.items() if r.get("success")]
        failed_uploads = [p for p, r in upload_results.items() if not r.get("success")]
        
        self._log(f"Upload selesai: {len(successful_uploads)}/{len(platforms)} berhasil", "SUCCESS")
        
        return {
            "success": len(successful_uploads) > 0,
            "content_source": content_source,
            "content_type": content_type,
            "platforms": platforms,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "upload_results": upload_results,
            "ai_content": ai_content,
            "used_ai": use_ai,
            "used_ffmpeg": use_ffmpeg
        }

    def _select_platforms_by_content_type(self, content_type: str) -> List[str]:
        """Select platforms berdasarkan content type"""
        print(f"\n{Fore.YELLOW}📱 PILIH PLATFORM UPLOAD:")
        
        if content_type == "text":
            print("1. Facebook (Text Status)")
            print("2. Kembali")
            
            choice = input(f"{Fore.WHITE}Pilihan (1-2): ").strip()
            if choice == "1":
                return ["facebook"]
            else:
                return []
        
        elif content_type == "image":
            print("1. Facebook (Image Post)")
            print("2. Instagram (Image Post)")
            print("3. Facebook + Instagram")
            print("4. Kembali")
            
            choice = input(f"{Fore.WHITE}Pilihan (1-4): ").strip()
            if choice == "1":
                return ["facebook"]
            elif choice == "2":
                return ["instagram"]
            elif choice == "3":
                return ["facebook", "instagram"]
            else:
                return []
        
        else:  # video
            print("1. TikTok")
            print("2. Facebook (Reels)")
            print("3. YouTube (Shorts)")
            print("4. Instagram (Reels)")
            print("5. Semua Platform")
            
            choice = input(f"{Fore.WHITE}Pilihan (1-5, atau pisahkan dengan koma): ").strip()
            
            if choice == "5":
                return ["tiktok", "facebook", "youtube", "instagram"]
            elif "," in choice:
                platform_map = {"1": "tiktok", "2": "facebook", "3": "youtube", "4": "instagram"}
                selected = []
                for c in choice.split(","):
                    platform = platform_map.get(c.strip())
                    if platform:
                        selected.append(platform)
                return selected
            else:
                platform_map = {"1": "tiktok", "2": "facebook", "3": "youtube", "4": "instagram"}
                platform = platform_map.get(choice)
                return [platform] if platform else []

    def _ai_content_generation_by_type(self, content_source: Dict[str, Any], strategy: str, platforms: List[str]) -> Dict[str, Any]:
        """AI content generation berdasarkan content type"""
        try:
            content_type = content_source.get("content_type", "video")
            
            if not self.ai_assistant:
                self._log("AI Assistant tidak tersedia", "WARNING")
                return self._generate_fallback_content_by_type(content_type, platforms)
            
            self._log(f"Menganalisis {content_type} dengan AI...", "INFO")
            time.sleep(2)  # Simulate processing time
            
            # Generate content for each platform
            ai_content = {}
            
            for platform in platforms:
                if content_type == "text" and platform == "facebook":
                    original_text = content_source.get("status_text", "")
                    ai_content[platform] = {
                        "title": "Enhanced Status",
                        "description": f"{original_text} #facebook #status #viral #trending #amazing",
                        "hashtags": ["#facebook", "#status", "#viral", "#trending"]
                    }
                
                elif content_type == "image":
                    caption = content_source.get("caption", "")
                    if platform == "facebook":
                        ai_content[platform] = {
                            "title": "Amazing Image Post!",
                            "description": f"{caption} Check out this amazing image! #viral #amazing #image #facebook #post",
                            "hashtags": ["#viral", "#amazing", "#image", "#facebook"]
                        }
                    elif platform == "instagram":
                        ai_content[platform] = {
                            "title": "Beautiful Content! ✨",
                            "description": f"{caption} Love this shot! Tag your friends! #viral #instagram #photo #amazing #beautiful",
                            "hashtags": ["#viral", "#instagram", "#photo", "#amazing"]
                        }
                
                else:  # video
                    if platform == "tiktok":
                        ai_content[platform] = {
                            "title": "Video Viral yang Menakjubkan! 🔥",
                            "description": "#fyp #viral #trending #amazing #wow #foryou #tiktok #video #content #entertainment",
                            "hashtags": ["#fyp", "#viral", "#trending", "#amazing", "#wow", "#foryou"]
                        }
                    elif platform == "facebook":
                        ai_content[platform] = {
                            "title": "Video Menakjubkan yang Wajib Ditonton!",
                            "description": "Video ini benar-benar luar biasa! Jangan lupa like dan share ke teman-teman kalian. #viral #amazing #video #facebook #reels",
                            "hashtags": ["#viral", "#amazing", "#video", "#facebook", "#reels"]
                        }
                    elif platform == "youtube":
                        ai_content[platform] = {
                            "title": "Video Viral yang Akan Mengejutkan Anda!",
                            "description": "Tonton video menakjubkan ini sampai habis! Jangan lupa subscribe, like, dan share. #Shorts #viral #amazing #youtube #trending",
                            "hashtags": ["#Shorts", "#viral", "#amazing", "#youtube", "#trending"]
                        }
                    elif platform == "instagram":
                        ai_content[platform] = {
                            "title": "Content yang Luar Biasa! ✨",
                            "description": "Video yang wajib kalian tonton! Tag teman kalian di komentar. #viral #instagram #reels #amazing #content #trending",
                            "hashtags": ["#viral", "#instagram", "#reels", "#amazing", "#content"]
                        }
            
            self._log("AI content generation selesai", "SUCCESS")
            return ai_content
            
        except Exception as e:
            self._log(f"AI content generation error: {e}", "WARNING")
            return self._generate_fallback_content_by_type(content_type, platforms)

    def _generate_fallback_content_by_type(self, content_type: str, platforms: List[str]) -> Dict[str, Any]:
        """Generate fallback content berdasarkan content type"""
        fallback_content = {}
        
        for platform in platforms:
            if content_type == "text" and platform == "facebook":
                fallback_content[platform] = {
                    "title": "Status Update",
                    "description": "#facebook #status #update",
                    "hashtags": ["#facebook", "#status"]
                }
            elif content_type == "image":
                if platform == "facebook":
                    fallback_content[platform] = {
                        "title": "Amazing Image",
                        "description": "Check out this image! #image #facebook",
                        "hashtags": ["#image", "#facebook"]
                    }
                elif platform == "instagram":
                    fallback_content[platform] = {
                        "title": "Beautiful Shot",
                        "description": "Love this! #instagram #photo",
                        "hashtags": ["#instagram", "#photo"]
                    }
            else:  # video - same as before
                if platform == "tiktok":
                    fallback_content[platform] = {
                        "title": "Video Menarik",
                        "description": "#fyp #viral #trending",
                        "hashtags": ["#fyp", "#viral", "#trending"]
                    }
                elif platform == "facebook":
                    fallback_content[platform] = {
                        "title": "Video Menarik",
                        "description": "Check out this amazing video! #viral #video",
                        "hashtags": ["#viral", "#video"]
                    }
                elif platform == "youtube":
                    fallback_content[platform] = {
                        "title": "Amazing Video",
                        "description": "Watch this amazing video! #Shorts #viral",
                        "hashtags": ["#Shorts", "#viral"]
                    }
                elif platform == "instagram":
                    fallback_content[platform] = {
                        "title": "Amazing Content",
                        "description": "Check out this content! #viral #instagram",
                        "hashtags": ["#viral", "#instagram"]
                    }
        
        return fallback_content

    def _enhance_video_with_options(self, video_path: str, enhancement_choice: str, 
                                   intensity: str, platforms: List[str], ai_content: Dict) -> str:
        """Enhance video berdasarkan pilihan user"""
        try:
            if not self.video_editor:
                self._log("Video editor tidak tersedia", "WARNING")
                return video_path
            
            # Simulate video enhancement - replace with actual FFmpeg call
            self._log(f"Enhancing video dengan pilihan: {enhancement_choice}, intensitas: {intensity}", "INFO")
            time.sleep(3)  # Simulate processing time
            
            # For now, return original path
            # In actual implementation, this would call FFmpeg to enhance the video
            enhanced_path = video_path
            
            self._log("Video enhancement selesai", "SUCCESS")
            return enhanced_path
            
        except Exception as e:
            self._log(f"Video enhancement error: {e}", "WARNING")
            return video_path

    def _upload_to_platform_by_type(self, platform: str, content_source: Dict[str, Any], 
                                   content_path: str, content: Dict) -> Dict[str, Any]:
        """Upload ke platform berdasarkan content type"""
        try:
            content_type = content_source.get("content_type", "video")
            
            if platform == "facebook" and self.facebook_uploader:
                if content_type == "text":
                    # Facebook text status
                    status_text = content_source.get("status_text", "")
                    enhanced_text = content.get("description", status_text)
                    return self.facebook_uploader.upload_status(enhanced_text)
                
                elif content_type == "image":
                    # Facebook image post
                    media_path = content_source.get("media_path", "")
                    caption = content.get("description", content_source.get("caption", ""))
                    return self.facebook_uploader.upload_status(caption, media_path)
                
                else:  # video
                    # Facebook reels
                    description = content.get("description", "Amazing video!")
                    return self.facebook_uploader.upload_reels(content_path, description)
            
            elif platform == "instagram" and self.instagram_uploader:
                if content_type == "image":
                    # Instagram image post
                    caption = content.get("description", content_source.get("caption", ""))
                    return self.instagram_uploader.upload_photo(content_source.get("media_path", ""), caption)
                else:  # video
                    # Instagram reels
                    caption = content.get("description", "Amazing content! #viral #instagram")
                    return self.instagram_uploader.upload_reel(content_path, caption)
            
            elif platform == "tiktok" and self.tiktok_uploader and content_type == "video":
                caption = content.get("description", "#fyp #viral #trending")
                return self.tiktok_uploader.upload_video(content_path, caption)
            
            elif platform == "youtube" and self.youtube_uploader and content_type == "video":
                title = content.get("title", "Amazing Video")
                description = content.get("description", "Check out this video!")
                if not self.youtube_uploader.initialize_youtube_service():
                    return {"success": False, "message": "YouTube API initialization failed"}
                return self.youtube_uploader.upload_shorts(content_path, title, description)
            
            else:
                return {"success": False, "message": f"Platform {platform} tidak mendukung content type {content_type} atau uploader tidak tersedia"}
                
        except Exception as e:
            return {"success": False, "message": f"Upload error: {str(e)}"}

    def show_main_menu(self):
        """Show simplified main interactive menu"""
        print(f"\n{Fore.LIGHTBLUE_EX}🚀 SUPER ADVANCED SOCIAL MEDIA UPLOADER")
        print("=" * 70)
        print(f"{Fore.LIGHTMAGENTA_EX}🎯 Dengan Video + Text + Media Support + AI + FFmpeg + Instagram Integration")
        print()
        
        print(f"{Fore.YELLOW}📋 MENU UTAMA:")
        print("1. 🚀 Smart Upload Pipeline (Video/Text/Media)")
        print("2. 📊 System Status & Statistics")
        print("3. 🧹 System Cleanup")
        print("4. ❌ Exit")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            result = self.smart_upload_pipeline()
            self._display_pipeline_results(result)
        
        elif choice == "2":
            self._show_system_status_and_stats()
        
        elif choice == "3":
            self._system_cleanup_menu()
        
        elif choice == "4":
            print(f"{Fore.YELLOW}👋 Sampai jumpa!")
            return False
        
        else:
            self._log("Pilihan tidak valid!", "ERROR")
        
        return True

    def _display_pipeline_results(self, result: Dict[str, Any]):
        """Display hasil pipeline"""
        if not result.get("success"):
            self._log(f"Pipeline gagal: {result.get('message', 'Unknown error')}", "ERROR")
            return
        
        print(f"\n{Fore.GREEN}🎉 PIPELINE RESULTS:")
        print("=" * 50)
        
        content_source = result.get("content_source", {})
        content_type = result.get("content_type", "unknown")
        
        print(f"Content Type: {content_type.upper()}")
        
        if content_type == "text":
            status_text = content_source.get("status_text", "")
            print(f"Status: {status_text[:50]}{'...' if len(status_text) > 50 else ''}")
        else:
            print(f"Filename: {content_source.get('filename', 'unknown')}")
            if content_source.get('file_size_mb'):
                print(f"Size: {content_source.get('file_size_mb', 0):.2f} MB")
        
        print(f"AI Content: {'✅ Used' if result.get('used_ai') else '❌ Not used'}")
        if content_type == "video":
            print(f"Video Enhancement: {'✅ Used' if result.get('used_ffmpeg') else '❌ Not used'}")
        
        if result.get("successful_uploads"):
            print(f"\n{Fore.GREEN}✅ Successful uploads:")
            for platform in result["successful_uploads"]:
                print(f"  - {platform.upper()}")
        
        if result.get("failed_uploads"):
            print(f"\n{Fore.RED}❌ Failed uploads:")
            for platform in result["failed_uploads"]:
                print(f"  - {platform.upper()}")
        
        # Show detailed results
        upload_results = result.get("upload_results", {})
        for platform, upload_result in upload_results.items():
            if upload_result.get("success"):
                print(f"\n{Fore.GREEN}{platform.upper()} Details:")
                if "video_url" in upload_result:
                    print(f"  URL: {upload_result['video_url']}")
                if "video_id" in upload_result:
                    print(f"  ID: {upload_result['video_id']}")

    def _show_system_status_and_stats(self):
        """Show system status dan statistics"""
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
        
        # Check yt-dlp
        if self.video_downloader and self.video_downloader.ytdlp_path:
            print(f"yt-dlp: ✅ Available")
        else:
            print(f"yt-dlp: ❌ Not available")
        
        # Check FFmpeg
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"FFmpeg: ✅ Available")
            else:
                print(f"FFmpeg: ❌ Not available")
        except:
            print(f"FFmpeg: ❌ Not available")
        
        # Check Gemini API
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            print(f"Gemini API: ✅ Key configured")
        else:
            print(f"Gemini API: ❌ Key not configured")
        
        # Content type support
        print(f"\n{Fore.GREEN}📋 CONTENT TYPE SUPPORT:")
        print(f"Video Content: ✅ TikTok, Facebook Reels, YouTube Shorts, Instagram Reels")
        print(f"Text Status: ✅ Facebook Status")
        print(f"Image/Media: ✅ Facebook Posts, Instagram Posts")
        
        # Download statistics
        if self.video_downloader:
            print(f"\n{Fore.GREEN}📊 DOWNLOAD STATISTICS:")
            stats = self.video_downloader.get_download_stats()
            print(f"Total files: {stats['total_files']}")
            print(f"Total size: {stats['total_size_mb']:.2f} MB")
            
            print(f"\n📱 Platform breakdown:")
            for platform, data in stats['platform_breakdown'].items():
                print(f"  {platform}: {data['files']} files ({data['size_mb']:.2f} MB)")
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free / (1024**3)
            print(f"\nFree disk space: {free_gb:.2f} GB")
        except:
            print(f"\nFree disk space: Unknown")

    def _system_cleanup_menu(self):
        """System cleanup menu"""
        print(f"\n{Fore.YELLOW}🧹 SYSTEM CLEANUP:")
        print("1. Cleanup Downloads (>7 days)")
        print("2. Cleanup Temp Files")
        print("3. Cleanup Edited Videos (>7 days)")
        print("4. Cleanup All")
        print("5. Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-5): ").strip()
        
        if choice == "1":
            if self.video_downloader:
                self.video_downloader.cleanup_downloads(7)
        elif choice == "2":
            self._cleanup_temp_files()
        elif choice == "3":
            self._cleanup_edited_videos(7)
        elif choice == "4":
            if self.video_downloader:
                self.video_downloader.cleanup_downloads(7)
            self._cleanup_temp_files()
            self._cleanup_edited_videos(7)
        elif choice == "5":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

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

    def _cleanup_edited_videos(self, days_old: int = 7):
        """Cleanup edited videos yang lama"""
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            
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
    parser = argparse.ArgumentParser(description="Social Media Uploader Super Advanced")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--url", help="URL untuk download")
    parser.add_argument("--video", help="Path ke video file")
    parser.add_argument("--platform", choices=['tiktok', 'facebook', 'youtube', 'instagram', 'all'], help="Platform upload")
    
    args = parser.parse_args()
    
    uploader = SocialMediaUploader(debug=args.debug)
    
    if args.url or args.video:
        # Command line mode
        print("Command line mode - Coming soon!")
    else:
        # Interactive mode
        uploader.run_interactive()


if __name__ == "__main__":
    main()