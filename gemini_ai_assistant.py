#!/usr/bin/env python3
"""
Gemini AI Assistant untuk Social Media Content Generation
Menggunakan Google Gemini AI untuk analisis video dan generate konten
Enhanced dengan Gemini 2.0-flash dan Language Support
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import cv2
import numpy as np
from PIL import Image
import argparse
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class GeminiAIAssistant:
    def __init__(self, debug: bool = False):
        """
        Initialize Gemini AI Assistant
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.model = None
        self.vision_model = None
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.temp_dir = self.base_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.ai_cache_dir = self.base_dir / "ai_cache"
        self.ai_cache_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        self._load_env_file()
        
        # Initialize Gemini
        self._initialize_gemini()

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA,
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

    def _initialize_gemini(self):
        """Initialize Gemini AI dengan model terbaru"""
        if not GENAI_AVAILABLE:
            self._log("google-generativeai tidak tersedia", "ERROR")
            self._log("Install dengan: pip install google-generativeai", "INFO")
            return False
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_api_key_here":
            self._log("GEMINI_API_KEY tidak ditemukan atau masih placeholder", "WARNING")
            self._log("Buat file .env dengan: GEMINI_API_KEY=your_actual_api_key", "INFO")
            return False
        
        try:
            genai.configure(api_key=api_key)
            
            # Try Gemini 2.0-flash first (latest model)
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self._log("Gemini 2.0-flash berhasil diinisialisasi", "SUCCESS")
                return True
            except Exception as e:
                if self.debug:
                    self._log(f"Gemini 2.0-flash tidak tersedia: {e}", "DEBUG")
                
                # Fallback to gemini-pro
                try:
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.vision_model = genai.GenerativeModel('gemini-pro-vision')
                    self._log("Gemini Pro berhasil diinisialisasi (fallback)", "SUCCESS")
                    return True
                except Exception as e2:
                    self._log(f"Gagal inisialisasi Gemini: {e2}", "ERROR")
                    return False
                    
        except Exception as e:
            self._log(f"Gagal konfigurasi Gemini AI: {e}", "ERROR")
            return False

    def extract_video_frames(self, video_path: str, num_frames: int = 3) -> List[str]:
        """Extract frames dari video untuk analisis"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video tidak ditemukan: {video_path}")
        
        self._log(f"🤖 Extracting {num_frames} frames dari video...", "AI")
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                raise ValueError("Video tidak dapat dibaca atau kosong")
            
            # Calculate frame intervals
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            extracted_frames = []
            
            for i, frame_idx in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Save frame as image
                    frame_filename = f"frame_{i+1}_{int(time.time())}.jpg"
                    frame_path = self.temp_dir / frame_filename
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    image.save(frame_path, quality=85)
                    
                    extracted_frames.append(str(frame_path))
                    
            cap.release()
            
            self._log(f"✅ Berhasil extract {len(extracted_frames)} frames", "SUCCESS")
            return extracted_frames
            
        except Exception as e:
            self._log(f"Error extracting frames: {e}", "ERROR")
            return []

    def analyze_video_content(self, video_path: str, language: str = "indonesian") -> Dict[str, Any]:
        """Analyze video content menggunakan Gemini AI dengan language support"""
        if not self.vision_model:
            self._log("Gemini AI tidak tersedia", "ERROR")
            return self._generate_fallback_analysis(video_path, language)
        
        try:
            # Extract frames
            frames = self.extract_video_frames(video_path, num_frames=3)
            if not frames:
                return self._generate_fallback_analysis(video_path, language)
            
            self._log(f"🤖 Menganalisis konten video dengan Gemini 2.0-flash...", "AI")
            
            # Analyze first frame
            image = Image.open(frames[0])
            
            # Enhanced prompt dengan language support
            if language == "english":
                prompt = """
                You are a viral marketing genius and expert YouTube Shorts strategist. Your task is to analyze the given input (visual frames and possibly audio transcription) to create highly engaging metadata.

                Provide response ONLY in valid JSON format with these keys:
                "objects": Array of main objects/subjects in the video
                "activities": Array of activities happening
                "setting": Setting/environment (indoor/outdoor, location type)
                "mood": Mood/emotion conveyed
                "colors": Dominant colors
                "style": Visual style and quality
                "viral_score": Viral potential (1-10 scale)
                "target_audience": Target audience description
                "content_type": Content type classification
                "trending_elements": Elements that could make it trending
                "optimization_tips": Actionable optimization tips
                "engagement_potential": Engagement potential assessment
                "platforms": Best platforms for this content
                "angles": Suggested content angles
                """
            else:
                prompt = """
                Anda adalah seorang jenius marketing viral dan ahli strategi konten YouTube Shorts. Tugas Anda adalah menganalisis input yang diberikan (frame visual dan mungkin transkripsi audio) untuk membuat metadata yang sangat menarik.

                Berikan respons HANYA dalam format JSON yang valid dengan kunci-kunci berikut:
                "objects": Array objek/subjek utama dalam video
                "activities": Array aktivitas yang terjadi
                "setting": Setting/lingkungan (indoor/outdoor, jenis lokasi)
                "mood": Suasana/emosi yang disampaikan
                "colors": Warna-warna dominan
                "style": Gaya visual dan kualitas
                "viral_score": Potensi viral (skala 1-10)
                "target_audience": Deskripsi target audience
                "content_type": Klasifikasi jenis konten
                "trending_elements": Elemen yang bisa membuat trending
                "optimization_tips": Tips optimasi yang actionable
                "engagement_potential": Penilaian potensi engagement
                "platforms": Platform terbaik untuk konten ini
                "angles": Sudut konten yang disarankan
                """
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse response
            try:
                # Extract JSON from response
                response_text = response.text
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
                
                analysis = json.loads(json_text)
                
                self._log(f"✅ Video analysis dengan Gemini 2.0-flash selesai", "SUCCESS")
                return analysis
                
            except json.JSONDecodeError:
                self._log("Error parsing AI response, using fallback", "WARNING")
                return self._generate_fallback_analysis(video_path, language)
                
        except Exception as e:
            self._log(f"Error analyzing video: {e}", "ERROR")
            return self._generate_fallback_analysis(video_path, language)

    def _generate_fallback_analysis(self, video_path: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback analysis jika AI tidak tersedia"""
        if language == "english":
            return {
                "objects": ["video content"],
                "activities": ["unknown activity"],
                "setting": "unknown",
                "mood": "neutral",
                "colors": ["mixed"],
                "style": "standard",
                "viral_score": 7,
                "target_audience": "general audience",
                "content_type": "entertainment",
                "trending_elements": ["engaging visuals"],
                "optimization_tips": ["add trending hashtags", "optimize for mobile"],
                "engagement_potential": "moderate",
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["entertaining", "engaging", "shareable"]
            }
        else:
            return {
                "objects": ["konten video"],
                "activities": ["aktivitas tidak diketahui"],
                "setting": "tidak diketahui",
                "mood": "netral",
                "colors": ["campuran"],
                "style": "standar",
                "viral_score": 7,
                "target_audience": "audience umum",
                "content_type": "hiburan",
                "trending_elements": ["visual menarik"],
                "optimization_tips": ["tambahkan hashtag trending", "optimasi untuk mobile"],
                "engagement_potential": "sedang",
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["menghibur", "menarik", "shareable"]
            }

    def generate_platform_content(self, analysis: Dict[str, Any], platforms: List[str], 
                                language: str = "indonesian") -> Dict[str, Any]:
        """Generate content untuk setiap platform berdasarkan analysis dengan language support"""
        if not self.model:
            return self._generate_fallback_content(platforms, language)
        
        try:
            content = {}
            
            for platform in platforms:
                self._log(f"🤖 Generating content untuk {platform}...", "AI")
                
                # Enhanced prompt dengan language support
                if language == "english":
                    prompt = f"""
                    You are a viral marketing genius and expert {platform} strategist. Create highly engaging content for {platform} based on this video analysis:
                    {json.dumps(analysis, indent=2)}

                    Generate content optimized for {platform} with these requirements:

                    Platform-specific requirements:
                    - TikTok: Viral, trendy, youth-focused, max 150 chars title
                    - Instagram: Aesthetic, visual, lifestyle, max 125 chars title  
                    - YouTube: SEO-optimized, searchable, max 100 chars title
                    - Facebook: Community-focused, shareable, max 255 chars title

                    Provide response ONLY in valid JSON format with these keys:
                    "title_options": Array of 3 engaging title options:
                        1. "Positive Clickbait" style
                        2. Question format
                        3. Descriptive but mysterious style
                    "description": Short description (1-2 sentences)
                    "tags": Array of 10-15 relevant tags (without '#' character)
                    "thumbnail_suggestion": Short description of best thumbnail concept
                    "caption_suggestion": ONE short caption suggestion (max 10-12 words) for the video, without hashtags (#) or other symbols
                    "cta": Call-to-action appropriate for platform
                    "best_time": Best posting time suggestion
                    """
                else:
                    prompt = f"""
                    Anda adalah seorang jenius marketing viral dan ahli strategi konten {platform}. Buat konten yang sangat menarik untuk {platform} berdasarkan analisis video ini:
                    {json.dumps(analysis, indent=2)}

                    Generate konten yang dioptimasi untuk {platform} dengan requirements ini:

                    Requirements spesifik platform:
                    - TikTok: Viral, trendy, youth-focused, max 150 karakter judul
                    - Instagram: Aesthetic, visual, lifestyle, max 125 karakter judul  
                    - YouTube: SEO-optimized, searchable, max 100 karakter judul
                    - Facebook: Community-focused, shareable, max 255 karakter judul

                    Berikan respons HANYA dalam format JSON yang valid dengan kunci-kunci berikut:
                    "title_options": Array berisi 3 opsi judul yang menarik:
                        1. Gaya "Clickbait Positif"
                        2. Berbentuk pertanyaan
                        3. Gaya deskriptif tapi misterius
                    "description": Deskripsi singkat (1-2 kalimat)
                    "tags": Array berisi 10-15 tag yang relevan (tanpa karakter '#')
                    "thumbnail_suggestion": Deskripsi singkat konsep thumbnail terbaik
                    "caption_suggestion": SATU saran caption singkat (maksimal 10-12 kata) untuk di video, tanpa hashtag (#) atau yang lainnya
                    "cta": Call-to-action yang sesuai platform
                    "best_time": Saran waktu posting terbaik
                    """
                
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text
                    
                    # Extract JSON
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    else:
                        json_text = response_text
                    
                    platform_content = json.loads(json_text)
                    content[platform] = platform_content
                    
                except (json.JSONDecodeError, Exception) as e:
                    self._log(f"Error generating content for {platform}: {e}", "WARNING")
                    content[platform] = self._generate_fallback_platform_content(platform, language)
            
            self._log(f"✅ Content generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return content
            
        except Exception as e:
            self._log(f"Error generating platform content: {e}", "ERROR")
            return self._generate_fallback_content(platforms, language)

    def _generate_fallback_content(self, platforms: List[str], language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback content dengan language support"""
        content = {}
        for platform in platforms:
            content[platform] = self._generate_fallback_platform_content(platform, language)
        return content

    def _generate_fallback_platform_content(self, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback content untuk platform tertentu dengan language support"""
        if language == "english":
            base_content = {
                "tiktok": {
                    "title_options": [
                        "This Video Will Blow Your Mind! 🔥",
                        "Why Is Everyone Talking About This?",
                        "The Secret They Don't Want You to Know..."
                    ],
                    "description": "Amazing content that will change your perspective! Tag someone who needs to see this.",
                    "tags": ["viral", "trending", "fyp", "amazing", "wow", "mindblowing", "tiktok", "video", "content", "entertainment"],
                    "thumbnail_suggestion": "Bright, eye-catching thumbnail with surprised expression",
                    "caption_suggestion": "Wait for the plot twist at the end!",
                    "cta": "Follow for more amazing content!",
                    "best_time": "7:00-9:00 PM"
                },
                "instagram": {
                    "title_options": [
                        "Content That Will Change Your Life! ✨",
                        "Have You Seen This Incredible Thing?",
                        "The Story Behind This Amazing Moment..."
                    ],
                    "description": "Incredible content you need to see! Save this post and share with your friends.",
                    "tags": ["viral", "instagram", "reels", "amazing", "content", "trending", "lifestyle", "inspiration", "wow", "incredible"],
                    "thumbnail_suggestion": "Aesthetic, high-quality thumbnail with good lighting",
                    "caption_suggestion": "This moment changed everything for me",
                    "cta": "Save and share to your story!",
                    "best_time": "8:00-10:00 PM"
                },
                "youtube": {
                    "title_options": [
                        "This Video Will Surprise You!",
                        "What Happens Next Will Shock You",
                        "The Truth About This Amazing Content"
                    ],
                    "description": "Watch this incredible video until the end! Don't forget to subscribe, like, and share.",
                    "tags": ["Shorts", "viral", "amazing", "youtube", "trending", "incredible", "wow", "mindblowing", "content", "video"],
                    "thumbnail_suggestion": "High-contrast thumbnail with clear focal point",
                    "caption_suggestion": "Subscribe for more amazing content like this!",
                    "cta": "Subscribe for more amazing videos!",
                    "best_time": "6:00-8:00 PM"
                },
                "facebook": {
                    "title_options": [
                        "Amazing Video That Everyone Is Sharing!",
                        "Have You Seen This Incredible Content?",
                        "The Video That's Breaking the Internet..."
                    ],
                    "description": "This incredible video is going viral! Share it with your friends and family.",
                    "tags": ["viral", "amazing", "video", "facebook", "reels", "incredible", "wow", "trending", "share", "community"],
                    "thumbnail_suggestion": "Community-friendly thumbnail that encourages sharing",
                    "caption_suggestion": "Share this with someone who needs to see it!",
                    "cta": "Share with your friends!",
                    "best_time": "7:00-9:00 PM"
                }
            }
        else:
            base_content = {
                "tiktok": {
                    "title_options": [
                        "Video Viral yang Bikin Jutaan Views! 🔥",
                        "Kenapa Video Ini Bisa Trending #1?",
                        "Plot Twist yang Nggak Akan Kamu Sangka..."
                    ],
                    "description": "Konten amazing yang akan mengubah perspektif kamu! Tag bestie yang perlu lihat ini.",
                    "tags": ["viral", "trending", "fyp", "amazing", "wow", "keren", "tiktok", "video", "konten", "hiburan"],
                    "thumbnail_suggestion": "Thumbnail cerah dan eye-catching dengan ekspresi terkejut",
                    "caption_suggestion": "Tunggu plot twist di akhir video!",
                    "cta": "Follow untuk konten amazing lainnya!",
                    "best_time": "19:00-21:00"
                },
                "instagram": {
                    "title_options": [
                        "Konten yang Akan Mengubah Hidupmu! ✨",
                        "Udah Lihat yang Incredible Ini Belum?",
                        "Cerita di Balik Momen Amazing Ini..."
                    ],
                    "description": "Konten incredible yang wajib kamu lihat! Save post ini dan share ke teman-teman kamu.",
                    "tags": ["viral", "instagram", "reels", "amazing", "konten", "trending", "lifestyle", "inspirasi", "wow", "incredible"],
                    "thumbnail_suggestion": "Thumbnail aesthetic berkualitas tinggi dengan pencahayaan bagus",
                    "caption_suggestion": "Momen ini mengubah segalanya untukku",
                    "cta": "Save dan share ke story kamu!",
                    "best_time": "20:00-22:00"
                },
                "youtube": {
                    "title_options": [
                        "Video Ini Akan Mengejutkan Kamu!",
                        "Yang Terjadi Selanjutnya Bikin Shock",
                        "Fakta Mengejutkan di Balik Konten Ini"
                    ],
                    "description": "Tonton video incredible ini sampai habis! Jangan lupa subscribe, like, dan share.",
                    "tags": ["Shorts", "viral", "amazing", "youtube", "trending", "incredible", "wow", "mengejutkan", "konten", "video"],
                    "thumbnail_suggestion": "Thumbnail kontras tinggi dengan focal point yang jelas",
                    "caption_suggestion": "Subscribe untuk konten amazing lainnya!",
                    "cta": "Subscribe untuk video amazing lainnya!",
                    "best_time": "18:00-20:00"
                },
                "facebook": {
                    "title_options": [
                        "Video Amazing yang Lagi Viral Banget!",
                        "Udah Lihat Konten Incredible Ini Belum?",
                        "Video yang Lagi Heboh di Internet..."
                    ],
                    "description": "Video incredible ini lagi viral! Share ke teman dan keluarga kamu.",
                    "tags": ["viral", "amazing", "video", "facebook", "reels", "incredible", "wow", "trending", "share", "komunitas"],
                    "thumbnail_suggestion": "Thumbnail yang community-friendly dan mendorong sharing",
                    "caption_suggestion": "Share ini ke yang perlu lihat!",
                    "cta": "Share ke teman-teman kamu!",
                    "best_time": "19:00-21:00"
                }
            }
        
        return base_content.get(platform, base_content["tiktok"])

    def generate_text_post(self, topic: str, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate text post berdasarkan topik dengan language support"""
        if not self.model:
            return self._generate_fallback_text_post(topic, platform, language)
        
        try:
            self._log(f"🤖 Generating text post untuk {platform} dengan topik: {topic}", "AI")
            
            if language == "english":
                prompt = f"""
                You are a viral marketing genius and expert {platform} strategist. Create an engaging text post for {platform} about: {topic}

                Platform guidelines:
                - TikTok: Casual, trendy, youth-focused
                - Instagram: Aesthetic, lifestyle, visual
                - YouTube: Informative, searchable, community
                - Facebook: Conversational, community-focused

                Provide response ONLY in valid JSON format with these keys:
                "title": Engaging title
                "content": Main post content
                "hashtags": Relevant hashtags (without '#' character)
                "cta": Call-to-action
                """
            else:
                prompt = f"""
                Anda adalah seorang jenius marketing viral dan ahli strategi konten {platform}. Buat text post yang menarik untuk {platform} tentang: {topic}

                Panduan platform:
                - TikTok: Casual, trendy, youth-focused
                - Instagram: Aesthetic, lifestyle, visual
                - YouTube: Informatif, searchable, community
                - Facebook: Conversational, community-focused

                Berikan respons HANYA dalam format JSON yang valid dengan kunci-kunci berikut:
                "title": Judul yang menarik
                "content": Konten post utama
                "hashtags": Hashtag yang relevan (tanpa karakter '#')
                "cta": Call-to-action
                """
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            post_content = json.loads(json_text)
            
            self._log(f"✅ Text post generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return post_content
            
        except Exception as e:
            self._log(f"Error generating text post: {e}", "ERROR")
            return self._generate_fallback_text_post(topic, platform, language)

    def _generate_fallback_text_post(self, topic: str, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback text post dengan language support"""
        if language == "english":
            return {
                "title": f"Amazing Tips About {topic} You Need to Know!",
                "content": f"Check out these incredible tips about {topic}! This will definitely change your perspective. Share your experience in the comments!",
                "hashtags": f"tips {topic.replace(' ', '')} viral trending {platform}",
                "cta": "Share your experience in the comments!"
            }
        else:
            return {
                "title": f"Tips {topic} yang Wajib Diketahui!",
                "content": f"Simak tips {topic} yang sangat berguna ini! Pasti akan mengubah perspektif kamu. Share pengalaman kamu di komentar!",
                "hashtags": f"tips {topic.replace(' ', '')} viral trending {platform}",
                "cta": "Share pengalaman kamu di komentar!"
            }

    def check_api_status(self) -> Dict[str, Any]:
        """Check Gemini API status"""
        if not GENAI_AVAILABLE:
            return {
                "success": False,
                "error": "google-generativeai not installed",
                "message": "Install dengan: pip install google-generativeai"
            }
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_api_key_here":
            return {
                "success": False,
                "error": "API key not configured",
                "message": "Buat file .env dengan GEMINI_API_KEY=your_actual_api_key"
            }
        
        try:
            genai.configure(api_key=api_key)
            
            # Test with simple request
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Test")
            
            return {
                "success": True,
                "model": "gemini-2.0-flash-exp",
                "message": "Gemini 2.0-flash API ready"
            }
            
        except Exception as e:
            try:
                # Fallback test
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Test")
                
                return {
                    "success": True,
                    "model": "gemini-pro",
                    "message": "Gemini Pro API ready (fallback)"
                }
            except Exception as e2:
                return {
                    "success": False,
                    "error": str(e2),
                    "message": "API key invalid atau quota habis"
                }

    def cleanup_temp_files(self):
        """Cleanup temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                for file_path in self.temp_dir.glob("frame_*.jpg"):
                    file_path.unlink()
                self._log("Temp files cleaned up", "SUCCESS")
        except Exception as e:
            self._log(f"Error cleaning temp files: {e}", "ERROR")

    def interactive_ai_menu(self):
        """Interactive AI assistant menu"""
        if not GENAI_AVAILABLE:
            print(f"{Fore.RED}❌ google-generativeai tidak tersedia!")
            print(f"{Fore.YELLOW}Install dengan: pip install google-generativeai")
            return
        
        if not self.model:
            print(f"{Fore.RED}❌ Gemini AI tidak tersedia!")
            print(f"{Fore.YELLOW}Buat file .env dengan GEMINI_API_KEY=your_api_key")
            return
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}🤖 Gemini AI Assistant")
        print("=" * 50)
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 🎬 Analyze Video")
            print("2. ✍️ Generate Text Post")
            print("3. 📱 Generate Platform Content")
            print("4. 🔍 Check API Status")
            print("5. 🧹 Cleanup Temp Files")
            print("6. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-6): ").strip()
            
            if choice == "1":
                video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
                if os.path.exists(video_path):
                    language = "english" if input(f"{Fore.CYAN}Language (en/id): ").strip().lower() == "en" else "indonesian"
                    analysis = self.analyze_video_content(video_path, language)
                    
                    print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS:")
                    print(json.dumps(analysis, indent=2, ensure_ascii=False))
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "2":
                topic = input(f"{Fore.CYAN}Topik: ").strip()
                platform = input(f"{Fore.CYAN}Platform (tiktok/instagram/youtube/facebook): ").strip()
                if topic and platform:
                    language = "english" if input(f"{Fore.CYAN}Language (en/id): ").strip().lower() == "en" else "indonesian"
                    post = self.generate_text_post(topic, platform, language)
                    
                    print(f"\n{Fore.GREEN}📝 GENERATED POST:")
                    print(json.dumps(post, indent=2, ensure_ascii=False))
                else:
                    print(f"{Fore.RED}❌ Topik dan platform harus diisi!")
            
            elif choice == "3":
                video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
                if os.path.exists(video_path):
                    platforms = input(f"{Fore.CYAN}Platforms (comma separated): ").strip().split(',')
                    platforms = [p.strip() for p in platforms if p.strip()]
                    
                    if platforms:
                        language = "english" if input(f"{Fore.CYAN}Language (en/id): ").strip().lower() == "en" else "indonesian"
                        analysis = self.analyze_video_content(video_path, language)
                        content = self.generate_platform_content(analysis, platforms, language)
                        
                        print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
                        print(json.dumps(content, indent=2, ensure_ascii=False))
                    else:
                        print(f"{Fore.RED}❌ Minimal satu platform harus dipilih!")
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "4":
                status = self.check_api_status()
                if status["success"]:
                    print(f"{Fore.GREEN}✅ {status['message']}")
                    print(f"Model: {status['model']}")
                else:
                    print(f"{Fore.RED}❌ {status['message']}")
            
            elif choice == "5":
                self.cleanup_temp_files()
            
            elif choice == "6":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="Gemini AI Assistant")
    parser.add_argument("--video", "-v", help="Path ke video untuk analisis")
    parser.add_argument("--topic", "-t", help="Topik untuk text post")
    parser.add_argument("--platform", "-p", help="Platform target")
    parser.add_argument("--language", "-l", choices=['indonesian', 'english'], 
                       default='indonesian', help="Language for content generation")
    parser.add_argument("--api-key", help="Gemini API key")
    parser.add_argument("--check-api", action="store_true", help="Check API status")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ['GEMINI_API_KEY'] = args.api_key
    
    assistant = GeminiAIAssistant(debug=args.debug)
    
    if args.check_api:
        status = assistant.check_api_status()
        if status["success"]:
            print(f"{Fore.GREEN}✅ {status['message']}")
            print(f"Model: {status['model']}")
        else:
            print(f"{Fore.RED}❌ {status['message']}")
        return
    
    if args.video:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ Video file not found: {args.video}")
            sys.exit(1)
        
        analysis = assistant.analyze_video_content(args.video, args.language)
        print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]
            content = assistant.generate_platform_content(analysis, platforms, args.language)
            print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
    
    elif args.topic and args.platform:
        post = assistant.generate_text_post(args.topic, args.platform, args.language)
        print(f"\n{Fore.GREEN}📝 GENERATED POST:")
        print(json.dumps(post, indent=2, ensure_ascii=False))
    
    else:
        # Interactive mode
        assistant.interactive_ai_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)