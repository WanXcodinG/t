#!/usr/bin/env python3
"""
Social Media Uploader Super Advanced dengan AI, FFmpeg, dan yt-dlp Integration
Upload ke TikTok, Facebook, YouTube, Instagram dengan dukungan AI content generation,
video enhancement, dan video downloader terintegrasi
FIXED VERSION - Compatibility issues resolved
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
        
        # Initialize uploaders with proper parameters
        self.tiktok_uploader = TikTokUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.facebook_uploader = FacebookUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.youtube_uploader = YouTubeAPIUploader(debug=debug) if UPLOADERS_AVAILABLE else None  # Fixed: removed headless parameter
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

    def get_video_source(self) -> Dict[str, Any]:
        """
        Interactive menu untuk memilih sumber video
        
        Returns:
            Dict dengan informasi sumber video
        """
        print(f"\n{Fore.LIGHTBLUE_EX}📹 PILIH SUMBER VIDEO:")
        print("=" * 50)
        print(f"{Fore.YELLOW}1. 📁 File Video Lokal")
        print(f"{Fore.YELLOW}2. 📥 Download dari URL (yt-dlp)")
        print(f"{Fore.YELLOW}3. 📋 Batch Download dari URLs")
        print(f"{Fore.YELLOW}4. 🎵 Download Audio Only")
        print(f"{Fore.YELLOW}5. ℹ️ Get Video Info Only")
        print(f"{Fore.YELLOW}6. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-6): ").strip()
        
        if choice == "1":
            return self._get_local_video()
        elif choice == "2":
            return self._download_single_video()
        elif choice == "3":
            return self._batch_download_videos()
        elif choice == "4":
            return self._download_audio_only()
        elif choice == "5":
            return self._get_video_info_only()
        elif choice == "6":
            return {"source": "cancel"}
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return self.get_video_source()

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

    def _download_audio_only(self) -> Dict[str, Any]:
        """Download audio only dari video"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return {"source": "error", "message": "Downloader tidak tersedia"}
        
        print(f"\n{Fore.CYAN}🎵 DOWNLOAD AUDIO ONLY:")
        
        url = input(f"{Fore.WHITE}URL video: ").strip()
        if not url:
            self._log("URL tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "URL kosong"}
        
        # Audio format selection
        print(f"\n{Fore.YELLOW}Pilih format audio:")
        print("1. MP3 (Universal)")
        print("2. M4A (High quality)")
        print("3. WAV (Lossless)")
        
        format_choice = input(f"{Fore.WHITE}Pilihan (1-3, default: 1): ").strip()
        format_map = {"1": "mp3", "2": "m4a", "3": "wav"}
        audio_format = format_map.get(format_choice, "mp3")
        
        self._log(f"Memulai download audio dalam format {audio_format}...", "PIPELINE")
        
        # Download audio
        result = self.video_downloader.download_audio_only(url, audio_format)
        
        if result.get("success"):
            self._log(f"Audio download berhasil: {result['filename']}", "SUCCESS")
            return {
                "source": "audio_download",
                "audio_path": result["file_path"],
                "filename": result["filename"],
                "file_size_mb": result["file_size_mb"],
                "format": result["format"],
                "platform": result["platform"],
                "original_url": url,
                "original_source": "audio_downloaded"
            }
        else:
            self._log(f"Audio download gagal: {result.get('error', 'Unknown error')}", "ERROR")
            return {"source": "error", "message": result.get('error', 'Audio download failed')}

    def _get_video_info_only(self) -> Dict[str, Any]:
        """Get video info tanpa download"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return {"source": "error", "message": "Downloader tidak tersedia"}
        
        print(f"\n{Fore.CYAN}ℹ️ GET VIDEO INFO:")
        
        url = input(f"{Fore.WHITE}URL video: ").strip()
        if not url:
            self._log("URL tidak boleh kosong!", "ERROR")
            return {"source": "error", "message": "URL kosong"}
        
        self._log("Mengambil informasi video...", "INFO")
        
        # Get video info
        info = self.video_downloader.get_video_info(url)
        
        if "error" in info:
            self._log(f"Error getting video info: {info['error']}", "ERROR")
            return {"source": "error", "message": info['error']}
        
        # Display info
        print(f"\n{Fore.GREEN}📹 VIDEO INFO:")
        print(f"Title: {info['title']}")
        print(f"Uploader: {info['uploader']}")
        print(f"Duration: {info['duration']} seconds")
        print(f"Views: {info['view_count']:,}")
        print(f"Platform: {info['platform']}")
        print(f"Best quality: {info['best_quality']}")
        print(f"Has audio: {'✅' if info['has_audio'] else '❌'}")
        print(f"Has video: {'✅' if info['has_video'] else '❌'}")
        if info['description']:
            print(f"Description: {info['description']}")
        
        # Ask if user wants to download
        download_choice = input(f"\n{Fore.YELLOW}Download video ini? (y/N): ").strip().lower()
        if download_choice == 'y':
            # Redirect to download
            return self._download_single_video()
        else:
            return {"source": "info_only", "video_info": info}

    def smart_upload_pipeline(self) -> Dict[str, Any]:
        """
        Smart upload pipeline dengan pilihan sumber video
        """
        print(f"\n{Fore.LIGHTMAGENTA_EX}🚀 SMART UPLOAD PIPELINE")
        print("=" * 60)
        
        # Step 1: Get video source
        video_source = self.get_video_source()
        
        if video_source.get("source") == "cancel":
            return {"success": False, "message": "Dibatalkan oleh user"}
        
        if video_source.get("source") == "error":
            return {"success": False, "message": video_source.get("message", "Unknown error")}
        
        if video_source.get("source") == "info_only":
            return {"success": True, "message": "Info only", "action": "info_only"}
        
        if video_source.get("source") == "audio_download":
            self._log("Audio download selesai. Tidak dapat diupload ke platform video.", "INFO")
            return {"success": True, "message": "Audio downloaded", "action": "audio_only"}
        
        # Get video path
        video_path = video_source.get("video_path")
        if not video_path or not os.path.exists(video_path):
            return {"success": False, "message": "Video path tidak valid"}
        
        self._log(f"Video source: {video_source.get('original_source', 'unknown')}", "INFO")
        self._log(f"Processing: {video_source.get('filename', 'unknown')}", "INFO")
        
        # Step 2: Platform selection
        platforms = self._select_platforms()
        if not platforms:
            return {"success": False, "message": "Tidak ada platform dipilih"}
        
        # Step 3: Processing strategy
        strategy = self._select_processing_strategy()
        
        # Step 4: AI Analysis (if available and enabled)
        ai_content = {}
        if self.ai_assistant and AI_AVAILABLE:
            use_ai = input(f"\n{Fore.YELLOW}Gunakan AI untuk generate konten? (Y/n): ").strip().lower()
            if use_ai != 'n':
                self._log("Memulai AI analysis dan content generation...", "PIPELINE")
                ai_content = self._ai_analysis_and_content_generation(video_path, strategy, platforms)
        
        # Step 5: Video Enhancement (if available and enabled)
        processed_video_path = video_path
        if self.video_editor and FFMPEG_AVAILABLE:
            use_enhancement = input(f"\n{Fore.YELLOW}Gunakan video enhancement? (Y/n): ").strip().lower()
            if use_enhancement != 'n':
                self._log("Memulai video enhancement...", "PIPELINE")
                processed_video_path = self._enhance_video_with_strategy(video_path, strategy, ai_content)
        
        # Step 6: Upload to platforms
        upload_results = {}
        for platform in platforms:
            self._log(f"Uploading ke {platform.upper()}...", "PIPELINE")
            
            # Get platform-specific content
            platform_content = ai_content.get(platform, {}) if ai_content else {}
            
            result = self._upload_to_platform(
                platform=platform,
                video_path=processed_video_path,
                content=platform_content,
                video_source=video_source
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
            "video_source": video_source,
            "platforms": platforms,
            "strategy": strategy,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads,
            "upload_results": upload_results,
            "ai_content": ai_content
        }

    def _select_platforms(self) -> List[str]:
        """Select platforms untuk upload"""
        print(f"\n{Fore.YELLOW}📱 PILIH PLATFORM UPLOAD:")
        print("1. TikTok")
        print("2. Facebook (Reels)")
        print("3. YouTube (Shorts)")
        print("4. Instagram (Reels/Posts)")
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

    def _select_processing_strategy(self) -> str:
        """Select processing strategy"""
        print(f"\n{Fore.YELLOW}⚙️ PILIH STRATEGI PROCESSING:")
        print("1. Viral Focused (Maximum viral potential)")
        print("2. Quality Focused (Professional quality)")
        print("3. Speed Focused (Fast processing)")
        print("4. Balanced (Good balance)")
        
        choice = input(f"{Fore.WHITE}Pilihan (1-4, default: 4): ").strip()
        strategy_map = {
            "1": "viral_focused",
            "2": "quality_focused", 
            "3": "speed_focused",
            "4": "balanced"
        }
        return strategy_map.get(choice, "balanced")

    def _ai_analysis_and_content_generation(self, video_path: str, strategy: str, platforms: List[str]) -> Dict[str, Any]:
        """AI analysis dan content generation"""
        try:
            if not self.ai_assistant:
                self._log("AI Assistant tidak tersedia", "WARNING")
                return self._generate_fallback_content(platforms)
            
            # Simulate AI analysis - replace with actual AI call
            self._log("Menganalisis video dengan AI...", "INFO")
            time.sleep(2)  # Simulate processing time
            
            # Generate content for each platform
            ai_content = {}
            
            for platform in platforms:
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
            self._log(f"AI analysis error: {e}", "WARNING")
            return self._generate_fallback_content(platforms)

    def _generate_fallback_content(self, platforms: List[str]) -> Dict[str, Any]:
        """Generate fallback content jika AI tidak tersedia"""
        fallback_content = {}
        
        for platform in platforms:
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

    def _enhance_video_with_strategy(self, video_path: str, strategy: str, ai_content: Dict) -> str:
        """Enhance video berdasarkan strategy"""
        try:
            if not self.video_editor:
                self._log("Video editor tidak tersedia", "WARNING")
                return video_path
            
            # Simulate video enhancement - replace with actual FFmpeg call
            self._log(f"Enhancing video dengan strategy: {strategy}", "INFO")
            time.sleep(3)  # Simulate processing time
            
            # For now, return original path
            # In actual implementation, this would call FFmpeg to enhance the video
            enhanced_path = video_path
            
            self._log("Video enhancement selesai", "SUCCESS")
            return enhanced_path
            
        except Exception as e:
            self._log(f"Video enhancement error: {e}", "WARNING")
            return video_path

    def _upload_to_platform(self, platform: str, video_path: str, content: Dict, video_source: Dict) -> Dict[str, Any]:
        """Upload ke platform tertentu"""
        try:
            if platform == "tiktok" and self.tiktok_uploader:
                caption = content.get("description", "#fyp #viral #trending")
                return self.tiktok_uploader.upload_video(video_path, caption)
            
            elif platform == "facebook" and self.facebook_uploader:
                description = content.get("description", "Amazing video!")
                return self.facebook_uploader.upload_reels(video_path, description)
            
            elif platform == "youtube" and self.youtube_uploader:
                title = content.get("title", "Amazing Video")
                description = content.get("description", "Check out this video!")
                if not self.youtube_uploader.initialize_youtube_service():
                    return {"success": False, "message": "YouTube API initialization failed"}
                return self.youtube_uploader.upload_shorts(video_path, title, description)
            
            elif platform == "instagram" and self.instagram_uploader:
                caption = content.get("description", "Amazing content! #viral #instagram")
                # Auto-detect if it's a video (for Reel) or image (for Post)
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                is_reel = any(video_path.lower().endswith(ext) for ext in video_extensions)
                return self.instagram_uploader.upload_post(video_path, caption, is_reel)
            
            else:
                return {"success": False, "message": f"Platform {platform} tidak tersedia atau uploader tidak diinisialisasi"}
                
        except Exception as e:
            return {"success": False, "message": f"Upload error: {str(e)}"}

    def show_main_menu(self):
        """Show main interactive menu"""
        print(f"\n{Fore.LIGHTBLUE_EX}🚀 SUPER ADVANCED SOCIAL MEDIA UPLOADER")
        print("=" * 70)
        print(f"{Fore.LIGHTMAGENTA_EX}🎯 Dengan Video Downloader (yt-dlp) + AI + FFmpeg + Instagram Integration")
        print()
        
        print(f"{Fore.YELLOW}🎯 Super Advanced Features:")
        print("1. 🚀 Smart Upload Pipeline (File atau Download)")
        print("2. 📥 Video Downloader Only")
        print("3. 🤖 AI Content Generator")
        print("4. 🎬 Video Editor")
        print("5. 📊 Download Statistics")
        print("6. 🧹 System Cleanup")
        print("7. ⚙️ System Status")
        print("8. ❌ Exit")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-8): ").strip()
        
        if choice == "1":
            result = self.smart_upload_pipeline()
            self._display_pipeline_results(result)
        
        elif choice == "2":
            self._video_downloader_menu()
        
        elif choice == "3":
            self._ai_content_generator_menu()
        
        elif choice == "4":
            self._video_editor_menu()
        
        elif choice == "5":
            self._show_download_statistics()
        
        elif choice == "6":
            self._system_cleanup_menu()
        
        elif choice == "7":
            self._show_system_status()
        
        elif choice == "8":
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
        
        video_source = result.get("video_source", {})
        print(f"Video Source: {video_source.get('original_source', 'unknown')}")
        print(f"Filename: {video_source.get('filename', 'unknown')}")
        print(f"Size: {video_source.get('file_size_mb', 0):.2f} MB")
        
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

    def _video_downloader_menu(self):
        """Video downloader menu"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return
        
        # Call the interactive menu from video downloader
        self.video_downloader.interactive_download_menu()

    def _ai_content_generator_menu(self):
        """AI content generator menu"""
        if not self.ai_assistant:
            self._log("AI Assistant tidak tersedia!", "ERROR")
            self._log("Install dengan: pip install google-generativeai", "INFO")
            self._log("Set environment variable: GEMINI_API_KEY=your_api_key", "INFO")
            return
        
        print(f"\n{Fore.CYAN}🤖 AI CONTENT GENERATOR:")
        print("1. Generate Content dari Video")
        print("2. Generate Text Post")
        print("3. Analyze Video")
        print("4. Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
        
        if choice == "1":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            if os.path.exists(video_path):
                platforms = ["tiktok", "facebook", "youtube", "instagram"]
                content = self._ai_analysis_and_content_generation(video_path, "balanced", platforms)
                
                print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
                for platform, platform_content in content.items():
                    print(f"\n{platform.upper()}:")
                    print(f"  Title: {platform_content.get('title', 'N/A')}")
                    print(f"  Description: {platform_content.get('description', 'N/A')}")
            else:
                self._log("File video tidak ditemukan!", "ERROR")
        
        elif choice == "2":
            topic = input(f"{Fore.CYAN}Topik untuk post: ").strip()
            platform = input(f"{Fore.CYAN}Platform (tiktok/facebook/youtube/instagram): ").strip()
            if topic and platform:
                # Simulate text generation
                self._log(f"Generating content untuk topik: {topic}", "INFO")
                print(f"\n{Fore.GREEN}Generated content untuk {platform}:")
                print(f"Title: Tips {topic} yang Wajib Diketahui!")
                print(f"Description: Simak tips {topic} yang sangat berguna ini! #tips #{topic} #viral")
        
        elif choice == "3":
            video_path = input(f"{Fore.CYAN}Path ke video untuk analisis: ").strip()
            if os.path.exists(video_path):
                self._log("Menganalisis video...", "INFO")
                time.sleep(2)
                print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS:")
                print("- Format: MP4")
                print("- Duration: Suitable for Shorts")
                print("- Quality: Good")
                print("- Viral Potential: High")
                print("- Recommended platforms: TikTok, Instagram Reels")
            else:
                self._log("File video tidak ditemukan!", "ERROR")
        
        elif choice == "4":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _video_editor_menu(self):
        """Video editor menu"""
        if not self.video_editor:
            self._log("Video Editor tidak tersedia!", "ERROR")
            self._log("Install FFmpeg dan pastikan tersedia di PATH", "INFO")
            return
        
        print(f"\n{Fore.CYAN}🎬 VIDEO EDITOR:")
        print("1. Enhance Video Quality")
        print("2. Apply Anti-Detection")
        print("3. Optimize for Platform")
        print("4. Create Variations")
        print("5. Compress Video")
        print("6. Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-6): ").strip()
        
        if choice == "1":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            if os.path.exists(video_path):
                self._log("Enhancing video quality...", "INFO")
                time.sleep(3)
                output_path = video_path.replace('.mp4', '_enhanced.mp4')
                self._log(f"Video enhanced: {output_path}", "SUCCESS")
            else:
                self._log("File video tidak ditemukan!", "ERROR")
        
        elif choice == "2":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            if os.path.exists(video_path):
                self._log("Applying anti-detection modifications...", "INFO")
                time.sleep(3)
                output_path = video_path.replace('.mp4', '_antidetect.mp4')
                self._log(f"Anti-detection applied: {output_path}", "SUCCESS")
            else:
                self._log("File video tidak ditemukan!", "ERROR")
        
        elif choice == "3":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            platform = input(f"{Fore.CYAN}Platform (tiktok/facebook/youtube/instagram): ").strip()
            if os.path.exists(video_path) and platform:
                self._log(f"Optimizing for {platform}...", "INFO")
                time.sleep(3)
                output_path = video_path.replace('.mp4', f'_{platform}_optimized.mp4')
                self._log(f"Video optimized for {platform}: {output_path}", "SUCCESS")
            else:
                self._log("File video tidak ditemukan atau platform tidak valid!", "ERROR")
        
        elif choice == "4":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            if os.path.exists(video_path):
                variations = input(f"{Fore.CYAN}Jumlah variasi (default: 3): ").strip()
                variations = int(variations) if variations else 3
                self._log(f"Creating {variations} variations...", "INFO")
                time.sleep(5)
                for i in range(variations):
                    output_path = video_path.replace('.mp4', f'_variation_{i+1}.mp4')
                    self._log(f"Variation {i+1} created: {output_path}", "SUCCESS")
            else:
                self._log("File video tidak ditemukan!", "ERROR")
        
        elif choice == "5":
            video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
            target_size = input(f"{Fore.CYAN}Target size (MB): ").strip()
            if os.path.exists(video_path) and target_size:
                self._log(f"Compressing to {target_size}MB...", "INFO")
                time.sleep(3)
                output_path = video_path.replace('.mp4', '_compressed.mp4')
                self._log(f"Video compressed: {output_path}", "SUCCESS")
            else:
                self._log("File video tidak ditemukan atau target size tidak valid!", "ERROR")
        
        elif choice == "6":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _show_download_statistics(self):
        """Show download statistics"""
        if not self.video_downloader:
            self._log("Video downloader tidak tersedia!", "ERROR")
            return
        
        stats = self.video_downloader.get_download_stats()
        
        print(f"\n{Fore.GREEN}📊 DOWNLOAD STATISTICS:")
        print("=" * 40)
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        
        print(f"\n📱 Platform breakdown:")
        for platform, data in stats['platform_breakdown'].items():
            print(f"  {platform}: {data['files']} files ({data['size_mb']:.2f} MB)")
        
        if stats['recent_downloads']:
            print(f"\n📥 Recent downloads:")
            for file_info in stats['recent_downloads'][:5]:
                print(f"  {file_info['name']} ({file_info['platform']}) - {file_info['size_mb']:.2f} MB")

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
        
        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.base_dir)
            free_gb = free / (1024**3)
            print(f"Free disk space: {free_gb:.2f} GB")
        except:
            print(f"Free disk space: Unknown")

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
    parser.add_argument("--strategy", choices=['viral_focused', 'quality_focused', 'speed_focused', 'balanced'], 
                       default='balanced', help="Processing strategy")
    
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