#!/usr/bin/env python3
"""
FFmpeg Video Editor untuk Social Media
Advanced video enhancement, anti-detection, dan platform optimization
"""

import os
import sys
import json
import time
import subprocess
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
import argparse
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class FFmpegVideoEditor:
    def __init__(self, debug: bool = False):
        """
        Initialize FFmpeg Video Editor
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.edited_videos_dir = self.base_dir / "edited_videos"
        self.edited_videos_dir.mkdir(exist_ok=True)
        self.temp_ffmpeg_dir = self.base_dir / "temp_ffmpeg"
        self.temp_ffmpeg_dir.mkdir(exist_ok=True)
        self.ffmpeg_presets_dir = self.base_dir / "ffmpeg_presets"
        self.ffmpeg_presets_dir.mkdir(exist_ok=True)
        
        # Check FFmpeg installation
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            self._log("FFmpeg tidak ditemukan! Install FFmpeg terlebih dahulu", "ERROR")
        
        # Enhancement presets
        self.enhancement_presets = {
            'light': {
                'brightness': 0.05,
                'contrast': 1.1,
                'saturation': 1.1,
                'sharpness': 0.3,
                'noise_reduction': 'light'
            },
            'medium': {
                'brightness': 0.1,
                'contrast': 1.2,
                'saturation': 1.2,
                'sharpness': 0.5,
                'noise_reduction': 'medium'
            },
            'heavy': {
                'brightness': 0.15,
                'contrast': 1.3,
                'saturation': 1.3,
                'sharpness': 0.7,
                'noise_reduction': 'heavy'
            },
            'professional': {
                'brightness': 0.08,
                'contrast': 1.25,
                'saturation': 1.15,
                'sharpness': 0.6,
                'noise_reduction': 'medium'
            }
        }
        
        # Platform optimization settings
        self.platform_settings = {
            'tiktok': {
                'resolution': '1080x1920',
                'fps': 30,
                'bitrate': '2500k',
                'format': 'mp4',
                'codec': 'libx264'
            },
            'instagram': {
                'resolution': '1080x1920',
                'fps': 30,
                'bitrate': '3000k',
                'format': 'mp4',
                'codec': 'libx264'
            },
            'youtube': {
                'resolution': '1080x1920',
                'fps': 30,
                'bitrate': '4000k',
                'format': 'mp4',
                'codec': 'libx264'
            },
            'facebook': {
                'resolution': '1080x1080',
                'fps': 30,
                'bitrate': '2000k',
                'format': 'mp4',
                'codec': 'libx264'
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
            "FFMPEG": Fore.LIGHTBLUE_EX
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
            "FFMPEG": "🎬"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def _find_ffmpeg(self) -> Optional[str]:
        """Cari FFmpeg di system"""
        import shutil
        
        # Check if ffmpeg is available
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            self._log(f"FFmpeg ditemukan: {ffmpeg_path}", "SUCCESS")
            return ffmpeg_path
        
        self._log("FFmpeg tidak ditemukan", "ERROR")
        return None

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get informasi video menggunakan FFprobe"""
        if not self.ffmpeg_path:
            return {"error": "FFmpeg not available"}
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                
                # Extract video stream info
                video_stream = None
                for stream in info['streams']:
                    if stream['codec_type'] == 'video':
                        video_stream = stream
                        break
                
                if video_stream:
                    return {
                        'duration': float(info['format'].get('duration', 0)),
                        'width': int(video_stream.get('width', 0)),
                        'height': int(video_stream.get('height', 0)),
                        'fps': eval(video_stream.get('r_frame_rate', '30/1')),
                        'bitrate': int(info['format'].get('bit_rate', 0)),
                        'codec': video_stream.get('codec_name', 'unknown'),
                        'format': info['format'].get('format_name', 'unknown')
                    }
            
            return {"error": "Could not get video info"}
            
        except Exception as e:
            return {"error": str(e)}

    def enhance_video(self, input_path: str, preset: str = 'medium', 
                     output_path: str = None) -> Dict[str, Any]:
        """Enhance video quality menggunakan preset"""
        if not self.ffmpeg_path:
            return {"success": False, "error": "FFmpeg not available"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": "Input file not found"}
        
        if preset not in self.enhancement_presets:
            preset = 'medium'
        
        settings = self.enhancement_presets[preset]
        
        if not output_path:
            base_name = Path(input_path).stem
            output_path = self.edited_videos_dir / f"{base_name}_enhanced_{preset}.mp4"
        
        self._log(f"Enhancing video dengan preset: {preset}", "FFMPEG")
        
        try:
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', self._build_enhancement_filter(settings),
                '-c:v', 'libx264',
                '-crf', '18',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # Overwrite output
                str(output_path)
            ]
            
            if self.debug:
                self._log(f"FFmpeg command: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self._log(f"Video enhancement selesai: {output_path.name} ({file_size:.2f}MB)", "SUCCESS")
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "preset": preset,
                    "file_size_mb": round(file_size, 2)
                }
            else:
                error_msg = result.stderr or "Enhancement failed"
                self._log(f"Enhancement gagal: {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self._log(f"Enhancement error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def _build_enhancement_filter(self, settings: Dict[str, Any]) -> str:
        """Build FFmpeg filter string untuk enhancement"""
        filters = []
        
        # Brightness and contrast
        if settings.get('brightness') or settings.get('contrast'):
            brightness = settings.get('brightness', 0)
            contrast = settings.get('contrast', 1)
            filters.append(f"eq=brightness={brightness}:contrast={contrast}")
        
        # Saturation
        if settings.get('saturation'):
            saturation = settings.get('saturation', 1)
            filters.append(f"eq=saturation={saturation}")
        
        # Sharpening
        if settings.get('sharpness'):
            sharpness = settings.get('sharpness', 0)
            filters.append(f"unsharp=5:5:{sharpness}:5:5:{sharpness}")
        
        # Noise reduction
        noise_level = settings.get('noise_reduction', 'none')
        if noise_level == 'light':
            filters.append("hqdn3d=2:1:2:3")
        elif noise_level == 'medium':
            filters.append("hqdn3d=4:3:6:4.5")
        elif noise_level == 'heavy':
            filters.append("hqdn3d=8:6:12:9")
        
        return ','.join(filters) if filters else 'null'

    def apply_anti_detection(self, input_path: str, intensity: str = 'medium',
                           output_path: str = None) -> Dict[str, Any]:
        """Apply anti-detection modifications"""
        if not self.ffmpeg_path:
            return {"success": False, "error": "FFmpeg not available"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": "Input file not found"}
        
        if not output_path:
            base_name = Path(input_path).stem
            output_path = self.edited_videos_dir / f"{base_name}_antidetect_{intensity}.mp4"
        
        self._log(f"Applying anti-detection dengan intensity: {intensity}", "FFMPEG")
        
        try:
            # Build anti-detection filters
            filters = self._build_anti_detection_filters(intensity)
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', filters,
                '-c:v', 'libx264',
                '-crf', '20',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',
                str(output_path)
            ]
            
            if self.debug:
                self._log(f"FFmpeg command: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self._log(f"Anti-detection applied: {output_path.name} ({file_size:.2f}MB)", "SUCCESS")
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "intensity": intensity,
                    "file_size_mb": round(file_size, 2)
                }
            else:
                error_msg = result.stderr or "Anti-detection failed"
                self._log(f"Anti-detection gagal: {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self._log(f"Anti-detection error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def _build_anti_detection_filters(self, intensity: str) -> str:
        """Build anti-detection filters"""
        filters = []
        
        if intensity == 'light':
            # Light modifications
            filters.extend([
                f"eq=brightness={random.uniform(-0.02, 0.02)}:contrast={random.uniform(0.98, 1.02)}",
                f"hue=h={random.uniform(-2, 2)}"
            ])
        elif intensity == 'medium':
            # Medium modifications
            filters.extend([
                f"eq=brightness={random.uniform(-0.05, 0.05)}:contrast={random.uniform(0.95, 1.05)}",
                f"hue=h={random.uniform(-5, 5)}:s={random.uniform(0.95, 1.05)}",
                f"scale=iw*{random.uniform(0.99, 1.01)}:ih*{random.uniform(0.99, 1.01)}"
            ])
        elif intensity == 'heavy':
            # Heavy modifications
            filters.extend([
                f"eq=brightness={random.uniform(-0.1, 0.1)}:contrast={random.uniform(0.9, 1.1)}",
                f"hue=h={random.uniform(-10, 10)}:s={random.uniform(0.9, 1.1)}",
                f"scale=iw*{random.uniform(0.98, 1.02)}:ih*{random.uniform(0.98, 1.02)}",
                "noise=alls=1:allf=t"
            ])
        
        return ','.join(filters) if filters else 'null'

    def optimize_for_platform(self, input_path: str, platform: str,
                            output_path: str = None) -> Dict[str, Any]:
        """Optimize video untuk platform tertentu"""
        if not self.ffmpeg_path:
            return {"success": False, "error": "FFmpeg not available"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": "Input file not found"}
        
        if platform not in self.platform_settings:
            return {"success": False, "error": f"Platform {platform} not supported"}
        
        settings = self.platform_settings[platform]
        
        if not output_path:
            base_name = Path(input_path).stem
            output_path = self.edited_videos_dir / f"{base_name}_{platform}_optimized.mp4"
        
        self._log(f"Optimizing untuk {platform}...", "FFMPEG")
        
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', f"scale={settings['resolution']}:force_original_aspect_ratio=decrease,pad={settings['resolution']}:(ow-iw)/2:(oh-ih)/2",
                '-r', str(settings['fps']),
                '-c:v', settings['codec'],
                '-b:v', settings['bitrate'],
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                str(output_path)
            ]
            
            if self.debug:
                self._log(f"FFmpeg command: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self._log(f"Platform optimization selesai: {output_path.name} ({file_size:.2f}MB)", "SUCCESS")
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "platform": platform,
                    "file_size_mb": round(file_size, 2)
                }
            else:
                error_msg = result.stderr or "Optimization failed"
                self._log(f"Optimization gagal: {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self._log(f"Optimization error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def create_variations(self, input_path: str, num_variations: int = 3,
                         output_dir: str = None) -> Dict[str, Any]:
        """Create multiple variations dari video"""
        if not self.ffmpeg_path:
            return {"success": False, "error": "FFmpeg not available"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": "Input file not found"}
        
        if not output_dir:
            output_dir = self.edited_videos_dir / "variations"
            output_dir.mkdir(exist_ok=True)
        
        self._log(f"Creating {num_variations} variations...", "FFMPEG")
        
        variations = []
        
        for i in range(num_variations):
            try:
                base_name = Path(input_path).stem
                output_path = output_dir / f"{base_name}_variation_{i+1}.mp4"
                
                # Random modifications for each variation
                brightness = random.uniform(-0.05, 0.05)
                contrast = random.uniform(0.95, 1.05)
                hue = random.uniform(-5, 5)
                saturation = random.uniform(0.95, 1.05)
                
                filters = f"eq=brightness={brightness}:contrast={contrast},hue=h={hue}:s={saturation}"
                
                cmd = [
                    'ffmpeg', '-i', input_path,
                    '-vf', filters,
                    '-c:v', 'libx264',
                    '-crf', '20',
                    '-preset', 'medium',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-y',
                    str(output_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    file_size = os.path.getsize(output_path) / (1024 * 1024)
                    variations.append({
                        "path": str(output_path),
                        "file_size_mb": round(file_size, 2)
                    })
                    self._log(f"Variation {i+1} created: {output_path.name}", "SUCCESS")
                else:
                    self._log(f"Variation {i+1} failed", "ERROR")
                    
            except Exception as e:
                self._log(f"Error creating variation {i+1}: {e}", "ERROR")
        
        return {
            "success": len(variations) > 0,
            "variations": variations,
            "total_created": len(variations)
        }

    def compress_video(self, input_path: str, target_size_mb: float,
                      output_path: str = None) -> Dict[str, Any]:
        """Compress video ke target size"""
        if not self.ffmpeg_path:
            return {"success": False, "error": "FFmpeg not available"}
        
        if not os.path.exists(input_path):
            return {"success": False, "error": "Input file not found"}
        
        if not output_path:
            base_name = Path(input_path).stem
            output_path = self.edited_videos_dir / f"{base_name}_compressed_{target_size_mb}MB.mp4"
        
        self._log(f"Compressing to {target_size_mb}MB...", "FFMPEG")
        
        try:
            # Get video info untuk calculate bitrate
            info = self.get_video_info(input_path)
            if "error" in info:
                return {"success": False, "error": "Could not get video info"}
            
            duration = info['duration']
            target_bitrate = int((target_size_mb * 8 * 1024) / duration)  # kbps
            
            # Ensure minimum quality
            if target_bitrate < 500:
                target_bitrate = 500
                self._log("Target bitrate too low, using minimum 500k", "WARNING")
            
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', 'libx264',
                '-b:v', f'{target_bitrate}k',
                '-maxrate', f'{int(target_bitrate * 1.2)}k',
                '-bufsize', f'{int(target_bitrate * 2)}k',
                '-c:a', 'aac',
                '-b:a', '64k',
                '-preset', 'medium',
                '-y',
                str(output_path)
            ]
            
            if self.debug:
                self._log(f"Target bitrate: {target_bitrate}k", "DEBUG")
                self._log(f"FFmpeg command: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                self._log(f"Compression selesai: {output_path.name} ({file_size:.2f}MB)", "SUCCESS")
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "target_size_mb": target_size_mb,
                    "actual_size_mb": round(file_size, 2),
                    "compression_ratio": round(file_size / target_size_mb, 2)
                }
            else:
                error_msg = result.stderr or "Compression failed"
                self._log(f"Compression gagal: {error_msg}", "ERROR")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self._log(f"Compression error: {e}", "ERROR")
            return {"success": False, "error": str(e)}

    def interactive_editor_menu(self):
        """Interactive video editor menu"""
        if not self.ffmpeg_path:
            print(f"{Fore.RED}❌ FFmpeg tidak tersedia!")
            print(f"{Fore.YELLOW}Install FFmpeg dan pastikan tersedia di PATH")
            return
        
        print(f"\n{Fore.LIGHTBLUE_EX}🎬 FFmpeg Video Editor")
        print("=" * 50)
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. ✨ Enhance Video Quality")
            print("2. 🕵️ Apply Anti-Detection")
            print("3. 📱 Optimize for Platform")
            print("4. 🎭 Create Variations")
            print("5. 🗜️ Compress Video")
            print("6. ℹ️ Get Video Info")
            print("7. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-7): ").strip()
            
            if choice == "1":
                self._interactive_enhance()
            elif choice == "2":
                self._interactive_anti_detection()
            elif choice == "3":
                self._interactive_platform_optimize()
            elif choice == "4":
                self._interactive_create_variations()
            elif choice == "5":
                self._interactive_compress()
            elif choice == "6":
                self._interactive_video_info()
            elif choice == "7":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")

    def _interactive_enhance(self):
        """Interactive video enhancement"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        print(f"\n{Fore.YELLOW}Pilih preset enhancement:")
        print("1. Light")
        print("2. Medium")
        print("3. Heavy")
        print("4. Professional")
        
        preset_choice = input(f"{Fore.WHITE}Pilihan (1-4): ").strip()
        preset_map = {"1": "light", "2": "medium", "3": "heavy", "4": "professional"}
        preset = preset_map.get(preset_choice, "medium")
        
        result = self.enhance_video(video_path, preset)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Enhancement selesai!")
            print(f"Output: {result['output_path']}")
            print(f"Size: {result['file_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Enhancement gagal: {result['error']}")

    def _interactive_anti_detection(self):
        """Interactive anti-detection"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        print(f"\n{Fore.YELLOW}Pilih intensity anti-detection:")
        print("1. Light")
        print("2. Medium")
        print("3. Heavy")
        
        intensity_choice = input(f"{Fore.WHITE}Pilihan (1-3): ").strip()
        intensity_map = {"1": "light", "2": "medium", "3": "heavy"}
        intensity = intensity_map.get(intensity_choice, "medium")
        
        result = self.apply_anti_detection(video_path, intensity)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Anti-detection applied!")
            print(f"Output: {result['output_path']}")
            print(f"Size: {result['file_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Anti-detection gagal: {result['error']}")

    def _interactive_platform_optimize(self):
        """Interactive platform optimization"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        print(f"\n{Fore.YELLOW}Pilih platform:")
        print("1. TikTok")
        print("2. Instagram")
        print("3. YouTube")
        print("4. Facebook")
        
        platform_choice = input(f"{Fore.WHITE}Pilihan (1-4): ").strip()
        platform_map = {"1": "tiktok", "2": "instagram", "3": "youtube", "4": "facebook"}
        platform = platform_map.get(platform_choice)
        
        if not platform:
            print(f"{Fore.RED}❌ Platform tidak valid!")
            return
        
        result = self.optimize_for_platform(video_path, platform)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Platform optimization selesai!")
            print(f"Output: {result['output_path']}")
            print(f"Size: {result['file_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Optimization gagal: {result['error']}")

    def _interactive_create_variations(self):
        """Interactive create variations"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        num_variations = input(f"{Fore.CYAN}Jumlah variasi (default: 3): ").strip()
        num_variations = int(num_variations) if num_variations else 3
        
        result = self.create_variations(video_path, num_variations)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ {result['total_created']} variasi berhasil dibuat!")
            for i, variation in enumerate(result['variations'], 1):
                print(f"  Variation {i}: {Path(variation['path']).name} ({variation['file_size_mb']:.2f} MB)")
        else:
            print(f"{Fore.RED}❌ Create variations gagal!")

    def _interactive_compress(self):
        """Interactive video compression"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        target_size = input(f"{Fore.CYAN}Target size (MB): ").strip()
        try:
            target_size = float(target_size)
        except ValueError:
            print(f"{Fore.RED}❌ Target size harus berupa angka!")
            return
        
        result = self.compress_video(video_path, target_size)
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Compression selesai!")
            print(f"Output: {result['output_path']}")
            print(f"Target: {result['target_size_mb']:.2f} MB")
            print(f"Actual: {result['actual_size_mb']:.2f} MB")
        else:
            print(f"{Fore.RED}❌ Compression gagal: {result['error']}")

    def _interactive_video_info(self):
        """Interactive video info"""
        video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
        if not os.path.exists(video_path):
            print(f"{Fore.RED}❌ File video tidak ditemukan!")
            return
        
        info = self.get_video_info(video_path)
        
        if "error" in info:
            print(f"{Fore.RED}❌ Error: {info['error']}")
            return
        
        print(f"\n{Fore.GREEN}📹 VIDEO INFO:")
        print(f"Duration: {info['duration']:.2f} seconds")
        print(f"Resolution: {info['width']}x{info['height']}")
        print(f"FPS: {info['fps']:.2f}")
        print(f"Bitrate: {info['bitrate']} bps")
        print(f"Codec: {info['codec']}")
        print(f"Format: {info['format']}")


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="FFmpeg Video Editor")
    parser.add_argument("--input", "-i", help="Input video file")
    parser.add_argument("--operation", choices=['enhance', 'anti-detect', 'optimize', 'variations', 'compress', 'info'], 
                       help="Operation to perform")
    parser.add_argument("--preset", choices=['light', 'medium', 'heavy', 'professional'], 
                       default='medium', help="Enhancement preset")
    parser.add_argument("--intensity", choices=['light', 'medium', 'heavy'], 
                       default='medium', help="Anti-detection intensity")
    parser.add_argument("--platform", choices=['tiktok', 'instagram', 'youtube', 'facebook'], 
                       help="Platform for optimization")
    parser.add_argument("--variations", type=int, default=3, help="Number of variations")
    parser.add_argument("--target-size", type=float, help="Target size in MB for compression")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    editor = FFmpegVideoEditor(debug=args.debug)
    
    if args.input and args.operation:
        if not os.path.exists(args.input):
            print(f"{Fore.RED}❌ Input file not found: {args.input}")
            sys.exit(1)
        
        if args.operation == 'enhance':
            result = editor.enhance_video(args.input, args.preset, args.output)
        elif args.operation == 'anti-detect':
            result = editor.apply_anti_detection(args.input, args.intensity, args.output)
        elif args.operation == 'optimize':
            if not args.platform:
                print(f"{Fore.RED}❌ Platform required for optimization")
                sys.exit(1)
            result = editor.optimize_for_platform(args.input, args.platform, args.output)
        elif args.operation == 'variations':
            result = editor.create_variations(args.input, args.variations)
        elif args.operation == 'compress':
            if not args.target_size:
                print(f"{Fore.RED}❌ Target size required for compression")
                sys.exit(1)
            result = editor.compress_video(args.input, args.target_size, args.output)
        elif args.operation == 'info':
            info = editor.get_video_info(args.input)
            if "error" in info:
                print(f"{Fore.RED}❌ Error: {info['error']}")
                sys.exit(1)
            print(json.dumps(info, indent=2))
            return
        
        if result.get("success"):
            print(f"{Fore.GREEN}✅ Operation successful!")
            if "output_path" in result:
                print(f"Output: {result['output_path']}")
        else:
            print(f"{Fore.RED}❌ Operation failed: {result.get('error')}")
            sys.exit(1)
    
    else:
        # Interactive mode
        editor.interactive_editor_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)