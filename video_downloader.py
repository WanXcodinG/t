#!/usr/bin/env python3
"""
Video Downloader menggunakan yt-dlp
Download video dari berbagai platform sosial media
Terintegrasi dengan AI Assistant dan FFmpeg Video Editor
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
import glob
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

class VideoDownloader:
    def __init__(self, debug: bool = False):
        """
        Initialize Video Downloader
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.downloads_dir = self.base_dir / "downloads"
        self.downloads_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for different platforms
        self.platform_dirs = {
            'youtube': self.downloads_dir / "youtube",
            'tiktok': self.downloads_dir / "tiktok", 
            'facebook': self.downloads_dir / "facebook",
            'instagram': self.downloads_dir / "instagram",
            'twitter': self.downloads_dir / "twitter",
            'general': self.downloads_dir / "general"
        }
        
        for platform_dir in self.platform_dirs.values():
            platform_dir.mkdir(exist_ok=True)
        
        # Check yt-dlp installation
        self.ytdlp_path = self._find_ytdlp()
        if not self.ytdlp_path:
            self._log("yt-dlp tidak ditemukan! Install dengan: pip install yt-dlp", "ERROR")
        
        # Platform detection patterns
        self.platform_patterns = {
            'youtube': [
                r'youtube\.com',
                r'youtu\.be',
                r'youtube-nocookie\.com'
            ],
            'tiktok': [
                r'tiktok\.com',
                r'vm\.tiktok\.com',
                r'vt\.tiktok\.com'
            ],
            'facebook': [
                r'facebook\.com',
                r'fb\.watch',
                r'fb\.com'
            ],
            'instagram': [
                r'instagram\.com',
                r'instagr\.am'
            ],
            'twitter': [
                r'twitter\.com',
                r't\.co',
                r'x\.com'
            ]
        }
        
        # Quality presets with better Facebook support
        self.quality_presets = {
            'best': 'best[ext=mp4]/best',
            'high': 'best[height<=1080][ext=mp4]/best[height<=1080]/best',
            'medium': 'best[height<=720][ext=mp4]/best[height<=720]/best',
            'low': 'best[height<=480][ext=mp4]/best[height<=480]/best',
            'audio_only': 'bestaudio[ext=m4a]/bestaudio'
        }
        
        # Platform-specific quality presets
        self.platform_quality_presets = {
            'facebook': {
                'best': 'best/worst',
                'high': 'best[height<=1080]/best/worst',
                'medium': 'best[height<=720]/best/worst',
                'low': 'best[height<=480]/best/worst'
            },
            'instagram': {
                'best': 'best/worst',
                'high': 'best[height<=1080]/best/worst',
                'medium': 'best[height<=720]/best/worst',
                'low': 'best[height<=480]/best/worst'
            }
        }

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA,
            "DOWNLOAD": Fore.LIGHTBLUE_EX
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
            "DOWNLOAD": "📥"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def _find_ytdlp(self) -> Optional[str]:
        """Cari yt-dlp di system"""
        import shutil
        
        # Check if yt-dlp is available
        ytdlp_path = shutil.which('yt-dlp')
        if ytdlp_path:
            self._log(f"yt-dlp ditemukan: {ytdlp_path}", "SUCCESS")
            return ytdlp_path
        
        # Try python -m yt_dlp
        try:
            result = subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self._log("yt-dlp tersedia via python module", "SUCCESS")
                return f"{sys.executable} -m yt_dlp"
        except:
            pass
        
        self._log("yt-dlp tidak ditemukan", "ERROR")
        return None

    def detect_platform(self, url: str) -> str:
        """Deteksi platform dari URL"""
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        return 'general'

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get informasi video tanpa download"""
        if not self.ytdlp_path:
            return {"error": "yt-dlp not available"}
        
        self._log("Mengambil informasi video...", "DOWNLOAD")
        
        try:
            # Build command untuk get info
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split() + ['--dump-json', '--no-download', url]
            else:
                cmd = [self.ytdlp_path, '--dump-json', '--no-download', url]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                # Extract relevant information
                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'extractor': info.get('extractor', 'unknown'),
                    'platform': self.detect_platform(url),
                    'formats_available': len(info.get('formats', [])),
                    'has_audio': any(f.get('acodec') != 'none' for f in info.get('formats', [])),
                    'has_video': any(f.get('vcodec') != 'none' for f in info.get('formats', [])),
                    'best_quality': self._get_best_quality(info.get('formats', [])),
                    'id': info.get('id', 'unknown')
                }
                
                self._log("Informasi video berhasil diambil", "SUCCESS")
                return video_info
            else:
                error_msg = result.stderr or "Unknown error"
                self._log(f"Error getting video info: {error_msg}", "ERROR")
                return {"error": error_msg}
                
        except subprocess.TimeoutExpired:
            self._log("Timeout getting video info", "ERROR")
            return {"error": "Timeout"}
        except json.JSONDecodeError:
            self._log("Error parsing video info", "ERROR")
            return {"error": "Invalid response"}
        except Exception as e:
            self._log(f"Error getting video info: {e}", "ERROR")
            return {"error": str(e)}

    def _get_best_quality(self, formats: List[Dict]) -> str:
        """Get best quality available"""
        if not formats:
            return "unknown"
        
        # Find highest resolution
        max_height = 0
        for fmt in formats:
            height = fmt.get('height', 0)
            if height and height > max_height:
                max_height = height
        
        if max_height >= 1080:
            return "1080p+"
        elif max_height >= 720:
            return "720p"
        elif max_height >= 480:
            return "480p"
        else:
            return "low"

    def _find_downloaded_files(self, output_dir: Path, base_filename: str = None, video_id: str = None) -> List[Path]:
        """Find downloaded files dengan berbagai pattern"""
        downloaded_files = []
        
        # Video extensions to look for
        video_extensions = ['.mp4', '.mkv', '.webm', '.m4a', '.mp3', '.flv', '.avi', '.mov']
        
        if self.debug:
            self._log(f"Looking for files in: {output_dir}", "DEBUG")
            self._log(f"Base filename: {base_filename}", "DEBUG")
            self._log(f"Video ID: {video_id}", "DEBUG")
        
        # Method 1: Look for files with base filename
        if base_filename:
            for ext in video_extensions:
                pattern = base_filename.replace('.%(ext)s', ext)
                matching_files = list(output_dir.glob(Path(pattern).name))
                downloaded_files.extend(matching_files)
                
                if self.debug and matching_files:
                    self._log(f"Found files with pattern {pattern}: {[f.name for f in matching_files]}", "DEBUG")
        
        # Method 2: Look for files with video ID
        if video_id and video_id != 'unknown':
            for ext in video_extensions:
                pattern = f"*{video_id}*{ext}"
                matching_files = list(output_dir.glob(pattern))
                downloaded_files.extend(matching_files)
                
                if self.debug and matching_files:
                    self._log(f"Found files with ID pattern {pattern}: {[f.name for f in matching_files]}", "DEBUG")
        
        # Method 3: Look for any recent video files (last 5 minutes)
        import time
        current_time = time.time()
        recent_threshold = current_time - 300  # 5 minutes
        
        for ext in video_extensions:
            pattern = f"*{ext}"
            all_files = list(output_dir.glob(pattern))
            recent_files = [f for f in all_files if f.stat().st_mtime > recent_threshold]
            downloaded_files.extend(recent_files)
            
            if self.debug and recent_files:
                self._log(f"Found recent files with pattern {pattern}: {[f.name for f in recent_files]}", "DEBUG")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in downloaded_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        
        if self.debug:
            self._log(f"Total unique files found: {len(unique_files)}", "DEBUG")
            for f in unique_files:
                self._log(f"  - {f.name} ({f.stat().st_size / (1024*1024):.2f}MB)", "DEBUG")
        
        return unique_files

    def get_available_formats(self, url: str) -> Dict[str, Any]:
        """Get semua format yang tersedia untuk URL"""
        if not self.ytdlp_path:
            return {"error": "yt-dlp not available"}
        
        self._log("Mengambil format yang tersedia...", "DOWNLOAD")
        
        try:
            # Build command
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split() + ['--list-formats', url]
            else:
                cmd = [self.ytdlp_path, '--list-formats', url]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "formats_list": result.stdout,
                    "platform": self.detect_platform(url)
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download_video(self, url: str, quality: str = 'high', 
                      custom_filename: str = None, platform: str = None) -> Dict[str, Any]:
        """
        Download video dari URL
        
        Args:
            url: URL video
            quality: Quality preset (best/high/medium/low/audio_only)
            custom_filename: Custom filename (optional)
            platform: Force platform detection (optional)
            
        Returns:
            Dict dengan status download dan path file
        """
        if not self.ytdlp_path:
            return {"success": False, "error": "yt-dlp not available"}
        
        # Detect platform
        if not platform:
            platform = self.detect_platform(url)
        
        output_dir = self.platform_dirs.get(platform, self.platform_dirs['general'])
        
        self._log(f"Downloading dari {platform} dengan quality {quality}...", "DOWNLOAD")
        
        try:
            # Get video info first
            info = self.get_video_info(url)
            if "error" in info:
                # If info fails, try to continue with download anyway
                self._log(f"Warning: Could not get video info: {info['error']}", "WARNING")
                info = {"title": "video", "id": "unknown"}
            
            video_id = info.get('id', 'unknown')
            
            # Build filename
            if custom_filename:
                filename_template = f"{custom_filename}.%(ext)s"
            else:
                # Safe filename dari title
                safe_title = re.sub(r'[^\w\s-]', '', info.get('title', 'video')).strip()
                safe_title = re.sub(r'[-\s]+', '-', safe_title)[:50]
                filename_template = f"{safe_title}_%(id)s.%(ext)s"
            
            output_template = str(output_dir / filename_template)
            
            # Get quality format based on platform
            if platform in self.platform_quality_presets:
                format_selector = self.platform_quality_presets[platform].get(quality, 
                    self.platform_quality_presets[platform]['best'])
            else:
                format_selector = self.quality_presets.get(quality, self.quality_presets['high'])
            
            # Build command
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split()
            else:
                cmd = [self.ytdlp_path]
            
            # Add options
            cmd.extend([
                '--format', format_selector,
                '--output', output_template,
                '--no-playlist',  # Download single video only
                '--write-info-json',  # Save metadata
                '--write-thumbnail',  # Save thumbnail
                '--ignore-errors',  # Continue on errors
                url
            ])
            
            # Add additional options based on platform
            if platform == 'tiktok':
                cmd.extend(['--add-header', 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'])
            elif platform == 'facebook':
                cmd.extend([
                    '--add-header', 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    '--extractor-args', 'facebook:tab_type=videos'
                ])
            elif platform == 'instagram':
                cmd.extend(['--cookies-from-browser', 'chrome'])  # May need login
            
            self._log(f"Starting download: {info.get('title', 'Unknown')}", "DOWNLOAD")
            
            if self.debug:
                self._log(f"Command: {' '.join(cmd)}", "DEBUG")
                self._log(f"Output template: {output_template}", "DEBUG")
            
            # Run download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if self.debug:
                self._log(f"Return code: {result.returncode}", "DEBUG")
                if result.stdout:
                    self._log(f"Stdout: {result.stdout[:500]}...", "DEBUG")
                if result.stderr:
                    self._log(f"Stderr: {result.stderr[:500]}...", "DEBUG")
            
            if result.returncode == 0:
                # Find downloaded file dengan improved detection
                downloaded_files = self._find_downloaded_files(output_dir, filename_template, video_id)
                
                if downloaded_files:
                    main_file = max(downloaded_files, key=lambda x: x.stat().st_size)
                    file_size = main_file.stat().st_size / (1024 * 1024)  # MB
                    
                    self._log(f"Download berhasil: {main_file.name} ({file_size:.2f}MB)", "SUCCESS")
                    
                    return {
                        "success": True,
                        "file_path": str(main_file),
                        "filename": main_file.name,
                        "file_size_mb": round(file_size, 2),
                        "platform": platform,
                        "quality": quality,
                        "video_info": info,
                        "output_dir": str(output_dir)
                    }
                else:
                    # List all files in directory for debugging
                    if self.debug:
                        all_files = list(output_dir.glob("*"))
                        self._log(f"All files in output dir: {[f.name for f in all_files]}", "DEBUG")
                    
                    return {"success": False, "error": "Downloaded file not found"}
            else:
                error_msg = result.stderr or "Download failed"
                self._log(f"Download gagal: {error_msg}", "ERROR")
                
                # Try with fallback format for Facebook/Instagram
                if platform in ['facebook', 'instagram'] and 'Requested format is not available' in error_msg:
                    self._log("Mencoba dengan format fallback...", "WARNING")
                    return self._download_with_fallback(url, output_template, platform, info)
                
                return {"success": False, "error": error_msg}
                
        except subprocess.TimeoutExpired:
            self._log("Download timeout", "ERROR")
            return {"success": False, "error": "Download timeout"}
        except Exception as e:
            self._log(f"Download error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def _download_with_fallback(self, url: str, output_template: str, platform: str, info: Dict) -> Dict[str, Any]:
        """Download dengan format fallback untuk Facebook/Instagram"""
        try:
            # Build fallback command dengan format paling sederhana
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split()
            else:
                cmd = [self.ytdlp_path]
            
            # Use simplest format selector
            cmd.extend([
                '--format', 'worst/best',  # Try worst quality first, then best
                '--output', output_template,
                '--no-playlist',
                '--ignore-errors',
                url
            ])
            
            if platform == 'facebook':
                cmd.extend([
                    '--add-header', 'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ])
            
            self._log("Trying fallback download with worst/best format...", "DOWNLOAD")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find downloaded file
                output_dir = Path(output_template).parent
                video_id = info.get('id', 'unknown')
                downloaded_files = self._find_downloaded_files(output_dir, output_template, video_id)
                
                if downloaded_files:
                    main_file = max(downloaded_files, key=lambda x: x.stat().st_size)
                    file_size = main_file.stat().st_size / (1024 * 1024)  # MB
                    
                    self._log(f"Fallback download berhasil: {main_file.name} ({file_size:.2f}MB)", "SUCCESS")
                    
                    return {
                        "success": True,
                        "file_path": str(main_file),
                        "filename": main_file.name,
                        "file_size_mb": round(file_size, 2),
                        "platform": platform,
                        "quality": "fallback",
                        "video_info": info,
                        "output_dir": str(output_dir)
                    }
            
            return {"success": False, "error": "Fallback download also failed"}
            
        except Exception as e:
            return {"success": False, "error": f"Fallback download error: {str(e)}"}

    def download_playlist(self, url: str, quality: str = 'high', 
                         max_downloads: int = 10) -> Dict[str, Any]:
        """Download playlist atau multiple videos"""
        if not self.ytdlp_path:
            return {"success": False, "error": "yt-dlp not available"}
        
        platform = self.detect_platform(url)
        output_dir = self.platform_dirs.get(platform, self.platform_dirs['general'])
        
        self._log(f"Downloading playlist dari {platform} (max {max_downloads} videos)...", "DOWNLOAD")
        
        try:
            # Build command
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split()
            else:
                cmd = [self.ytdlp_path]
            
            # Get quality format
            if platform in self.platform_quality_presets:
                format_selector = self.platform_quality_presets[platform].get(quality, 
                    self.platform_quality_presets[platform]['best'])
            else:
                format_selector = self.quality_presets.get(quality, self.quality_presets['high'])
            
            cmd.extend([
                '--format', format_selector,
                '--output', str(output_dir / '%(uploader)s_%(title)s_%(id)s.%(ext)s'),
                '--playlist-end', str(max_downloads),
                '--write-info-json',
                '--ignore-errors',  # Continue on errors
                url
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Count downloaded files
            downloaded_files = []
            for ext in ['.mp4', '.mkv', '.webm', '.m4a', '.mp3', '.flv']:
                downloaded_files.extend(output_dir.glob(f"*{ext}"))
            
            if downloaded_files:
                total_size = sum(f.stat().st_size for f in downloaded_files) / (1024 * 1024)
                
                self._log(f"Playlist download selesai: {len(downloaded_files)} files ({total_size:.2f}MB)", "SUCCESS")
                
                return {
                    "success": True,
                    "files_downloaded": len(downloaded_files),
                    "total_size_mb": round(total_size, 2),
                    "files": [str(f) for f in downloaded_files],
                    "platform": platform,
                    "output_dir": str(output_dir)
                }
            else:
                return {"success": False, "error": "No files downloaded"}
                
        except subprocess.TimeoutExpired:
            self._log("Playlist download timeout", "ERROR")
            return {"success": False, "error": "Download timeout"}
        except Exception as e:
            self._log(f"Playlist download error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def download_audio_only(self, url: str, format: str = 'm4a') -> Dict[str, Any]:
        """Download audio only dari video"""
        if not self.ytdlp_path:
            return {"success": False, "error": "yt-dlp not available"}
        
        platform = self.detect_platform(url)
        output_dir = self.platform_dirs.get(platform, self.platform_dirs['general'])
        
        self._log(f"Downloading audio only dari {platform}...", "DOWNLOAD")
        
        try:
            # Build command
            if self.ytdlp_path.startswith(sys.executable):
                cmd = self.ytdlp_path.split()
            else:
                cmd = [self.ytdlp_path]
            
            cmd.extend([
                '--extract-audio',
                '--audio-format', format,
                '--audio-quality', '0',  # Best quality
                '--output', str(output_dir / '%(title)s_%(id)s.%(ext)s'),
                '--write-info-json',
                url
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                # Find downloaded audio file
                audio_files = list(output_dir.glob(f"*.{format}"))
                if audio_files:
                    audio_file = max(audio_files, key=lambda x: x.stat().st_mtime)
                    file_size = audio_file.stat().st_size / (1024 * 1024)
                    
                    self._log(f"Audio download berhasil: {audio_file.name} ({file_size:.2f}MB)", "SUCCESS")
                    
                    return {
                        "success": True,
                        "file_path": str(audio_file),
                        "filename": audio_file.name,
                        "file_size_mb": round(file_size, 2),
                        "format": format,
                        "platform": platform
                    }
                else:
                    return {"success": False, "error": "Audio file not found"}
            else:
                error_msg = result.stderr or "Audio download failed"
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self._log(f"Audio download error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def batch_download(self, urls: List[str], quality: str = 'high') -> Dict[str, Any]:
        """Download multiple URLs dalam batch"""
        self._log(f"Starting batch download untuk {len(urls)} URLs...", "DOWNLOAD")
        
        results = {
            "total_urls": len(urls),
            "successful": [],
            "failed": [],
            "total_size_mb": 0
        }
        
        for i, url in enumerate(urls, 1):
            self._log(f"Processing URL {i}/{len(urls)}: {url[:50]}...", "DOWNLOAD")
            
            result = self.download_video(url, quality)
            
            if result.get("success"):
                results["successful"].append({
                    "url": url,
                    "file_path": result["file_path"],
                    "file_size_mb": result["file_size_mb"]
                })
                results["total_size_mb"] += result["file_size_mb"]
            else:
                results["failed"].append({
                    "url": url,
                    "error": result.get("error", "Unknown error")
                })
        
        self._log(f"Batch download selesai: {len(results['successful'])}/{len(urls)} berhasil", "SUCCESS")
        return results

    def cleanup_downloads(self, days_old: int = 7):
        """Cleanup download files yang lama"""
        self._log(f"Cleaning up downloads older than {days_old} days...", "INFO")
        
        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        cleaned_files = 0
        freed_space = 0
        
        for platform_dir in self.platform_dirs.values():
            for file_path in platform_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files += 1
                        freed_space += file_size
                    except Exception as e:
                        self._log(f"Error deleting {file_path}: {e}", "WARNING")
        
        freed_space_mb = freed_space / (1024 * 1024)
        self._log(f"Cleanup selesai: {cleaned_files} files deleted, {freed_space_mb:.2f}MB freed", "SUCCESS")

    def get_download_stats(self) -> Dict[str, Any]:
        """Get statistik download"""
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "platform_breakdown": {},
            "recent_downloads": []
        }
        
        for platform, platform_dir in self.platform_dirs.items():
            platform_files = []
            platform_size = 0
            
            for file_path in platform_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.mp4', '.mkv', '.webm', '.m4a', '.mp3', '.flv']:
                    file_size = file_path.stat().st_size
                    platform_files.append({
                        "name": file_path.name,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified": file_path.stat().st_mtime
                    })
                    platform_size += file_size
            
            stats["platform_breakdown"][platform] = {
                "files": len(platform_files),
                "size_mb": round(platform_size / (1024 * 1024), 2)
            }
            
            stats["total_files"] += len(platform_files)
            stats["total_size_mb"] += platform_size / (1024 * 1024)
            
            # Add recent files
            recent_files = sorted(platform_files, key=lambda x: x["modified"], reverse=True)[:3]
            for file_info in recent_files:
                file_info["platform"] = platform
                stats["recent_downloads"].append(file_info)
        
        # Sort recent downloads
        stats["recent_downloads"] = sorted(stats["recent_downloads"], 
                                         key=lambda x: x["modified"], reverse=True)[:10]
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        return stats

    def interactive_download_menu(self):
        """Interactive menu untuk download"""
        print(f"\n{Fore.BLUE}📥 Video Downloader dengan yt-dlp")
        print("=" * 50)
        
        if not self.ytdlp_path:
            print(f"{Fore.RED}❌ yt-dlp tidak tersedia!")
            print(f"{Fore.YELLOW}Install dengan: pip install yt-dlp")
            return
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 📥 Download Video")
            print("2. 🎵 Download Audio Only")
            print("3. 📋 Download Playlist")
            print("4. ℹ️ Get Video Info")
            print("5. 📊 List Available Formats")
            print("6. 📦 Batch Download")
            print("7. 📊 Download Statistics")
            print("8. 🧹 Cleanup Old Files")
            print("9. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-9): ").strip()
            
            if choice == "1":
                self._interactive_single_download()
            elif choice == "2":
                self._interactive_audio_download()
            elif choice == "3":
                self._interactive_playlist_download()
            elif choice == "4":
                self._interactive_video_info()
            elif choice == "5":
                self._interactive_list_formats()
            elif choice == "6":
                self._interactive_batch_download()
            elif choice == "7":
                self._show_download_statistics()
            elif choice == "8":
                self._interactive_cleanup()
            elif choice == "9":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")

    def _interactive_single_download(self):
        """Interactive single download"""
        url = input(f"{Fore.CYAN}URL video: ").strip()
        if not url:
            print(f"{Fore.RED}❌ URL tidak boleh kosong!")
            return
        
        quality = input(f"{Fore.CYAN}Quality (best/high/medium/low): ").strip() or "high"
        filename = input(f"{Fore.CYAN}Custom filename (optional): ").strip()
        
        result = self.download_video(url, quality, filename if filename else None)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Download berhasil!")
            print(f"File: {result['filename']}")
            print(f"Size: {result['file_size_mb']:.2f} MB")
            print(f"Path: {result['file_path']}")
        else:
            print(f"{Fore.RED}❌ Download gagal: {result['error']}")

    def _interactive_audio_download(self):
        """Interactive audio download"""
        url = input(f"{Fore.CYAN}URL video: ").strip()
        if not url:
            print(f"{Fore.RED}❌ URL tidak boleh kosong!")
            return
        
        format_choice = input(f"{Fore.CYAN}Audio format (mp3/m4a/wav): ").strip() or "m4a"
        
        result = self.download_audio_only(url, format_choice)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Audio download berhasil!")
            print(f"File: {result['filename']}")
            print(f"Size: {result['file_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Audio download gagal: {result['error']}")

    def _interactive_playlist_download(self):
        """Interactive playlist download"""
        url = input(f"{Fore.CYAN}URL playlist: ").strip()
        if not url:
            print(f"{Fore.RED}❌ URL tidak boleh kosong!")
            return
        
        max_downloads = input(f"{Fore.CYAN}Max downloads (default: 10): ").strip()
        max_downloads = int(max_downloads) if max_downloads else 10
        
        quality = input(f"{Fore.CYAN}Quality (best/high/medium/low): ").strip() or "high"
        
        result = self.download_playlist(url, quality, max_downloads)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Playlist download berhasil!")
            print(f"Files downloaded: {result['files_downloaded']}")
            print(f"Total size: {result['total_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Playlist download gagal: {result['error']}")

    def _interactive_video_info(self):
        """Interactive video info"""
        url = input(f"{Fore.CYAN}URL video: ").strip()
        if not url:
            print(f"{Fore.RED}❌ URL tidak boleh kosong!")
            return
        
        info = self.get_video_info(url)
        
        if "error" in info:
            print(f"{Fore.RED}❌ Error: {info['error']}")
            return
        
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

    def _interactive_list_formats(self):
        """Interactive list formats"""
        url = input(f"{Fore.CYAN}URL video: ").strip()
        if not url:
            print(f"{Fore.RED}❌ URL tidak boleh kosong!")
            return
        
        formats = self.get_available_formats(url)
        
        if formats.get("success"):
            print(f"\n{Fore.GREEN}📋 AVAILABLE FORMATS:")
            print(formats["formats_list"])
        else:
            print(f"{Fore.RED}❌ Error: {formats.get('error', 'Unknown error')}")

    def _interactive_batch_download(self):
        """Interactive batch download"""
        print(f"{Fore.YELLOW}Pilih metode input:")
        print("1. Input URLs manual")
        print("2. Load dari file")
        
        choice = input(f"{Fore.WHITE}Pilihan (1-2): ").strip()
        
        urls = []
        
        if choice == "1":
            print(f"{Fore.CYAN}Masukkan URLs (ketik 'done' untuk selesai):")
            while True:
                url = input(f"{Fore.WHITE}URL: ").strip()
                if url.lower() == 'done':
                    break
                if url:
                    urls.append(url)
        
        elif choice == "2":
            file_path = input(f"{Fore.WHITE}Path ke file URLs: ").strip()
            if not os.path.exists(file_path):
                print(f"{Fore.RED}❌ File tidak ditemukan!")
                return
            
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"{Fore.RED}❌ Error reading file: {e}")
                return
        
        if not urls:
            print(f"{Fore.RED}❌ Tidak ada URLs!")
            return
        
        quality = input(f"{Fore.CYAN}Quality (best/high/medium/low): ").strip() or "high"
        
        result = self.batch_download(urls, quality)
        
        print(f"\n{Fore.GREEN}📊 BATCH DOWNLOAD RESULTS:")
        print(f"Total URLs: {result['total_urls']}")
        print(f"Successful: {len(result['successful'])}")
        print(f"Failed: {len(result['failed'])}")
        print(f"Total size: {result['total_size_mb']:.2f} MB")

    def _show_download_statistics(self):
        """Show download statistics"""
        stats = self.get_download_stats()
        print(f"\n{Fore.GREEN}📊 DOWNLOAD STATISTICS:")
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        
        print(f"\n📱 Platform breakdown:")
        for platform, data in stats['platform_breakdown'].items():
            print(f"  {platform}: {data['files']} files ({data['size_mb']:.2f} MB)")
        
        if stats['recent_downloads']:
            print(f"\n📥 Recent downloads:")
            for file_info in stats['recent_downloads'][:5]:
                print(f"  {file_info['name']} ({file_info['platform']}) - {file_info['size_mb']:.2f} MB")

    def _interactive_cleanup(self):
        """Interactive cleanup"""
        days = input(f"{Fore.CYAN}Hapus file lebih lama dari berapa hari? (default: 7): ").strip()
        days = int(days) if days else 7
        
        confirm = input(f"{Fore.YELLOW}Yakin ingin menghapus file > {days} hari? (y/N): ").strip().lower()
        if confirm == 'y':
            self.cleanup_downloads(days)


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="Video Downloader menggunakan yt-dlp")
    parser.add_argument("--url", "-u", help="URL video untuk download")
    parser.add_argument("--quality", "-q", choices=['best', 'high', 'medium', 'low', 'audio_only'], 
                       default='high', help="Quality preset")
    parser.add_argument("--filename", "-f", help="Custom filename")
    parser.add_argument("--platform", "-p", choices=['youtube', 'tiktok', 'facebook', 'instagram', 'twitter'], 
                       help="Force platform detection")
    parser.add_argument("--playlist", action="store_true", help="Download as playlist")
    parser.add_argument("--max-downloads", type=int, default=10, help="Max downloads for playlist")
    parser.add_argument("--audio-only", action="store_true", help="Download audio only")
    parser.add_argument("--audio-format", choices=['mp3', 'm4a', 'wav'], default='m4a', help="Audio format")
    parser.add_argument("--info", action="store_true", help="Get video info only")
    parser.add_argument("--formats", action="store_true", help="List available formats")
    parser.add_argument("--batch", help="File with URLs for batch download")
    parser.add_argument("--cleanup", type=int, help="Cleanup files older than N days")
    parser.add_argument("--stats", action="store_true", help="Show download statistics")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    downloader = VideoDownloader(debug=args.debug)
    
    # Handle different actions
    if args.cleanup:
        downloader.cleanup_downloads(args.cleanup)
        return
    
    if args.stats:
        downloader._show_download_statistics()
        return
    
    if not args.url and not args.batch:
        # Interactive mode
        downloader.interactive_download_menu()
        return
    
    # Command line mode
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"{Fore.RED}❌ Batch file not found: {args.batch}")
            sys.exit(1)
        
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        result = downloader.batch_download(urls, args.quality)
        print(f"Batch download: {len(result['successful'])}/{result['total_urls']} successful")
        return
    
    if args.info:
        info = downloader.get_video_info(args.url)
        if "error" in info:
            print(f"{Fore.RED}❌ Error: {info['error']}")
            sys.exit(1)
        
        print(f"Title: {info['title']}")
        print(f"Platform: {info['platform']}")
        print(f"Duration: {info['duration']}s")
        print(f"Quality: {info['best_quality']}")
        return
    
    if args.formats:
        formats = downloader.get_available_formats(args.url)
        if formats.get("success"):
            print(formats["formats_list"])
        else:
            print(f"{Fore.RED}❌ Error: {formats.get('error')}")
        return
    
    if args.audio_only:
        result = downloader.download_audio_only(args.url, args.audio_format)
    elif args.playlist:
        result = downloader.download_playlist(args.url, args.quality, args.max_downloads)
    else:
        result = downloader.download_video(args.url, args.quality, args.filename, args.platform)
    
    if result.get("success"):
        print(f"{Fore.GREEN}✅ Download successful!")
        if "file_path" in result:
            print(f"File: {result['file_path']}")
        elif "files_downloaded" in result:
            print(f"Files: {result['files_downloaded']}")
    else:
        print(f"{Fore.RED}❌ Download failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)