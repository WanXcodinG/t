#!/usr/bin/env python3
"""
Gemini AI Assistant untuk Social Media Content Generation
Menggunakan Google Gemini AI untuk analisis video dan generate konten
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
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.temp_dir = self.base_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.ai_cache_dir = self.base_dir / "ai_cache"
        self.ai_cache_dir.mkdir(exist_ok=True)
        
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

    def _initialize_gemini(self):
        """Initialize Gemini AI"""
        if not GENAI_AVAILABLE:
            self._log("google-generativeai tidak tersedia", "ERROR")
            self._log("Install dengan: pip install google-generativeai", "INFO")
            return False
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self._log("GEMINI_API_KEY tidak ditemukan di environment variables", "WARNING")
            self._log("Set dengan: set GEMINI_API_KEY=your_api_key", "INFO")
            return False
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
            self._log("Gemini AI berhasil diinisialisasi", "SUCCESS")
            return True
        except Exception as e:
            self._log(f"Gagal inisialisasi Gemini AI: {e}", "ERROR")
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
        """Analyze video content menggunakan Gemini AI"""
        if not self.model:
            self._log("Gemini AI tidak tersedia", "ERROR")
            return self._generate_fallback_analysis(video_path)
        
        try:
            # Extract frames
            frames = self.extract_video_frames(video_path, num_frames=3)
            if not frames:
                return self._generate_fallback_analysis(video_path)
            
            self._log("Menganalisis konten video dengan Gemini AI...", "AI")
            
            # Analyze first frame
            image = Image.open(frames[0])
            
            prompt = f"""
            Analyze this video frame and provide insights for social media content creation.
            Strategy: {strategy}
            
            Please provide:
            1. Main objects/subjects in the video
            2. Setting/environment (indoor/outdoor, location type)
            3. Mood/emotion conveyed
            4. Visual style and quality
            5. Viral potential (1-10 scale)
            6. Best platforms for this content
            7. Suggested content angles
            
            Format as JSON with these keys: objects, setting, mood, style, viral_score, platforms, angles
            """
            
            response = self.model.generate_content([prompt, image])
            
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
                
                self._log("Video analysis selesai", "SUCCESS")
                return analysis
                
            except json.JSONDecodeError:
                self._log("Error parsing AI response, using fallback", "WARNING")
                return self._generate_fallback_analysis(video_path)
                
        except Exception as e:
            self._log(f"Error analyzing video: {e}", "ERROR")
            return self._generate_fallback_analysis(video_path)

    def _generate_fallback_analysis(self, video_path: str) -> Dict[str, Any]:
        """Generate fallback analysis jika AI tidak tersedia"""
        return {
            "objects": ["video content"],
            "setting": "unknown",
            "mood": "neutral",
            "style": "standard",
            "viral_score": 7,
            "platforms": ["tiktok", "instagram", "youtube"],
            "angles": ["entertaining", "engaging", "shareable"]
        }

    def generate_platform_content(self, analysis: Dict[str, Any], platforms: List[str], 
                                strategy: str = "balanced") -> Dict[str, Any]:
        """Generate content untuk setiap platform berdasarkan analysis"""
        if not self.model:
            return self._generate_fallback_content(platforms)
        
        try:
            content = {}
            
            for platform in platforms:
                self._log(f"Generating content untuk {platform}...", "AI")
                
                prompt = f"""
                Create engaging social media content for {platform} based on this video analysis:
                {json.dumps(analysis, indent=2)}
                
                Strategy: {strategy}
                
                Generate:
                1. Catchy title (platform-appropriate length)
                2. Engaging description with relevant hashtags
                3. Call-to-action
                4. Best posting time suggestion
                
                Platform-specific requirements:
                - TikTok: Viral, trendy, youth-focused, max 150 chars title
                - Instagram: Aesthetic, visual, lifestyle, max 125 chars title  
                - YouTube: SEO-optimized, searchable, max 100 chars title
                - Facebook: Community-focused, shareable, max 255 chars title
                
                Format as JSON with keys: title, description, cta, best_time
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
                    content[platform] = self._generate_fallback_platform_content(platform)
            
            self._log("Content generation selesai", "SUCCESS")
            return content
            
        except Exception as e:
            self._log(f"Error generating platform content: {e}", "ERROR")
            return self._generate_fallback_content(platforms)

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
                "description": "#fyp #viral #trending #amazing #wow #foryou #tiktok #video #content #entertainment",
                "cta": "Follow untuk konten menarik lainnya!",
                "best_time": "19:00-21:00"
            },
            "instagram": {
                "title": "Content yang Luar Biasa! ✨",
                "description": "Video yang wajib kalian tonton! Tag teman kalian di komentar. #viral #instagram #reels #amazing #content #trending",
                "cta": "Save dan share ke story kalian!",
                "best_time": "20:00-22:00"
            },
            "youtube": {
                "title": "Video Viral yang Akan Mengejutkan Anda!",
                "description": "Tonton video menakjubkan ini sampai habis! Jangan lupa subscribe, like, dan share. #Shorts #viral #amazing #youtube #trending",
                "cta": "Subscribe untuk video menarik lainnya!",
                "best_time": "18:00-20:00"
            },
            "facebook": {
                "title": "Video Menakjubkan yang Wajib Ditonton!",
                "description": "Video ini benar-benar luar biasa! Jangan lupa like dan share ke teman-teman kalian. #viral #amazing #video #facebook #reels",
                "cta": "Share ke teman-teman kalian!",
                "best_time": "19:00-21:00"
            }
        }
        
        return base_content.get(platform, base_content["tiktok"])

    def generate_text_post(self, topic: str, platform: str, style: str = "engaging") -> Dict[str, Any]:
        """Generate text post berdasarkan topik"""
        if not self.model:
            return self._generate_fallback_text_post(topic, platform)
        
        try:
            self._log(f"Generating text post untuk {platform} dengan topik: {topic}", "AI")
            
            prompt = f"""
            Create an engaging text post for {platform} about: {topic}
            Style: {style}
            
            Requirements:
            - Platform-appropriate tone and format
            - Include relevant hashtags
            - Add call-to-action
            - Make it engaging and shareable
            
            Platform guidelines:
            - TikTok: Casual, trendy, youth-focused
            - Instagram: Aesthetic, lifestyle, visual
            - YouTube: Informative, searchable, community
            - Facebook: Conversational, community-focused
            
            Format as JSON with keys: title, content, hashtags, cta
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
            
            self._log("Text post generation selesai", "SUCCESS")
            return post_content
            
        except Exception as e:
            self._log(f"Error generating text post: {e}", "ERROR")
            return self._generate_fallback_text_post(topic, platform)

    def _generate_fallback_text_post(self, topic: str, platform: str) -> Dict[str, Any]:
        """Generate fallback text post"""
        return {
            "title": f"Tips {topic} yang Wajib Diketahui!",
            "content": f"Simak tips {topic} yang sangat berguna ini! Jangan lupa untuk mencoba dan share pengalaman kalian di komentar.",
            "hashtags": f"#tips #{topic.replace(' ', '')} #viral #trending #{platform}",
            "cta": "Share pengalaman kalian di komentar!"
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
            print(f"{Fore.YELLOW}Set GEMINI_API_KEY environment variable")
            return
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}🤖 Gemini AI Assistant")
        print("=" * 50)
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 🎬 Analyze Video")
            print("2. ✍️ Generate Text Post")
            print("3. 📱 Generate Platform Content")
            print("4. 🧹 Cleanup Temp Files")
            print("5. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-5): ").strip()
            
            if choice == "1":
                video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
                if os.path.exists(video_path):
                    strategy = input(f"{Fore.CYAN}Strategy (viral/quality/speed/balanced): ").strip() or "balanced"
                    analysis = self.analyze_video_content(video_path, strategy)
                    
                    print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS:")
                    print(f"Objects: {', '.join(analysis.get('objects', []))}")
                    print(f"Setting: {analysis.get('setting', 'unknown')}")
                    print(f"Mood: {analysis.get('mood', 'neutral')}")
                    print(f"Viral Score: {analysis.get('viral_score', 'N/A')}/10")
                    print(f"Best Platforms: {', '.join(analysis.get('platforms', []))}")
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "2":
                topic = input(f"{Fore.CYAN}Topik: ").strip()
                platform = input(f"{Fore.CYAN}Platform (tiktok/instagram/youtube/facebook): ").strip()
                if topic and platform:
                    post = self.generate_text_post(topic, platform)
                    
                    print(f"\n{Fore.GREEN}📝 GENERATED POST:")
                    print(f"Title: {post.get('title', 'N/A')}")
                    print(f"Content: {post.get('content', 'N/A')}")
                    print(f"Hashtags: {post.get('hashtags', 'N/A')}")
                    print(f"CTA: {post.get('cta', 'N/A')}")
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
                        
                        print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
                        for platform, platform_content in content.items():
                            print(f"\n{platform.upper()}:")
                            print(f"  Title: {platform_content.get('title', 'N/A')}")
                            print(f"  Description: {platform_content.get('description', 'N/A')[:100]}...")
                    else:
                        print(f"{Fore.RED}❌ Minimal satu platform harus dipilih!")
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "4":
                self.cleanup_temp_files()
            
            elif choice == "5":
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
    parser.add_argument("--strategy", "-s", choices=['viral', 'quality', 'speed', 'balanced'], 
                       default='balanced', help="Content strategy")
    parser.add_argument("--api-key", help="Gemini API key")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ['GEMINI_API_KEY'] = args.api_key
    
    assistant = GeminiAIAssistant(debug=args.debug)
    
    if args.video:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ Video file not found: {args.video}")
            sys.exit(1)
        
        analysis = assistant.analyze_video_content(args.video, args.strategy)
        print(f"\n{Fore.GREEN}📊 VIDEO ANALYSIS:")
        print(json.dumps(analysis, indent=2))
        
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]
            content = assistant.generate_platform_content(analysis, platforms, args.strategy)
            print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
            print(json.dumps(content, indent=2))
    
    elif args.topic and args.platform:
        post = assistant.generate_text_post(args.topic, args.platform)
        print(f"\n{Fore.GREEN}📝 GENERATED POST:")
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