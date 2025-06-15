#!/usr/bin/env python3
"""
Gemini AI Assistant untuk Social Media Content Generation
Menggunakan Google Gemini AI 2.0-flash untuk analisis video dan generate konten
Enhanced dengan model terbaru untuk performa yang lebih baik
Support untuk Bahasa Indonesia dan English dengan Viral Marketing Genius
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
        Initialize Gemini AI Assistant dengan model 2.0-flash
        
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
        
        # Initialize Gemini dengan model 2.0-flash
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
                return True
            except Exception as e:
                if self.debug:
                    self._log(f"Error loading .env file: {e}", "WARNING")
                return False
        else:
            if self.debug:
                self._log(".env file not found", "WARNING")
            return False

    def _initialize_gemini(self):
        """Initialize Gemini AI dengan model 2.0-flash"""
        if not GENAI_AVAILABLE:
            self._log("google-generativeai tidak tersedia", "ERROR")
            self._log("Install dengan: pip install google-generativeai", "INFO")
            return False
        
        # Load .env file first
        self._load_env_file()
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            self._log("GEMINI_API_KEY tidak ditemukan", "WARNING")
            self._log("Buat file .env di folder project dengan isi:", "INFO")
            self._log("GEMINI_API_KEY=your_api_key_here", "INFO")
            self._log("Atau set environment variable: set GEMINI_API_KEY=your_api_key", "INFO")
            return False
        
        try:
            genai.configure(api_key=api_key)
            
            # Initialize dengan model 2.0-flash yang lebih powerful
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            self._log("Gemini AI 2.0-flash berhasil diinisialisasi", "SUCCESS")
            self._log("Model: gemini-2.0-flash-exp (Latest & Most Powerful)", "AI")
            return True
        except Exception as e:
            self._log(f"Gagal inisialisasi Gemini AI: {e}", "ERROR")
            
            # Fallback ke model lama jika 2.0-flash tidak tersedia
            try:
                self.model = genai.GenerativeModel('gemini-pro')
                self.vision_model = genai.GenerativeModel('gemini-pro-vision')
                self._log("Fallback ke gemini-pro berhasil", "WARNING")
                return True
            except Exception as e2:
                self._log(f"Fallback juga gagal: {e2}", "ERROR")
                return False

    def get_language_preference(self, context: str = "content generation") -> str:
        """Get user language preference untuk AI content generation"""
        print(f"\n{Fore.YELLOW}🌍 Pilih bahasa untuk {context}:")
        print("1. 🇮🇩 Bahasa Indonesia")
        print("2. 🇺🇸 English")
        
        choice = input(f"{Fore.WHITE}Pilihan (1-2, default: 1): ").strip()
        
        if choice == "2":
            self._log("Language selected: English", "AI")
            return "english"
        else:
            self._log("Language selected: Bahasa Indonesia", "AI")
            return "indonesian"

    def extract_video_frames(self, video_path: str, num_frames: int = 5) -> List[str]:
        """Extract frames dari video untuk analisis"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video tidak ditemukan: {video_path}")
        
        self._log(f"Extracting {num_frames} frames dari video...", "AI")
        
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
            
            self._log(f"Berhasil extract {len(extracted_frames)} frames", "SUCCESS")
            return extracted_frames
            
        except Exception as e:
            self._log(f"Error extracting frames: {e}", "ERROR")
            return []

    def analyze_video_content(self, video_path: str, strategy: str = "balanced", language: str = None) -> Dict[str, Any]:
        """Analyze video content menggunakan Gemini 2.0-flash dengan language support"""
        if not self.vision_model:
            self._log("Gemini AI tidak tersedia", "ERROR")
            return self._generate_fallback_analysis(video_path)
        
        # Get language preference if not provided
        if not language:
            language = self.get_language_preference("video analysis")
        
        try:
            # Extract frames
            frames = self.extract_video_frames(video_path, num_frames=3)
            if not frames:
                return self._generate_fallback_analysis(video_path)
            
            self._log(f"Menganalisis konten video dengan Gemini 2.0-flash ({language})...", "AI")
            
            # Analyze first frame dengan VIRAL MARKETING GENIUS prompt
            image = Image.open(frames[0])
            
            # Enhanced VIRAL MARKETING GENIUS prompt dengan language support
            if language == "english":
                prompt = f"""
                You are a VIRAL MARKETING GENIUS and expert YouTube Shorts strategist. Your task is to analyze the given input (visual frames and possibly audio transcription) to create highly engaging metadata.

                Provide response ONLY in valid JSON format with these exact keys:

                {{
                    "title_options": [
                        "Positive Clickbait style title",
                        "Question-based title", 
                        "Descriptive but mysterious title"
                    ],
                    "description": "Short description (1-2 sentences)",
                    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
                    "thumbnail_suggestion": "Brief description of best thumbnail concept",
                    "caption_suggestion": "ONE short caption suggestion (max 10-12 words)",
                    "objects": ["main objects/subjects visible"],
                    "setting": "indoor/outdoor/studio/nature/urban/etc",
                    "mood": "energetic/calm/exciting/professional/fun/dramatic/etc",
                    "style": "cinematic/casual/professional/artistic/documentary/etc",
                    "viral_score": 8,
                    "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                    "angles": ["entertaining", "educational", "inspiring", "trending"],
                    "colors": ["dominant color palette"],
                    "composition": "close-up/wide-shot/medium/etc",
                    "lighting": "natural/artificial/dramatic/soft/etc",
                    "engagement_potential": "high/medium/low",
                    "target_audience": "teens/young-adults/adults/general",
                    "content_type": "dance/comedy/tutorial/lifestyle/etc",
                    "trending_elements": ["elements that could make it viral"],
                    "optimization_tips": ["specific tips for better performance"]
                }}

                Strategy: {strategy}
                Language: English
                Focus on viral potential and engagement optimization.
                """
            else:
                prompt = f"""
                Anda adalah seorang JENIUS MARKETING VIRAL dan ahli strategi konten YouTube Shorts. Tugas Anda adalah menganalisis input yang diberikan (frame visual dan mungkin transkripsi audio) untuk membuat metadata yang sangat menarik.

                Berikan respons HANYA dalam format JSON yang valid dengan kunci-kunci berikut:

                {{
                    "title_options": [
                        "Judul gaya Clickbait Positif",
                        "Judul berbentuk pertanyaan",
                        "Judul deskriptif tapi misterius"
                    ],
                    "description": "Deskripsi singkat (1-2 kalimat)",
                    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
                    "thumbnail_suggestion": "Deskripsi singkat konsep thumbnail terbaik",
                    "caption_suggestion": "SATU saran caption singkat (maksimal 10-12 kata)",
                    "objects": ["objek/subjek utama yang terlihat"],
                    "setting": "indoor/outdoor/studio/alam/urban/etc",
                    "mood": "energik/tenang/exciting/profesional/fun/dramatis/etc",
                    "style": "sinematik/kasual/profesional/artistik/dokumenter/etc",
                    "viral_score": 8,
                    "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                    "angles": ["menghibur", "edukatif", "inspiratif", "trending"],
                    "colors": ["palet warna dominan"],
                    "composition": "close-up/wide-shot/medium/etc",
                    "lighting": "natural/artificial/dramatis/lembut/etc",
                    "engagement_potential": "tinggi/sedang/rendah",
                    "target_audience": "remaja/dewasa-muda/dewasa/umum",
                    "content_type": "dance/komedi/tutorial/lifestyle/etc",
                    "trending_elements": ["elemen yang bisa membuatnya viral"],
                    "optimization_tips": ["tips spesifik untuk performa yang lebih baik"]
                }}

                Strategy: {strategy}
                Bahasa: Indonesia
                Fokus pada potensi viral dan optimasi engagement.
                """
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse response dengan improved error handling
            try:
                response_text = response.text
                
                # Clean up response text
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text.strip()
                
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
                
                analysis = json.loads(json_text)
                
                # Validate required keys
                required_keys = ["objects", "setting", "mood", "style", "viral_score", "platforms", "angles"]
                for key in required_keys:
                    if key not in analysis:
                        analysis[key] = self._get_default_value(key, language)
                
                # Add language info
                analysis["language"] = language
                
                self._log("Video analysis dengan Gemini 2.0-flash selesai", "SUCCESS")
                return analysis
                
            except (json.JSONDecodeError, AttributeError) as e:
                self._log(f"Error parsing AI response: {e}", "WARNING")
                self._log("Using enhanced fallback analysis", "INFO")
                return self._generate_enhanced_fallback_analysis(video_path, response.text if hasattr(response, 'text') else "", language)
                
        except Exception as e:
            self._log(f"Error analyzing video: {e}", "ERROR")
            return self._generate_fallback_analysis(video_path, language)

    def _get_default_value(self, key: str, language: str = "indonesian"):
        """Get default value untuk missing keys dengan language support"""
        if language == "english":
            defaults = {
                "objects": ["video content"],
                "setting": "unknown",
                "mood": "neutral",
                "style": "standard",
                "viral_score": 7,
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["entertaining", "engaging", "shareable"],
                "colors": ["mixed"],
                "composition": "medium",
                "lighting": "natural",
                "engagement_potential": "medium",
                "target_audience": "general",
                "content_type": "general",
                "trending_elements": ["engaging content"],
                "optimization_tips": ["add trending hashtags", "optimize timing"],
                "title_options": ["Amazing Content!", "What Happens Next?", "The Secret Behind This..."],
                "description": "Check out this amazing content!",
                "tags": ["viral", "trending", "amazing", "content", "video"],
                "thumbnail_suggestion": "Eye-catching thumbnail with bright colors",
                "caption_suggestion": "You won't believe what happens next!"
            }
        else:
            defaults = {
                "objects": ["konten video"],
                "setting": "tidak diketahui",
                "mood": "netral",
                "style": "standar",
                "viral_score": 7,
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["menghibur", "menarik", "shareable"],
                "colors": ["campuran"],
                "composition": "medium",
                "lighting": "natural",
                "engagement_potential": "sedang",
                "target_audience": "umum",
                "content_type": "umum",
                "trending_elements": ["konten menarik"],
                "optimization_tips": ["tambahkan hashtag trending", "optimasi waktu posting"],
                "title_options": ["Konten Menakjubkan!", "Apa yang Terjadi Selanjutnya?", "Rahasia di Balik Ini..."],
                "description": "Lihat konten menakjubkan ini!",
                "tags": ["viral", "trending", "amazing", "konten", "video"],
                "thumbnail_suggestion": "Thumbnail menarik dengan warna cerah",
                "caption_suggestion": "Kalian nggak akan percaya apa yang terjadi!"
            }
        
        return defaults.get(key, "unknown")

    def _generate_enhanced_fallback_analysis(self, video_path: str, ai_response: str = "", language: str = "indonesian") -> Dict[str, Any]:
        """Generate enhanced fallback analysis dengan partial AI response"""
        analysis = self._generate_fallback_analysis(video_path, language)
        
        # Try to extract useful info from partial AI response
        if ai_response:
            try:
                # Look for keywords in the response
                if "energetic" in ai_response.lower() or "energik" in ai_response.lower():
                    analysis["mood"] = "energetic" if language == "english" else "energik"
                elif "calm" in ai_response.lower() or "tenang" in ai_response.lower():
                    analysis["mood"] = "calm" if language == "english" else "tenang"
                elif "exciting" in ai_response.lower():
                    analysis["mood"] = "exciting"
                
                if "indoor" in ai_response.lower():
                    analysis["setting"] = "indoor"
                elif "outdoor" in ai_response.lower():
                    analysis["setting"] = "outdoor"
                
                # Extract viral score if mentioned
                import re
                score_match = re.search(r'(\d+)/10|score.*?(\d+)', ai_response.lower())
                if score_match:
                    score = int(score_match.group(1) or score_match.group(2))
                    if 1 <= score <= 10:
                        analysis["viral_score"] = score
                        
            except Exception:
                pass
        
        return analysis

    def _generate_fallback_analysis(self, video_path: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback analysis jika AI tidak tersedia"""
        if language == "english":
            return {
                "objects": ["video content"],
                "setting": "unknown",
                "mood": "neutral",
                "style": "standard",
                "viral_score": 7,
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["entertaining", "engaging", "shareable"],
                "colors": ["mixed"],
                "composition": "medium",
                "lighting": "natural",
                "engagement_potential": "medium",
                "target_audience": "general",
                "content_type": "general",
                "trending_elements": ["engaging content"],
                "optimization_tips": ["add trending hashtags", "optimize posting time"],
                "title_options": ["Amazing Content!", "What Happens Next?", "The Secret Behind This..."],
                "description": "Check out this amazing content!",
                "tags": ["viral", "trending", "amazing", "content", "video"],
                "thumbnail_suggestion": "Eye-catching thumbnail with bright colors",
                "caption_suggestion": "You won't believe what happens next!",
                "language": language
            }
        else:
            return {
                "objects": ["konten video"],
                "setting": "tidak diketahui",
                "mood": "netral",
                "style": "standar",
                "viral_score": 7,
                "platforms": ["tiktok", "instagram", "youtube", "facebook"],
                "angles": ["menghibur", "menarik", "shareable"],
                "colors": ["campuran"],
                "composition": "medium",
                "lighting": "natural",
                "engagement_potential": "sedang",
                "target_audience": "umum",
                "content_type": "umum",
                "trending_elements": ["konten menarik"],
                "optimization_tips": ["tambahkan hashtag trending", "optimasi waktu posting"],
                "title_options": ["Konten Menakjubkan!", "Apa yang Terjadi Selanjutnya?", "Rahasia di Balik Ini..."],
                "description": "Lihat konten menakjubkan ini!",
                "tags": ["viral", "trending", "amazing", "konten", "video"],
                "thumbnail_suggestion": "Thumbnail menarik dengan warna cerah",
                "caption_suggestion": "Kalian nggak akan percaya apa yang terjadi!",
                "language": language
            }

    def generate_platform_content(self, analysis: Dict[str, Any], platforms: List[str], 
                                strategy: str = "balanced", language: str = None) -> Dict[str, Any]:
        """Generate content untuk setiap platform berdasarkan analysis dengan Gemini 2.0-flash dan language support"""
        if not self.model:
            return self._generate_fallback_content(platforms, language or "indonesian")
        
        # Get language preference if not provided
        if not language:
            language = self.get_language_preference("platform content generation")
        
        try:
            content = {}
            
            for platform in platforms:
                self._log(f"Generating content untuk {platform} dengan Gemini 2.0-flash ({language})...", "AI")
                
                # Enhanced VIRAL MARKETING GENIUS prompt dengan language support
                if language == "english":
                    prompt = f"""
                    You are a VIRAL MARKETING GENIUS and expert social media strategist. Create highly engaging content for {platform} based on this video analysis:
                    {json.dumps(analysis, indent=2)}
                    
                    Strategy: {strategy}
                    Platform: {platform}
                    Language: English
                    
                    Generate platform-optimized content in JSON format:
                    
                    {{
                        "title_options": [
                            "Positive Clickbait style title",
                            "Question-based title",
                            "Descriptive but mysterious title"
                        ],
                        "title": "best title from options above",
                        "description": "engaging description with relevant hashtags",
                        "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                        "cta": "compelling call-to-action",
                        "best_time": "optimal posting time",
                        "hook": "attention-grabbing opening line",
                        "keywords": ["SEO keywords for discoverability"],
                        "engagement_tactics": ["specific tactics to boost engagement"],
                        "trending_hooks": ["trending phrases or formats to use"],
                        "thumbnail_suggestion": "brief description of best thumbnail concept",
                        "caption_suggestion": "ONE short caption (max 10-12 words)"
                    }}
                    
                    Platform-specific optimization:
                    - TikTok: Viral, trendy, youth-focused, max 150 chars title, trending sounds/effects
                    - Instagram: Aesthetic, visual storytelling, lifestyle, max 125 chars title, story-worthy
                    - YouTube: SEO-optimized, searchable, educational value, max 100 chars title, retention-focused
                    - Facebook: Community-focused, shareable, conversation-starter, max 255 chars title
                    
                    Make it highly engaging and platform-native. Use current trends and viral formats.
                    """
                else:
                    prompt = f"""
                    Anda adalah seorang JENIUS MARKETING VIRAL dan ahli strategi konten sosial media. Buat konten yang sangat menarik untuk {platform} berdasarkan analisis video ini:
                    {json.dumps(analysis, indent=2)}
                    
                    Strategy: {strategy}
                    Platform: {platform}
                    Bahasa: Indonesia
                    
                    Generate konten yang dioptimasi untuk platform dalam format JSON:
                    
                    {{
                        "title_options": [
                            "Judul gaya Clickbait Positif",
                            "Judul berbentuk pertanyaan",
                            "Judul deskriptif tapi misterius"
                        ],
                        "title": "judul terbaik dari opsi di atas",
                        "description": "deskripsi menarik dengan hashtag yang relevan",
                        "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                        "cta": "call-to-action yang compelling",
                        "best_time": "waktu posting optimal",
                        "hook": "kalimat pembuka yang menarik perhatian",
                        "keywords": ["kata kunci SEO untuk discoverability"],
                        "engagement_tactics": ["taktik spesifik untuk boost engagement"],
                        "trending_hooks": ["frasa atau format trending yang bisa digunakan"],
                        "thumbnail_suggestion": "deskripsi singkat konsep thumbnail terbaik",
                        "caption_suggestion": "SATU caption singkat (maksimal 10-12 kata)"
                    }}
                    
                    Optimasi spesifik platform:
                    - TikTok: Viral, trendy, youth-focused, max 150 karakter judul, trending sounds/effects
                    - Instagram: Aesthetic, visual storytelling, lifestyle, max 125 karakter judul, story-worthy
                    - YouTube: SEO-optimized, searchable, educational value, max 100 karakter judul, retention-focused
                    - Facebook: Community-focused, shareable, conversation-starter, max 255 karakter judul
                    
                    Buat konten yang sangat engaging dan platform-native. Gunakan trend terkini dan format viral.
                    """
                
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text
                    
                    # Enhanced JSON extraction
                    if "```json" in response_text:
                        json_start = response_text.find("```json") + 7
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif "```" in response_text:
                        json_start = response_text.find("```") + 3
                        json_end = response_text.find("```", json_start)
                        json_text = response_text[json_start:json_end].strip()
                    else:
                        # Try to find JSON object in response
                        import re
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            json_text = json_match.group()
                        else:
                            json_text = response_text
                    
                    platform_content = json.loads(json_text)
                    
                    # Validate and add missing keys
                    required_keys = ["title", "description", "cta", "best_time"]
                    for key in required_keys:
                        if key not in platform_content:
                            platform_content[key] = self._get_default_platform_value(key, platform, language)
                    
                    # Add language info
                    platform_content["language"] = language
                    
                    content[platform] = platform_content
                    
                except (json.JSONDecodeError, Exception) as e:
                    self._log(f"Error generating content for {platform}: {e}", "WARNING")
                    content[platform] = self._generate_fallback_platform_content(platform, language)
            
            self._log("Content generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return content
            
        except Exception as e:
            self._log(f"Error generating platform content: {e}", "ERROR")
            return self._generate_fallback_content(platforms, language)

    def _get_default_platform_value(self, key: str, platform: str, language: str = "indonesian"):
        """Get default value untuk platform content dengan language support"""
        if language == "english":
            defaults = {
                "title": f"Amazing Content for {platform.title()}!",
                "description": f"Check out this amazing content! Perfect for {platform}. #viral #trending",
                "cta": "Like and share if you enjoyed this!",
                "best_time": "19:00-21:00",
                "hook": "You won't believe what happens next!",
                "hashtags": [f"#{platform}", "#viral", "#trending"],
                "keywords": ["viral", "trending", "amazing"],
                "engagement_tactics": ["ask questions", "use trending hashtags"],
                "trending_hooks": ["POV:", "This is why", "Wait for it"]
            }
        else:
            defaults = {
                "title": f"Konten Menakjubkan untuk {platform.title()}!",
                "description": f"Lihat konten menakjubkan ini! Sempurna untuk {platform}. #viral #trending",
                "cta": "Like dan share jika kalian suka!",
                "best_time": "19:00-21:00",
                "hook": "Kalian nggak akan percaya apa yang terjadi!",
                "hashtags": [f"#{platform}", "#viral", "#trending"],
                "keywords": ["viral", "trending", "menakjubkan"],
                "engagement_tactics": ["ajukan pertanyaan", "gunakan hashtag trending"],
                "trending_hooks": ["POV:", "Inilah mengapa", "Tunggu dulu"]
            }
        
        return defaults.get(key, "")

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
                    "title_options": ["This Video Will Blow Your Mind! 🔥", "Why Is Everyone Talking About This?", "The Secret Behind Viral Content..."],
                    "title": "This Video Will Blow Your Mind! 🔥",
                    "description": "Content you NEED to watch! Tag your friends who need to see this! 🤯",
                    "hashtags": ["#fyp", "#viral", "#trending", "#amazing", "#wow", "#foryou", "#tiktok"],
                    "cta": "Follow for more viral content!",
                    "best_time": "19:00-21:00",
                    "hook": "POV: You found the best content today",
                    "keywords": ["viral", "trending", "fyp"],
                    "engagement_tactics": ["use trending sounds", "add text overlay", "quick cuts"],
                    "trending_hooks": ["POV:", "Wait for it", "This is why"],
                    "thumbnail_suggestion": "Bright colors with shocked expression",
                    "caption_suggestion": "You won't believe what happens next!",
                    "language": language
                },
                "instagram": {
                    "title_options": ["This Changed Everything! ✨", "Why Everyone's Obsessed With This", "The Story Behind This Viral Moment"],
                    "title": "This Changed Everything! ✨",
                    "description": "Video you MUST save! Tag your bestie in comments and share to story! 💫",
                    "hashtags": ["#viral", "#instagram", "#reels", "#amazing", "#content", "#trending", "#explore"],
                    "cta": "Save and share to your story!",
                    "best_time": "20:00-22:00",
                    "hook": "This will change your perspective",
                    "keywords": ["aesthetic", "lifestyle", "inspiration"],
                    "engagement_tactics": ["use trending audio", "add captions", "story polls"],
                    "trending_hooks": ["Get ready with me", "Day in my life", "Things I wish I knew"],
                    "thumbnail_suggestion": "Aesthetic layout with good lighting",
                    "caption_suggestion": "This will change how you see everything",
                    "language": language
                },
                "youtube": {
                    "title_options": ["This Video Will Shock You!", "The Truth About This Trend", "What Happens When You Try This"],
                    "title": "This Video Will Shock You!",
                    "description": "Watch this incredible video till the end! Don't forget to subscribe, like, and share to support this channel. Comment your thoughts below! 🎬",
                    "hashtags": ["#Shorts", "#viral", "#amazing", "#youtube", "#trending", "#subscribe"],
                    "cta": "Subscribe for more amazing content!",
                    "best_time": "18:00-20:00",
                    "hook": "In this video, you'll discover something incredible",
                    "keywords": ["tutorial", "how to", "amazing", "incredible"],
                    "engagement_tactics": ["ask for comments", "create series", "use end screens"],
                    "trending_hooks": ["You won't believe", "The secret to", "What happens when"],
                    "thumbnail_suggestion": "Bold text with contrasting colors",
                    "caption_suggestion": "The secret everyone's talking about",
                    "language": language
                },
                "facebook": {
                    "title_options": ["This Will Make You Think Differently!", "What Do You Think About This?", "Share If You Agree With This"],
                    "title": "This Will Make You Think Differently!",
                    "description": "This video is absolutely incredible! Don't forget to like, comment, and share with your friends. What's your opinion about this? 🤔",
                    "hashtags": ["#viral", "#amazing", "#video", "#facebook", "#reels", "#share"],
                    "cta": "Share with your friends!",
                    "best_time": "19:00-21:00",
                    "hook": "This will make you think differently",
                    "keywords": ["community", "discussion", "share"],
                    "engagement_tactics": ["ask questions", "create polls", "encourage sharing"],
                    "trending_hooks": ["What do you think about", "Share if you agree", "Tag someone who"],
                    "thumbnail_suggestion": "Clear image with engaging text",
                    "caption_suggestion": "What's your take on this?",
                    "language": language
                }
            }
        else:
            base_content = {
                "tiktok": {
                    "title_options": ["Video Viral yang Menakjubkan! 🔥", "Kenapa Semua Orang Bahas Ini?", "Rahasia di Balik Konten Viral..."],
                    "title": "Video Viral yang Menakjubkan! 🔥",
                    "description": "Content yang wajib kalian tonton! Tag teman kalian yang perlu lihat ini! 🤯",
                    "hashtags": ["#fyp", "#viral", "#trending", "#amazing", "#wow", "#foryou", "#tiktok"],
                    "cta": "Follow untuk konten viral lainnya!",
                    "best_time": "19:00-21:00",
                    "hook": "POV: Kamu menemukan konten terbaik hari ini",
                    "keywords": ["viral", "trending", "fyp"],
                    "engagement_tactics": ["gunakan trending sounds", "tambah text overlay", "quick cuts"],
                    "trending_hooks": ["POV:", "Tunggu dulu", "Inilah mengapa"],
                    "thumbnail_suggestion": "Warna cerah dengan ekspresi terkejut",
                    "caption_suggestion": "Kalian nggak akan percaya apa yang terjadi!",
                    "language": language
                },
                "instagram": {
                    "title_options": ["Ini Mengubah Segalanya! ✨", "Kenapa Semua Orang Obsesi Sama Ini", "Cerita di Balik Momen Viral Ini"],
                    "title": "Ini Mengubah Segalanya! ✨",
                    "description": "Video yang wajib kalian save! Tag bestie kalian di komentar dan share ke story! 💫",
                    "hashtags": ["#viral", "#instagram", "#reels", "#amazing", "#content", "#trending", "#explore"],
                    "cta": "Save dan share ke story kalian!",
                    "best_time": "20:00-22:00",
                    "hook": "Ini akan mengubah perspektif kalian",
                    "keywords": ["aesthetic", "lifestyle", "inspirasi"],
                    "engagement_tactics": ["gunakan trending audio", "tambah caption", "story polls"],
                    "trending_hooks": ["Get ready with me", "Day in my life", "Hal yang ingin aku tahu"],
                    "thumbnail_suggestion": "Layout aesthetic dengan pencahayaan bagus",
                    "caption_suggestion": "Ini akan mengubah cara kalian melihat semuanya",
                    "language": language
                },
                "youtube": {
                    "title_options": ["Video Ini Akan Mengejutkan Kalian!", "Kebenaran Tentang Trend Ini", "Apa Yang Terjadi Kalau Coba Ini"],
                    "title": "Video Ini Akan Mengejutkan Kalian!",
                    "description": "Tonton video menakjubkan ini sampai habis! Jangan lupa subscribe, like, dan share untuk mendukung channel ini. Komentar pendapat kalian di bawah! 🎬",
                    "hashtags": ["#Shorts", "#viral", "#amazing", "#youtube", "#trending", "#subscribe"],
                    "cta": "Subscribe untuk konten menakjubkan lainnya!",
                    "best_time": "18:00-20:00",
                    "hook": "Di video ini, kalian akan menemukan sesuatu yang luar biasa",
                    "keywords": ["tutorial", "cara", "menakjubkan", "luar biasa"],
                    "engagement_tactics": ["minta komentar", "buat series", "gunakan end screens"],
                    "trending_hooks": ["Kalian nggak akan percaya", "Rahasia dari", "Apa yang terjadi kalau"],
                    "thumbnail_suggestion": "Teks tebal dengan warna kontras",
                    "caption_suggestion": "Rahasia yang semua orang bicarakan",
                    "language": language
                },
                "facebook": {
                    "title_options": ["Ini Akan Mengubah Cara Berpikir Kalian!", "Apa Pendapat Kalian Tentang Ini?", "Share Kalau Setuju Sama Ini"],
                    "title": "Ini Akan Mengubah Cara Berpikir Kalian!",
                    "description": "Video ini benar-benar luar biasa! Jangan lupa like, comment, dan share ke teman-teman kalian. Apa pendapat kalian tentang ini? 🤔",
                    "hashtags": ["#viral", "#amazing", "#video", "#facebook", "#reels", "#share"],
                    "cta": "Share ke teman-teman kalian!",
                    "best_time": "19:00-21:00",
                    "hook": "Ini akan mengubah cara berpikir kalian",
                    "keywords": ["komunitas", "diskusi", "share"],
                    "engagement_tactics": ["ajukan pertanyaan", "buat polling", "dorong sharing"],
                    "trending_hooks": ["Apa pendapat kalian tentang", "Share kalau setuju", "Tag seseorang yang"],
                    "thumbnail_suggestion": "Gambar jelas dengan teks menarik",
                    "caption_suggestion": "Apa pendapat kalian tentang ini?",
                    "language": language
                }
            }
        
        return base_content.get(platform, base_content["tiktok"])

    def generate_text_post(self, topic: str, platform: str, style: str = "engaging", language: str = None) -> Dict[str, Any]:
        """Generate text post berdasarkan topik dengan Gemini 2.0-flash dan language support"""
        if not self.model:
            return self._generate_fallback_text_post(topic, platform, language or "indonesian")
        
        # Get language preference if not provided
        if not language:
            language = self.get_language_preference("text post generation")
        
        try:
            self._log(f"Generating text post untuk {platform} dengan topik: {topic} ({language})", "AI")
            
            # Enhanced VIRAL MARKETING GENIUS prompt dengan language support
            if language == "english":
                prompt = f"""
                You are a VIRAL MARKETING GENIUS and expert social media strategist. Create a highly engaging text post for {platform} about: {topic}
                Style: {style}
                Language: English
                
                Generate compelling content in JSON format:
                
                {{
                    "title_options": [
                        "Positive Clickbait style title",
                        "Question-based title",
                        "Descriptive but mysterious title"
                    ],
                    "title": "best title from options above",
                    "content": "engaging post content with storytelling",
                    "hashtags": ["#relevant", "#trending", "#hashtags"],
                    "cta": "compelling call-to-action",
                    "hook": "opening line that stops scrolling",
                    "engagement_questions": ["questions to boost comments"],
                    "trending_elements": ["current trends to incorporate"],
                    "emotional_triggers": ["emotions this post evokes"],
                    "thumbnail_suggestion": "brief description of visual concept",
                    "caption_suggestion": "ONE short caption (max 10-12 words)"
                }}
                
                Platform-specific requirements:
                - TikTok: Casual, trendy, youth-focused, use trending slang
                - Instagram: Aesthetic, lifestyle, inspirational, visual storytelling
                - YouTube: Informative, searchable, community-building, educational value
                - Facebook: Conversational, community-focused, discussion-starter, shareable
                
                Make it authentic, relatable, and highly engaging. Use current trends and viral formats.
                Include storytelling elements and emotional hooks.
                """
            else:
                prompt = f"""
                Anda adalah seorang JENIUS MARKETING VIRAL dan ahli strategi sosial media. Buat text post yang sangat menarik untuk {platform} tentang: {topic}
                Style: {style}
                Bahasa: Indonesia
                
                Generate konten yang compelling dalam format JSON:
                
                {{
                    "title_options": [
                        "Judul gaya Clickbait Positif",
                        "Judul berbentuk pertanyaan",
                        "Judul deskriptif tapi misterius"
                    ],
                    "title": "judul terbaik dari opsi di atas",
                    "content": "konten post yang menarik dengan storytelling",
                    "hashtags": ["#relevan", "#trending", "#hashtags"],
                    "cta": "call-to-action yang compelling",
                    "hook": "kalimat pembuka yang menghentikan scrolling",
                    "engagement_questions": ["pertanyaan untuk boost komentar"],
                    "trending_elements": ["trend terkini yang bisa dimasukkan"],
                    "emotional_triggers": ["emosi yang dibangkitkan post ini"],
                    "thumbnail_suggestion": "deskripsi singkat konsep visual",
                    "caption_suggestion": "SATU caption singkat (maksimal 10-12 kata)"
                }}
                
                Requirements spesifik platform:
                - TikTok: Kasual, trendy, youth-focused, gunakan slang trending
                - Instagram: Aesthetic, lifestyle, inspirational, visual storytelling
                - YouTube: Informatif, searchable, community-building, educational value
                - Facebook: Conversational, community-focused, discussion-starter, shareable
                
                Buat konten yang autentik, relatable, dan sangat engaging. Gunakan trend terkini dan format viral.
                Sertakan elemen storytelling dan emotional hooks.
                """
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON dengan improved parsing
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
                else:
                    json_text = response_text
            
            post_content = json.loads(json_text)
            
            # Validate required keys
            required_keys = ["title", "content", "hashtags", "cta"]
            for key in required_keys:
                if key not in post_content:
                    post_content[key] = self._get_default_text_value(key, topic, platform, language)
            
            # Add language info
            post_content["language"] = language
            
            self._log("Text post generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return post_content
            
        except Exception as e:
            self._log(f"Error generating text post: {e}", "ERROR")
            return self._generate_fallback_text_post(topic, platform, language)

    def _get_default_text_value(self, key: str, topic: str, platform: str, language: str = "indonesian"):
        """Get default value untuk text post dengan language support"""
        if language == "english":
            defaults = {
                "title": f"Essential {topic} Tips You Need to Know!",
                "content": f"Check out these amazing {topic} tips! Don't forget to try them and share your experience in the comments.",
                "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
                "cta": "Share your experience in the comments!",
                "hook": f"Here's the {topic} secret everyone's talking about",
                "engagement_questions": [f"What's your experience with {topic}?"],
                "trending_elements": ["storytelling", "personal experience"],
                "emotional_triggers": ["curiosity", "excitement"]
            }
        else:
            defaults = {
                "title": f"Tips {topic} yang Wajib Diketahui!",
                "content": f"Simak tips {topic} yang sangat berguna ini! Jangan lupa untuk mencoba dan share pengalaman kalian di komentar.",
                "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
                "cta": "Share pengalaman kalian di komentar!",
                "hook": f"Inilah rahasia {topic} yang jarang diketahui",
                "engagement_questions": [f"Apa pengalaman kalian dengan {topic}?"],
                "trending_elements": ["storytelling", "pengalaman personal"],
                "emotional_triggers": ["rasa penasaran", "excitement"]
            }
        
        return defaults.get(key, "")

    def _generate_fallback_text_post(self, topic: str, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback text post dengan language support"""
        if language == "english":
            return {
                "title_options": [f"Amazing {topic} Tips!", f"Why Is {topic} So Important?", f"The Secret Behind {topic}..."],
                "title": f"Essential {topic} Tips You Need to Know!",
                "content": f"Check out these amazing {topic} tips! Don't forget to try them and share your experience in the comments.",
                "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
                "cta": "Share your experience in the comments!",
                "hook": f"Here's the {topic} secret everyone's talking about",
                "engagement_questions": [f"What's your experience with {topic}?"],
                "trending_elements": ["storytelling", "personal experience"],
                "emotional_triggers": ["curiosity", "excitement"],
                "thumbnail_suggestion": f"Clean design highlighting {topic}",
                "caption_suggestion": f"The {topic} game-changer you need",
                "language": language
            }
        else:
            return {
                "title_options": [f"Tips {topic} yang Menakjubkan!", f"Kenapa {topic} Itu Penting?", f"Rahasia di Balik {topic}..."],
                "title": f"Tips {topic} yang Wajib Diketahui!",
                "content": f"Simak tips {topic} yang sangat berguna ini! Jangan lupa untuk mencoba dan share pengalaman kalian di komentar.",
                "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
                "cta": "Share pengalaman kalian di komentar!",
                "hook": f"Inilah rahasia {topic} yang jarang diketahui",
                "engagement_questions": [f"Apa pengalaman kalian dengan {topic}?"],
                "trending_elements": ["storytelling", "pengalaman personal"],
                "emotional_triggers": ["rasa penasaran", "excitement"],
                "thumbnail_suggestion": f"Desain bersih yang highlight {topic}",
                "caption_suggestion": f"Game-changer {topic} yang kalian butuhkan",
                "language": language
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

    def check_api_status(self):
        """Check Gemini API status dengan model 2.0-flash"""
        self._log("Checking Gemini API status...", "INFO")
        
        # Load .env file
        self._load_env_file()
        
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            self._log("❌ GEMINI_API_KEY tidak ditemukan", "ERROR")
            self._log("Buat file .env dengan isi:", "INFO")
            self._log("GEMINI_API_KEY=your_api_key_here", "INFO")
            return False
        
        if not GENAI_AVAILABLE:
            self._log("❌ google-generativeai tidak terinstall", "ERROR")
            self._log("Install dengan: pip install google-generativeai", "INFO")
            return False
        
        try:
            genai.configure(api_key=api_key)
            
            # Test dengan model 2.0-flash
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content("Hello, test connection")
                
                self._log("✅ Gemini 2.0-flash API working correctly", "SUCCESS")
                self._log("🚀 Model: gemini-2.0-flash-exp (Latest & Most Powerful)", "AI")
                self._log("🌍 Language Support: Indonesia & English", "AI")
                return True
                
            except Exception as e:
                self._log(f"⚠️ Gemini 2.0-flash not available: {e}", "WARNING")
                self._log("Trying fallback to gemini-pro...", "INFO")
                
                # Fallback test
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Hello, test connection")
                
                self._log("✅ Gemini Pro API working (fallback)", "SUCCESS")
                self._log("🌍 Language Support: Indonesia & English", "AI")
                return True
            
        except Exception as e:
            self._log(f"❌ Gemini API error: {e}", "ERROR")
            return False

    def interactive_ai_menu(self):
        """Interactive AI assistant menu dengan Gemini 2.0-flash dan language support"""
        if not GENAI_AVAILABLE:
            print(f"{Fore.RED}❌ google-generativeai tidak tersedia!")
            print(f"{Fore.YELLOW}Install dengan: pip install google-generativeai")
            return
        
        if not self.model:
            print(f"{Fore.RED}❌ Gemini AI tidak tersedia!")
            print(f"{Fore.YELLOW}Buat file .env dengan GEMINI_API_KEY=your_api_key")
            return
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}🤖 Gemini AI Assistant 2.0-flash")
        print("=" * 50)
        print(f"{Fore.CYAN}🚀 Powered by gemini-2.0-flash-exp (Latest Model)")
        print(f"{Fore.CYAN}🌍 Language Support: Indonesia & English")
        print(f"{Fore.CYAN}🎯 VIRAL MARKETING GENIUS Mode")
        print()
        
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
                    strategy = input(f"{Fore.CYAN}Strategy (viral/quality/speed/balanced): ").strip() or "balanced"
                    analysis = self.analyze_video_content(video_path, strategy)
                    
                    print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS (Gemini 2.0-flash):")
                    print(f"Language: {analysis.get('language', 'indonesian')}")
                    if analysis.get('title_options'):
                        print(f"Title Options: {', '.join(analysis['title_options'])}")
                    print(f"Objects: {', '.join(analysis.get('objects', []))}")
                    print(f"Setting: {analysis.get('setting', 'unknown')}")
                    print(f"Mood: {analysis.get('mood', 'neutral')}")
                    print(f"Style: {analysis.get('style', 'standard')}")
                    print(f"Viral Score: {analysis.get('viral_score', 'N/A')}/10")
                    print(f"Best Platforms: {', '.join(analysis.get('platforms', []))}")
                    print(f"Content Type: {analysis.get('content_type', 'general')}")
                    print(f"Target Audience: {analysis.get('target_audience', 'general')}")
                    if analysis.get('caption_suggestion'):
                        print(f"Caption Suggestion: {analysis['caption_suggestion']}")
                    if analysis.get('optimization_tips'):
                        print(f"Optimization Tips: {', '.join(analysis['optimization_tips'])}")
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "2":
                topic = input(f"{Fore.CYAN}Topik: ").strip()
                platform = input(f"{Fore.CYAN}Platform (tiktok/instagram/youtube/facebook): ").strip()
                if topic and platform:
                    post = self.generate_text_post(topic, platform)
                    
                    print(f"\n{Fore.GREEN}📝 GENERATED POST (Gemini 2.0-flash):")
                    print(f"Language: {post.get('language', 'indonesian')}")
                    if post.get('title_options'):
                        print(f"Title Options: {', '.join(post['title_options'])}")
                    print(f"Title: {post.get('title', 'N/A')}")
                    print(f"Content: {post.get('content', 'N/A')}")
                    print(f"Hashtags: {', '.join(post.get('hashtags', []))}")
                    print(f"CTA: {post.get('cta', 'N/A')}")
                    if post.get('hook'):
                        print(f"Hook: {post['hook']}")
                    if post.get('caption_suggestion'):
                        print(f"Caption Suggestion: {post['caption_suggestion']}")
                    if post.get('engagement_questions'):
                        print(f"Engagement Questions: {', '.join(post['engagement_questions'])}")
                else:
                    print(f"{Fore.RED}❌ Topik dan platform harus diisi!")
            
            elif choice == "3":
                video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
                if os.path.exists(video_path):
                    platforms = input(f"{Fore.CYAN}Platforms (comma separated): ").strip().split(',')
                    platforms = [p.strip() for p in platforms if p.strip()]
                    
                    if platforms:
                        analysis = self.analyze_video_content(video_path)
                        content = self.generate_platform_content(analysis, platforms)
                        
                        print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT (Gemini 2.0-flash):")
                        for platform, platform_content in content.items():
                            print(f"\n{platform.upper()}:")
                            print(f"  Language: {platform_content.get('language', 'indonesian')}")
                            if platform_content.get('title_options'):
                                print(f"  Title Options: {', '.join(platform_content['title_options'])}")
                            print(f"  Title: {platform_content.get('title', 'N/A')}")
                            print(f"  Description: {platform_content.get('description', 'N/A')[:100]}...")
                            print(f"  Hashtags: {', '.join(platform_content.get('hashtags', []))}")
                            print(f"  CTA: {platform_content.get('cta', 'N/A')}")
                            if platform_content.get('hook'):
                                print(f"  Hook: {platform_content['hook']}")
                            if platform_content.get('caption_suggestion'):
                                print(f"  Caption: {platform_content['caption_suggestion']}")
                    else:
                        print(f"{Fore.RED}❌ Minimal satu platform harus dipilih!")
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "4":
                self.check_api_status()
            
            elif choice == "5":
                self.cleanup_temp_files()
            
            elif choice == "6":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="Gemini AI Assistant 2.0-flash dengan Language Support")
    parser.add_argument("--video", "-v", help="Path ke video untuk analisis")
    parser.add_argument("--topic", "-t", help="Topik untuk text post")
    parser.add_argument("--platform", "-p", help="Platform target")
    parser.add_argument("--strategy", "-s", choices=['viral', 'quality', 'speed', 'balanced'], 
                       default='balanced', help="Content strategy")
    parser.add_argument("--language", "-l", choices=['indonesian', 'english'], 
                       help="Language for content generation")
    parser.add_argument("--check-api", action="store_true", help="Check API status")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    assistant = GeminiAIAssistant(debug=args.debug)
    
    if args.check_api:
        assistant.check_api_status()
        return
    
    if args.video:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ Video file not found: {args.video}")
            sys.exit(1)
        
        analysis = assistant.analyze_video_content(args.video, args.strategy, args.language)
        print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS (Gemini 2.0-flash):")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]
            content = assistant.generate_platform_content(analysis, platforms, args.strategy, args.language)
            print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
    
    elif args.topic and args.platform:
        post = assistant.generate_text_post(args.topic, args.platform, language=args.language)
        print(f"\n{Fore.GREEN}📝 GENERATED POST (Gemini 2.0-flash):")
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