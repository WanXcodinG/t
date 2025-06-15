#!/usr/bin/env python3
"""
Gemini AI Assistant untuk Social Media Content Generation
Menggunakan Google Gemini AI 2.0-flash untuk analisis video dan generate konten
Enhanced dengan model terbaru untuk performa yang lebih baik
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

    def analyze_video_content(self, video_path: str, strategy: str = "balanced") -> Dict[str, Any]:
        """Analyze video content menggunakan Gemini 2.0-flash"""
        if not self.vision_model:
            self._log("Gemini AI tidak tersedia", "ERROR")
            return self._generate_fallback_analysis(video_path)
        
        try:
            # Extract frames
            frames = self.extract_video_frames(video_path, num_frames=3)
            if not frames:
                return self._generate_fallback_analysis(video_path)
            
            self._log("Menganalisis konten video dengan Gemini 2.0-flash...", "AI")
            
            # Analyze first frame dengan prompt yang lebih advanced
            image = Image.open(frames[0])
            
            # Enhanced prompt untuk model 2.0-flash
            prompt = f"""
            Analyze this video frame for social media content optimization.
            Strategy: {strategy}
            
            Provide comprehensive analysis in JSON format with these exact keys:
            
            {{
                "objects": ["list of main objects/subjects visible"],
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
            
            Be specific and actionable in your analysis. Focus on elements that drive social media engagement.
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
                        analysis[key] = self._get_default_value(key)
                
                self._log("Video analysis dengan Gemini 2.0-flash selesai", "SUCCESS")
                return analysis
                
            except (json.JSONDecodeError, AttributeError) as e:
                self._log(f"Error parsing AI response: {e}", "WARNING")
                self._log("Using enhanced fallback analysis", "INFO")
                return self._generate_enhanced_fallback_analysis(video_path, response.text if hasattr(response, 'text') else "")
                
        except Exception as e:
            self._log(f"Error analyzing video: {e}", "ERROR")
            return self._generate_fallback_analysis(video_path)

    def _get_default_value(self, key: str):
        """Get default value untuk missing keys"""
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
            "optimization_tips": ["add trending hashtags", "optimize timing"]
        }
        return defaults.get(key, "unknown")

    def _generate_enhanced_fallback_analysis(self, video_path: str, ai_response: str = "") -> Dict[str, Any]:
        """Generate enhanced fallback analysis dengan partial AI response"""
        analysis = self._generate_fallback_analysis(video_path)
        
        # Try to extract useful info from partial AI response
        if ai_response:
            try:
                # Look for keywords in the response
                if "energetic" in ai_response.lower():
                    analysis["mood"] = "energetic"
                elif "calm" in ai_response.lower():
                    analysis["mood"] = "calm"
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

    def _generate_fallback_analysis(self, video_path: str) -> Dict[str, Any]:
        """Generate fallback analysis jika AI tidak tersedia"""
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
            "optimization_tips": ["add trending hashtags", "optimize posting time"]
        }

    def generate_platform_content(self, analysis: Dict[str, Any], platforms: List[str], 
                                strategy: str = "balanced") -> Dict[str, Any]:
        """Generate content untuk setiap platform berdasarkan analysis dengan Gemini 2.0-flash"""
        if not self.model:
            return self._generate_fallback_content(platforms)
        
        try:
            content = {}
            
            for platform in platforms:
                self._log(f"Generating content untuk {platform} dengan Gemini 2.0-flash...", "AI")
                
                # Enhanced prompt untuk model 2.0-flash
                prompt = f"""
                Create highly engaging social media content for {platform} based on this video analysis:
                {json.dumps(analysis, indent=2)}
                
                Strategy: {strategy}
                Platform: {platform}
                
                Generate platform-optimized content in JSON format:
                
                {{
                    "title": "catchy title optimized for {platform}",
                    "description": "engaging description with relevant hashtags",
                    "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
                    "cta": "compelling call-to-action",
                    "best_time": "optimal posting time",
                    "hook": "attention-grabbing opening line",
                    "keywords": ["SEO keywords for discoverability"],
                    "engagement_tactics": ["specific tactics to boost engagement"],
                    "trending_hooks": ["trending phrases or formats to use"]
                }}
                
                Platform-specific optimization:
                - TikTok: Viral, trendy, youth-focused, max 150 chars title, trending sounds/effects
                - Instagram: Aesthetic, visual storytelling, lifestyle, max 125 chars title, story-worthy
                - YouTube: SEO-optimized, searchable, educational value, max 100 chars title, retention-focused
                - Facebook: Community-focused, shareable, conversation-starter, max 255 chars title
                
                Make it highly engaging and platform-native. Use current trends and viral formats.
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
                            platform_content[key] = self._get_default_platform_value(key, platform)
                    
                    content[platform] = platform_content
                    
                except (json.JSONDecodeError, Exception) as e:
                    self._log(f"Error generating content for {platform}: {e}", "WARNING")
                    content[platform] = self._generate_fallback_platform_content(platform)
            
            self._log("Content generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return content
            
        except Exception as e:
            self._log(f"Error generating platform content: {e}", "ERROR")
            return self._generate_fallback_content(platforms)

    def _get_default_platform_value(self, key: str, platform: str):
        """Get default value untuk platform content"""
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
        return defaults.get(key, "")

    def _generate_fallback_content(self, platforms: List[str]) -> Dict[str, Any]:
        """Generate fallback content"""
        content = {}
        for platform in platforms:
            content[platform] = self._generate_fallback_platform_content(platform)
        return content

    def _generate_fallback_platform_content(self, platform: str) -> Dict[str, Any]:
        """Generate fallback content untuk platform tertentu"""
        base_content = {
            "tiktok": {
                "title": "Video Viral yang Menakjubkan! 🔥",
                "description": "Content yang wajib kalian tonton! Tag teman kalian yang perlu lihat ini! 🤯",
                "hashtags": ["#fyp", "#viral", "#trending", "#amazing", "#wow", "#foryou", "#tiktok"],
                "cta": "Follow untuk konten viral lainnya!",
                "best_time": "19:00-21:00",
                "hook": "POV: Kamu menemukan konten terbaik hari ini",
                "keywords": ["viral", "trending", "fyp"],
                "engagement_tactics": ["use trending sounds", "add text overlay", "quick cuts"],
                "trending_hooks": ["POV:", "Wait for it", "This is why"]
            },
            "instagram": {
                "title": "Content yang Luar Biasa! ✨",
                "description": "Video yang wajib kalian save! Tag bestie kalian di komentar dan share ke story! 💫",
                "hashtags": ["#viral", "#instagram", "#reels", "#amazing", "#content", "#trending", "#explore"],
                "cta": "Save dan share ke story kalian!",
                "best_time": "20:00-22:00",
                "hook": "This will change your perspective",
                "keywords": ["aesthetic", "lifestyle", "inspiration"],
                "engagement_tactics": ["use trending audio", "add captions", "story polls"],
                "trending_hooks": ["Get ready with me", "Day in my life", "Things I wish I knew"]
            },
            "youtube": {
                "title": "Video Viral yang Akan Mengejutkan Anda!",
                "description": "Tonton video menakjubkan ini sampai habis! Jangan lupa subscribe, like, dan share untuk mendukung channel ini. Komentar pendapat kalian di bawah! 🎬",
                "hashtags": ["#Shorts", "#viral", "#amazing", "#youtube", "#trending", "#subscribe"],
                "cta": "Subscribe untuk video menarik lainnya!",
                "best_time": "18:00-20:00",
                "hook": "In this video, you'll discover something incredible",
                "keywords": ["tutorial", "how to", "amazing", "incredible"],
                "engagement_tactics": ["ask for comments", "create series", "use end screens"],
                "trending_hooks": ["You won't believe", "The secret to", "What happens when"]
            },
            "facebook": {
                "title": "Video Menakjubkan yang Wajib Ditonton!",
                "description": "Video ini benar-benar luar biasa! Jangan lupa like, comment, dan share ke teman-teman kalian. Apa pendapat kalian tentang ini? 🤔",
                "hashtags": ["#viral", "#amazing", "#video", "#facebook", "#reels", "#share"],
                "cta": "Share ke teman-teman kalian!",
                "best_time": "19:00-21:00",
                "hook": "This will make you think differently",
                "keywords": ["community", "discussion", "share"],
                "engagement_tactics": ["ask questions", "create polls", "encourage sharing"],
                "trending_hooks": ["What do you think about", "Share if you agree", "Tag someone who"]
            }
        }
        
        return base_content.get(platform, base_content["tiktok"])

    def generate_text_post(self, topic: str, platform: str, style: str = "engaging") -> Dict[str, Any]:
        """Generate text post berdasarkan topik dengan Gemini 2.0-flash"""
        if not self.model:
            return self._generate_fallback_text_post(topic, platform)
        
        try:
            self._log(f"Generating text post untuk {platform} dengan topik: {topic}", "AI")
            
            # Enhanced prompt untuk Gemini 2.0-flash
            prompt = f"""
            Create a highly engaging text post for {platform} about: {topic}
            Style: {style}
            
            Generate compelling content in JSON format:
            
            {{
                "title": "attention-grabbing title",
                "content": "engaging post content with storytelling",
                "hashtags": ["#relevant", "#trending", "#hashtags"],
                "cta": "compelling call-to-action",
                "hook": "opening line that stops scrolling",
                "engagement_questions": ["questions to boost comments"],
                "trending_elements": ["current trends to incorporate"],
                "emotional_triggers": ["emotions this post evokes"]
            }}
            
            Platform-specific requirements:
            - TikTok: Casual, trendy, youth-focused, use trending slang
            - Instagram: Aesthetic, lifestyle, inspirational, visual storytelling
            - YouTube: Informative, searchable, community-building, educational value
            - Facebook: Conversational, community-focused, discussion-starter, shareable
            
            Make it authentic, relatable, and highly engaging. Use current trends and viral formats.
            Include storytelling elements and emotional hooks.
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
                    post_content[key] = self._get_default_text_value(key, topic, platform)
            
            self._log("Text post generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return post_content
            
        except Exception as e:
            self._log(f"Error generating text post: {e}", "ERROR")
            return self._generate_fallback_text_post(topic, platform)

    def _get_default_text_value(self, key: str, topic: str, platform: str):
        """Get default value untuk text post"""
        defaults = {
            "title": f"Tips {topic} yang Wajib Diketahui!",
            "content": f"Simak tips {topic} yang sangat berguna ini! Jangan lupa untuk mencoba dan share pengalaman kalian di komentar.",
            "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
            "cta": "Share pengalaman kalian di komentar!",
            "hook": f"Inilah rahasia {topic} yang jarang diketahui",
            "engagement_questions": [f"Apa pengalaman kalian dengan {topic}?"],
            "trending_elements": ["storytelling", "personal experience"],
            "emotional_triggers": ["curiosity", "excitement"]
        }
        return defaults.get(key, "")

    def _generate_fallback_text_post(self, topic: str, platform: str) -> Dict[str, Any]:
        """Generate fallback text post"""
        return {
            "title": f"Tips {topic} yang Wajib Diketahui!",
            "content": f"Simak tips {topic} yang sangat berguna ini! Jangan lupa untuk mencoba dan share pengalaman kalian di komentar.",
            "hashtags": [f"#tips", f"#{topic.replace(' ', '')}", "#viral", "#trending", f"#{platform}"],
            "cta": "Share pengalaman kalian di komentar!",
            "hook": f"Inilah rahasia {topic} yang jarang diketahui",
            "engagement_questions": [f"Apa pengalaman kalian dengan {topic}?"],
            "trending_elements": ["storytelling", "personal experience"],
            "emotional_triggers": ["curiosity", "excitement"]
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
                return True
                
            except Exception as e:
                self._log(f"⚠️ Gemini 2.0-flash not available: {e}", "WARNING")
                self._log("Trying fallback to gemini-pro...", "INFO")
                
                # Fallback test
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Hello, test connection")
                
                self._log("✅ Gemini Pro API working (fallback)", "SUCCESS")
                return True
            
        except Exception as e:
            self._log(f"❌ Gemini API error: {e}", "ERROR")
            return False

    def interactive_ai_menu(self):
        """Interactive AI assistant menu dengan Gemini 2.0-flash"""
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
                    print(f"Objects: {', '.join(analysis.get('objects', []))}")
                    print(f"Setting: {analysis.get('setting', 'unknown')}")
                    print(f"Mood: {analysis.get('mood', 'neutral')}")
                    print(f"Style: {analysis.get('style', 'standard')}")
                    print(f"Viral Score: {analysis.get('viral_score', 'N/A')}/10")
                    print(f"Best Platforms: {', '.join(analysis.get('platforms', []))}")
                    print(f"Content Type: {analysis.get('content_type', 'general')}")
                    print(f"Target Audience: {analysis.get('target_audience', 'general')}")
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
                    print(f"Title: {post.get('title', 'N/A')}")
                    print(f"Content: {post.get('content', 'N/A')}")
                    print(f"Hashtags: {', '.join(post.get('hashtags', []))}")
                    print(f"CTA: {post.get('cta', 'N/A')}")
                    if post.get('hook'):
                        print(f"Hook: {post['hook']}")
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
                            print(f"  Title: {platform_content.get('title', 'N/A')}")
                            print(f"  Description: {platform_content.get('description', 'N/A')[:100]}...")
                            print(f"  Hashtags: {', '.join(platform_content.get('hashtags', []))}")
                            print(f"  CTA: {platform_content.get('cta', 'N/A')}")
                            if platform_content.get('hook'):
                                print(f"  Hook: {platform_content['hook']}")
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
    parser = argparse.ArgumentParser(description="Gemini AI Assistant 2.0-flash")
    parser.add_argument("--video", "-v", help="Path ke video untuk analisis")
    parser.add_argument("--topic", "-t", help="Topik untuk text post")
    parser.add_argument("--platform", "-p", help="Platform target")
    parser.add_argument("--strategy", "-s", choices=['viral', 'quality', 'speed', 'balanced'], 
                       default='balanced', help="Content strategy")
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
        
        analysis = assistant.analyze_video_content(args.video, args.strategy)
        print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS (Gemini 2.0-flash):")
        print(json.dumps(analysis, indent=2))
        
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]
            content = assistant.generate_platform_content(analysis, platforms, args.strategy)
            print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
            print(json.dumps(content, indent=2))
    
    elif args.topic and args.platform:
        post = assistant.generate_text_post(args.topic, args.platform)
        print(f"\n{Fore.GREEN}📝 GENERATED POST (Gemini 2.0-flash):")
        print(json.dumps(post, indent=2))
    
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