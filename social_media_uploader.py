#!/usr/bin/env python3
"""
Social Media Uploader - SIMPLIFIED VERSION
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
        
        # Initialize components
        self.video_downloader = VideoDownloader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.ai_assistant = GeminiAIAssistant(debug=debug) if AI_AVAILABLE else None
        self.video_editor = FFmpegVideoEditor(debug=debug) if FFMPEG_AVAILABLE else None
        
        # Initialize uploaders dengan proper parameters
        self.tiktok_uploader = TikTokUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.facebook_uploader = FacebookUploader(debug=debug) if UPLOADERS_AVAILABLE else None
        self.youtube_uploader = YouTubeAPIUploader(debug=debug) if UPLOADERS_AVAILABLE else None  # Fixed: no headless parameter
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
        """Smart upload pipeline"""
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
        print("1. 🎬 Video Content (TikTok, Facebook Reels, YouTube Shorts, Instagram Reels)")
        print("2. 📝 Text Status (Facebook Status)")
        print("3. 🖼️ Image/Media (Facebook Post, Instagram Post)")
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
        """Video content upload pipeline"""
        print(f"\n{Fore.CYAN}🎬 VIDEO CONTENT PIPELINE")
        print("=" * 40)
        
        # Get video source
        print(f"\n{Fore.YELLOW}Pilih sumber video:")
        print("1. 📁 File video lokal")
        print("2. 📥 Download dari URL")
        print("3. ❌ Kembali")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-3): ").strip()
        
        video_path = None
        
        if choice == "1":
            video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
            if not os.path.exists(video_path):
                self._log("File video tidak ditemukan!", "ERROR")
                return
        elif choice == "2":
            if not self.video_downloader:
                self._log("Video downloader tidak tersedia!", "ERROR")
                return
            
            url = input(f"{Fore.CYAN}URL video: ").strip()
            if not url:
                self._log("URL tidak boleh kosong!", "ERROR")
                return
            
            self._log("Downloading video...", "INFO")
            result = self.video_downloader.download_video(url, quality="high")
            
            if result.get("success"):
                video_path = result["file_path"]
                self._log(f"Video downloaded: {result['filename']}", "SUCCESS")
            else:
                self._log(f"Download failed: {result.get('error')}", "ERROR")
                return
        elif choice == "3":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")
            return
        
        if not video_path:
            self._log("Video path tidak valid!", "ERROR")
            return
        
        # Select platforms
        platforms = self._select_platforms()
        if not platforms:
            return
        
        # Upload to selected platforms
        self._upload_video_to_platforms(video_path, platforms)

    def _text_status_pipeline(self):
        """Text status pipeline"""
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
                self._log("Set GEMINI_API_KEY environment variable", "INFO")
                return
            
            prompt = input(f"{Fore.CYAN}Prompt untuk AI: ").strip()
            if not prompt:
                self._log("Prompt tidak boleh kosong!", "ERROR")
                return
            
            self._log("Generating AI content...", "INFO")
            result = self.facebook_uploader.create_facebook_post(
                use_ai=True, 
                ai_prompt=prompt, 
                content_type="status"
            )
            
            if result.get("success"):
                self._log("AI status berhasil dipost!", "SUCCESS")
            else:
                self._log(f"AI status gagal: {result.get('message')}", "ERROR")
        
        elif choice == "3":
            return
        else:
            self._log("Pilihan tidak valid!", "ERROR")

    def _image_media_pipeline(self):
        """Image/media pipeline"""
        print(f"\n{Fore.CYAN}🖼️ IMAGE/MEDIA PIPELINE")
        print("=" * 40)
        
        media_path = input(f"{Fore.CYAN}Path ke file media: ").strip()
        if not os.path.exists(media_path):
            self._log("File media tidak ditemukan!", "ERROR")
            return
        
        caption = input(f"{Fore.CYAN}Caption (optional): ").strip()
        
        # Select platforms
        print(f"\n{Fore.YELLOW}Pilih platform:")
        print("1. 📘 Facebook")
        print("2. 📸 Instagram")
        print("3. 🔄 Kedua platform")
        
        choice = input(f"\n{Fore.WHITE}Pilihan (1-3): ").strip()
        
        if choice == "1":
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
            if self.instagram_uploader:
                # Auto-detect if video or image
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                is_reel = any(media_path.lower().endswith(ext) for ext in video_extensions)
                
                result = self.instagram_uploader.upload_post(media_path, caption, is_reel)
                if result.get("success"):
                    content_type = "Reel" if is_reel else "Post"
                    self._log(f"Instagram {content_type} berhasil!", "SUCCESS")
                else:
                    self._log(f"Instagram upload gagal: {result.get('message')}", "ERROR")
        
        elif choice == "3":
            # Upload to both platforms
            if self.facebook_uploader:
                result = self.facebook_uploader.create_facebook_post(
                    content=caption, 
                    media_path=media_path
                )
                if result.get("success"):
                    self._log("Facebook post berhasil!", "SUCCESS")
                else:
                    self._log(f"Facebook post gagal: {result.get('message')}", "ERROR")
            
            if self.instagram_uploader:
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                is_reel = any(media_path.lower().endswith(ext) for ext in video_extensions)
                
                result = self.instagram_uploader.upload_post(media_path, caption, is_reel)
                if result.get("success"):
                    content_type = "Reel" if is_reel else "Post"
                    self._log(f"Instagram {content_type} berhasil!", "SUCCESS")
                else:
                    self._log(f"Instagram upload gagal: {result.get('message')}", "ERROR")

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

    def _upload_video_to_platforms(self, video_path: str, platforms: List[str]):
        """Upload video ke multiple platforms"""
        self._log(f"Uploading video ke {len(platforms)} platform(s)...", "PIPELINE")
        
        results = {}
        
        for platform in platforms:
            self._log(f"Uploading ke {platform.upper()}...", "INFO")
            
            try:
                if platform == "tiktok" and self.tiktok_uploader:
                    result = self.tiktok_uploader.upload_video(video_path, "#fyp #viral #trending")
                
                elif platform == "facebook" and self.facebook_uploader:
                    result = self.facebook_uploader.upload_reels(video_path, "Amazing video! #viral")
                
                elif platform == "youtube" and self.youtube_uploader:
                    if not self.youtube_uploader.initialize_youtube_service():
                        result = {"success": False, "message": "YouTube API initialization failed"}
                    else:
                        result = self.youtube_uploader.upload_shorts(video_path, "Amazing Video", "Check out this video! #Shorts")
                
                elif platform == "instagram" and self.instagram_uploader:
                    result = self.instagram_uploader.upload_reel(video_path, "Amazing content! #viral #instagram")
                
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
        
        # Check API keys
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        print(f"Gemini API: {'✅' if gemini_api_key else '❌'}")
        
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