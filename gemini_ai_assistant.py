#!/usr/bin/env python3
"""
Gemini AI Assistant untuk Social Media Content Generation
Menggunakan Google Gemini 2.0-flash (Latest & Most Advanced Model)
Enhanced dengan Multi-modal capabilities dan Advanced Content Generation
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
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

# Try to import CV2 and PIL for video analysis
try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class GeminiAIAssistant:
    def __init__(self, debug: bool = False):
        """
        Initialize Gemini AI Assistant with 2.0-flash
        
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
        
        # Initialize Gemini 2.0-flash
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
        """Initialize Gemini 2.0-flash (Latest Model)"""
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
            
            # Use Gemini 2.0-flash (Latest and Most Advanced Model)
            try:
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self._log("🚀 Gemini 2.0-flash berhasil diinisialisasi!", "SUCCESS")
                self._log("🎯 Menggunakan model terbaru dan paling canggih", "AI")
                return True
            except Exception as e:
                if self.debug:
                    self._log(f"Gemini 2.0-flash error: {e}", "DEBUG")
                
                # Fallback to gemini-pro if 2.0-flash not available
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
        """Extract frames dari video untuk analisis dengan Gemini 2.0-flash"""
        if not CV2_AVAILABLE:
            self._log("OpenCV tidak tersedia untuk video analysis", "WARNING")
            return []
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video tidak ditemukan: {video_path}")
        
        self._log(f"🎬 Extracting {num_frames} frames untuk Gemini 2.0-flash...", "AI")
        
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
        """Analyze video content menggunakan Gemini 2.0-flash dengan advanced capabilities"""
        if not self.vision_model:
            self._log("Gemini AI tidak tersedia", "ERROR")
            return self._generate_fallback_analysis(video_path, language)
        
        try:
            # Extract frames jika CV2 tersedia
            frames = []
            if CV2_AVAILABLE:
                frames = self.extract_video_frames(video_path, num_frames=5)  # More frames for 2.0-flash
            
            if not frames:
                # Jika tidak bisa extract frames, gunakan fallback analysis
                self._log("Tidak bisa extract frames, menggunakan fallback analysis", "WARNING")
                return self._generate_fallback_analysis(video_path, language)
            
            self._log(f"🚀 Menganalisis konten video dengan Gemini 2.0-flash...", "AI")
            
            # Analyze multiple frames for better understanding
            images = [Image.open(frame) for frame in frames[:3]]  # Use first 3 frames
            
            # Enhanced prompt untuk Gemini 2.0-flash dengan advanced capabilities
            if language == "english":
                prompt = """
                You are an advanced AI content strategist powered by Gemini 2.0-flash. Analyze these video frames to create viral-ready social media content.

                ADVANCED ANALYSIS REQUIREMENTS:
                1. Deep visual understanding of scenes, objects, people, emotions
                2. Context awareness and storytelling potential
                3. Viral trend prediction and engagement optimization
                4. Platform-specific content adaptation
                5. Audience psychology and behavior analysis

                Provide response in PERFECT JSON format with these enhanced keys:
                {
                  "visual_elements": {
                    "main_subjects": ["list of main subjects/people"],
                    "objects": ["detailed objects in scene"],
                    "setting": "detailed environment description",
                    "lighting": "lighting quality and mood",
                    "composition": "visual composition analysis"
                  },
                  "content_analysis": {
                    "activities": ["what's happening in detail"],
                    "emotions": ["emotions conveyed"],
                    "story_potential": "narrative potential score 1-10",
                    "engagement_hooks": ["specific engagement elements"]
                  },
                  "viral_potential": {
                    "viral_score": "score 1-10 with reasoning",
                    "trending_elements": ["elements that could trend"],
                    "shareability_factors": ["why people would share"],
                    "meme_potential": "meme creation potential 1-10"
                  },
                  "platform_optimization": {
                    "tiktok_potential": "optimization score 1-10",
                    "instagram_potential": "optimization score 1-10", 
                    "youtube_potential": "optimization score 1-10",
                    "facebook_potential": "optimization score 1-10"
                  },
                  "content_strategy": {
                    "target_audience": "detailed audience description",
                    "content_pillars": ["main content themes"],
                    "call_to_action_suggestions": ["specific CTAs"],
                    "hashtag_strategy": ["strategic hashtag categories"]
                  },
                  "technical_quality": {
                    "video_quality": "quality assessment",
                    "audio_potential": "estimated audio quality",
                    "editing_suggestions": ["improvement suggestions"]
                  }
                }
                """
            else:
                prompt = """
                Anda adalah AI content strategist canggih yang didukung Gemini 2.0-flash. Analisis frame video ini untuk membuat konten media sosial yang viral.

                REQUIREMENTS ANALISIS LANJUTAN:
                1. Pemahaman visual mendalam tentang scene, objek, orang, emosi
                2. Kesadaran konteks dan potensi storytelling
                3. Prediksi trend viral dan optimasi engagement
                4. Adaptasi konten spesifik platform
                5. Analisis psikologi dan perilaku audience

                Berikan respons dalam format JSON SEMPURNA dengan keys yang ditingkatkan:
                {
                  "elemen_visual": {
                    "subjek_utama": ["daftar subjek/orang utama"],
                    "objek": ["objek detail dalam scene"],
                    "setting": "deskripsi environment detail",
                    "pencahayaan": "kualitas lighting dan mood",
                    "komposisi": "analisis komposisi visual"
                  },
                  "analisis_konten": {
                    "aktivitas": ["apa yang terjadi secara detail"],
                    "emosi": ["emosi yang disampaikan"],
                    "potensi_cerita": "skor potensi narasi 1-10",
                    "engagement_hooks": ["elemen engagement spesifik"]
                  },
                  "potensi_viral": {
                    "skor_viral": "skor 1-10 dengan alasan",
                    "elemen_trending": ["elemen yang bisa trending"],
                    "faktor_shareability": ["mengapa orang akan share"],
                    "potensi_meme": "potensi pembuatan meme 1-10"
                  },
                  "optimasi_platform": {
                    "potensi_tiktok": "skor optimasi 1-10",
                    "potensi_instagram": "skor optimasi 1-10",
                    "potensi_youtube": "skor optimasi 1-10", 
                    "potensi_facebook": "skor optimasi 1-10"
                  },
                  "strategi_konten": {
                    "target_audience": "deskripsi audience detail",
                    "pilar_konten": ["tema konten utama"],
                    "saran_call_to_action": ["CTA spesifik"],
                    "strategi_hashtag": ["kategori hashtag strategis"]
                  },
                  "kualitas_teknis": {
                    "kualitas_video": "penilaian kualitas",
                    "potensi_audio": "estimasi kualitas audio",
                    "saran_editing": ["saran perbaikan"]
                  }
                }
                """
            
            # Use Gemini 2.0-flash advanced multi-modal capabilities
            response = self.vision_model.generate_content([prompt] + images)
            
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
                
                self._log(f"🎯 Advanced video analysis dengan Gemini 2.0-flash selesai", "SUCCESS")
                return analysis
                
            except json.JSONDecodeError:
                self._log("Error parsing AI response, using enhanced fallback", "WARNING")
                return self._generate_enhanced_fallback_analysis(video_path, language)
                
        except Exception as e:
            self._log(f"Error analyzing video: {e}", "ERROR")
            return self._generate_enhanced_fallback_analysis(video_path, language)

    def _generate_enhanced_fallback_analysis(self, video_path: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate enhanced fallback analysis untuk Gemini 2.0-flash"""
        if language == "english":
            return {
                "visual_elements": {
                    "main_subjects": ["video content"],
                    "objects": ["various objects"],
                    "setting": "unknown environment",
                    "lighting": "standard lighting",
                    "composition": "standard composition"
                },
                "content_analysis": {
                    "activities": ["unknown activity"],
                    "emotions": ["neutral"],
                    "story_potential": 7,
                    "engagement_hooks": ["visual content", "interesting moments"]
                },
                "viral_potential": {
                    "viral_score": "7 - good potential with optimization",
                    "trending_elements": ["engaging visuals", "shareable content"],
                    "shareability_factors": ["interesting content", "good quality"],
                    "meme_potential": 6
                },
                "platform_optimization": {
                    "tiktok_potential": 8,
                    "instagram_potential": 7,
                    "youtube_potential": 7,
                    "facebook_potential": 6
                },
                "content_strategy": {
                    "target_audience": "general social media users",
                    "content_pillars": ["entertainment", "engagement"],
                    "call_to_action_suggestions": ["like and share", "comment below"],
                    "hashtag_strategy": ["trending", "viral", "content"]
                },
                "technical_quality": {
                    "video_quality": "good",
                    "audio_potential": "standard",
                    "editing_suggestions": ["add trending music", "optimize for mobile"]
                }
            }
        else:
            return {
                "elemen_visual": {
                    "subjek_utama": ["konten video"],
                    "objek": ["berbagai objek"],
                    "setting": "lingkungan tidak diketahui",
                    "pencahayaan": "pencahayaan standar",
                    "komposisi": "komposisi standar"
                },
                "analisis_konten": {
                    "aktivitas": ["aktivitas tidak diketahui"],
                    "emosi": ["netral"],
                    "potensi_cerita": 7,
                    "engagement_hooks": ["konten visual", "momen menarik"]
                },
                "potensi_viral": {
                    "skor_viral": "7 - potensi bagus dengan optimasi",
                    "elemen_trending": ["visual menarik", "konten shareable"],
                    "faktor_shareability": ["konten menarik", "kualitas bagus"],
                    "potensi_meme": 6
                },
                "optimasi_platform": {
                    "potensi_tiktok": 8,
                    "potensi_instagram": 7,
                    "potensi_youtube": 7,
                    "potensi_facebook": 6
                },
                "strategi_konten": {
                    "target_audience": "pengguna media sosial umum",
                    "pilar_konten": ["hiburan", "engagement"],
                    "saran_call_to_action": ["like dan share", "komentar di bawah"],
                    "strategi_hashtag": ["trending", "viral", "konten"]
                },
                "kualitas_teknis": {
                    "kualitas_video": "bagus",
                    "potensi_audio": "standar",
                    "saran_editing": ["tambah musik trending", "optimasi untuk mobile"]
                }
            }

    def generate_platform_content(self, analysis: Dict[str, Any], platforms: List[str], 
                                language: str = "indonesian") -> Dict[str, Any]:
        """Generate content untuk setiap platform menggunakan Gemini 2.0-flash advanced capabilities"""
        if not self.model:
            return self._generate_fallback_content(platforms, language)
        
        try:
            content = {}
            
            for platform in platforms:
                self._log(f"🚀 Generating advanced content untuk {platform} dengan Gemini 2.0-flash...", "AI")
                
                # Enhanced prompt untuk Gemini 2.0-flash dengan advanced content generation
                if language == "english":
                    prompt = f"""
                    You are a viral content creation expert powered by Gemini 2.0-flash. Create highly engaging, platform-optimized content for {platform} based on this advanced video analysis:
                    
                    {json.dumps(analysis, indent=2)}

                    ADVANCED CONTENT GENERATION FOR {platform.upper()}:

                    Platform-specific optimization:
                    - TikTok: Viral hooks, trending sounds, youth slang, 15-60s optimization
                    - Instagram: Aesthetic appeal, story-worthy, lifestyle integration
                    - YouTube: SEO optimization, retention hooks, algorithm-friendly
                    - Facebook: Community engagement, discussion starters, shareability

                    GENERATE PERFECT JSON with these enhanced keys:
                    {{
                      "title_variations": [
                        {{
                          "type": "viral_hook",
                          "title": "attention-grabbing viral title",
                          "hook_type": "curiosity/shock/emotion"
                        }},
                        {{
                          "type": "question_format", 
                          "title": "engaging question title",
                          "engagement_trigger": "specific trigger"
                        }},
                        {{
                          "type": "trending_format",
                          "title": "trending format title", 
                          "trend_element": "current trend used"
                        }}
                      ],
                      "description_options": [
                        {{
                          "type": "storytelling",
                          "content": "narrative-driven description",
                          "story_arc": "beginning-middle-end structure"
                        }},
                        {{
                          "type": "educational",
                          "content": "value-providing description",
                          "learning_outcome": "what viewers learn"
                        }},
                        {{
                          "type": "entertainment",
                          "content": "fun and engaging description",
                          "entertainment_value": "why it's entertaining"
                        }}
                      ],
                      "hashtag_strategy": {{
                        "trending_hashtags": ["current trending tags"],
                        "niche_hashtags": ["specific niche tags"],
                        "branded_hashtags": ["potential brand tags"],
                        "location_hashtags": ["location-based tags"],
                        "optimal_count": "recommended number for platform"
                      }},
                      "engagement_optimization": {{
                        "hook_timing": "when to place hook (seconds)",
                        "cta_placement": "optimal CTA placement",
                        "interaction_triggers": ["specific engagement triggers"],
                        "retention_tactics": ["keep viewers watching"]
                      }},
                      "viral_elements": {{
                        "trending_sounds": ["suggested trending audio"],
                        "visual_effects": ["recommended effects"],
                        "editing_style": "optimal editing approach",
                        "posting_strategy": "best time and frequency"
                      }}
                    }}
                    """
                else:
                    prompt = f"""
                    Anda adalah expert pembuatan konten viral yang didukung Gemini 2.0-flash. Buat konten yang sangat engaging dan dioptimasi untuk {platform} berdasarkan analisis video lanjutan ini:
                    
                    {json.dumps(analysis, indent=2)}

                    GENERASI KONTEN LANJUTAN UNTUK {platform.upper()}:

                    Optimasi spesifik platform:
                    - TikTok: Hook viral, trending sounds, bahasa anak muda, optimasi 15-60s
                    - Instagram: Daya tarik estetik, story-worthy, integrasi lifestyle
                    - YouTube: Optimasi SEO, retention hooks, algorithm-friendly
                    - Facebook: Community engagement, discussion starters, shareability

                    GENERATE JSON SEMPURNA dengan keys yang ditingkatkan:
                    {{
                      "variasi_judul": [
                        {{
                          "tipe": "viral_hook",
                          "judul": "judul viral yang menarik perhatian",
                          "tipe_hook": "curiosity/shock/emotion"
                        }},
                        {{
                          "tipe": "format_pertanyaan",
                          "judul": "judul pertanyaan yang engaging", 
                          "trigger_engagement": "trigger spesifik"
                        }},
                        {{
                          "tipe": "format_trending",
                          "judul": "judul format trending",
                          "elemen_trend": "trend terkini yang digunakan"
                        }}
                      ],
                      "opsi_deskripsi": [
                        {{
                          "tipe": "storytelling",
                          "konten": "deskripsi berbasis narasi",
                          "alur_cerita": "struktur awal-tengah-akhir"
                        }},
                        {{
                          "tipe": "edukatif",
                          "konten": "deskripsi yang memberikan value",
                          "hasil_pembelajaran": "apa yang dipelajari viewer"
                        }},
                        {{
                          "tipe": "hiburan",
                          "konten": "deskripsi fun dan engaging",
                          "nilai_hiburan": "mengapa menghibur"
                        }}
                      ],
                      "strategi_hashtag": {{
                        "hashtag_trending": ["tag trending saat ini"],
                        "hashtag_niche": ["tag niche spesifik"],
                        "hashtag_branded": ["potential brand tags"],
                        "hashtag_lokasi": ["tag berbasis lokasi"],
                        "jumlah_optimal": "jumlah yang direkomendasikan untuk platform"
                      }},
                      "optimasi_engagement": {{
                        "timing_hook": "kapan menempatkan hook (detik)",
                        "penempatan_cta": "penempatan CTA optimal",
                        "trigger_interaksi": ["trigger engagement spesifik"],
                        "taktik_retention": ["menjaga viewer tetap menonton"]
                      }},
                      "elemen_viral": {{
                        "trending_sounds": ["audio trending yang disarankan"],
                        "efek_visual": ["efek yang direkomendasikan"],
                        "gaya_editing": "pendekatan editing optimal",
                        "strategi_posting": "waktu dan frekuensi terbaik"
                      }}
                    }}
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
            
            self._log(f"🎯 Advanced content generation dengan Gemini 2.0-flash selesai", "SUCCESS")
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
                    "title_variations": [
                        {"type": "viral_hook", "title": "This Video Will Blow Your Mind! 🔥", "hook_type": "curiosity"},
                        {"type": "question_format", "title": "Why Is Everyone Talking About This?", "engagement_trigger": "curiosity"},
                        {"type": "trending_format", "title": "POV: You Discover This Amazing Thing", "trend_element": "POV format"}
                    ],
                    "description_options": [
                        {"type": "storytelling", "content": "Amazing content that will change your perspective! Tag someone who needs to see this.", "story_arc": "discovery-revelation-impact"},
                        {"type": "educational", "content": "Learn something new today with this incredible content!", "learning_outcome": "new knowledge"},
                        {"type": "entertainment", "content": "Pure entertainment that will make your day better!", "entertainment_value": "mood boost"}
                    ],
                    "hashtag_strategy": {
                        "trending_hashtags": ["#fyp", "#viral", "#trending"],
                        "niche_hashtags": ["#amazing", "#wow", "#mindblowing"],
                        "branded_hashtags": ["#tiktok", "#video"],
                        "location_hashtags": ["#worldwide"],
                        "optimal_count": "5-8 hashtags"
                    }
                }
            }
        else:
            base_content = {
                "tiktok": {
                    "variasi_judul": [
                        {"tipe": "viral_hook", "judul": "Video Viral yang Bikin Jutaan Views! 🔥", "tipe_hook": "curiosity"},
                        {"tipe": "format_pertanyaan", "judul": "Kenapa Video Ini Bisa Trending #1?", "trigger_engagement": "curiosity"},
                        {"tipe": "format_trending", "judul": "POV: Kamu Nemuin Hal Amazing Ini", "elemen_trend": "POV format"}
                    ],
                    "opsi_deskripsi": [
                        {"tipe": "storytelling", "konten": "Konten amazing yang akan mengubah perspektif kamu! Tag bestie yang perlu lihat ini.", "alur_cerita": "penemuan-revelasi-dampak"},
                        {"tipe": "edukatif", "konten": "Belajar hal baru hari ini dengan konten incredible ini!", "hasil_pembelajaran": "pengetahuan baru"},
                        {"tipe": "hiburan", "konten": "Hiburan murni yang akan membuat hari kamu lebih baik!", "nilai_hiburan": "mood boost"}
                    ],
                    "strategi_hashtag": {
                        "hashtag_trending": ["#fyp", "#viral", "#trending"],
                        "hashtag_niche": ["#amazing", "#wow", "#keren"],
                        "hashtag_branded": ["#tiktok", "#video"],
                        "hashtag_lokasi": ["#indonesia"],
                        "jumlah_optimal": "5-8 hashtag"
                    }
                }
            }
        
        return base_content.get(platform, base_content["tiktok"])

    def generate_text_post(self, topic: str, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate text post berdasarkan topik menggunakan Gemini 2.0-flash"""
        if not self.model:
            return self._generate_fallback_text_post(topic, platform, language)
        
        try:
            self._log(f"🚀 Generating advanced text post untuk {platform} dengan Gemini 2.0-flash...", "AI")
            
            if language == "english":
                prompt = f"""
                You are a viral content strategist powered by Gemini 2.0-flash. Create an engaging text post for {platform} about: {topic}

                ADVANCED TEXT POST GENERATION:

                Platform guidelines:
                - TikTok: Casual, trendy, youth-focused, hook-driven
                - Instagram: Aesthetic, lifestyle, visual storytelling
                - YouTube: Informative, searchable, community-building
                - Facebook: Conversational, community-focused, discussion-starter

                Generate PERFECT JSON with enhanced structure:
                {{
                  "content_variations": [
                    {{
                      "style": "viral_hook",
                      "content": "attention-grabbing content with hook",
                      "engagement_factor": "why it's engaging"
                    }},
                    {{
                      "style": "storytelling", 
                      "content": "narrative-driven content",
                      "story_element": "story component used"
                    }},
                    {{
                      "style": "educational",
                      "content": "value-providing content",
                      "value_proposition": "what value it provides"
                    }}
                  ],
                  "hashtag_strategy": {{
                    "primary_hashtags": ["main topic hashtags"],
                    "trending_hashtags": ["current trending hashtags"],
                    "engagement_hashtags": ["hashtags that drive engagement"]
                  }},
                  "call_to_action": {{
                    "primary_cta": "main call to action",
                    "secondary_cta": "backup call to action",
                    "engagement_type": "type of engagement expected"
                  }},
                  "optimization_tips": {{
                    "best_posting_time": "optimal posting time",
                    "engagement_tactics": ["specific tactics to boost engagement"],
                    "viral_potential": "viral potential score 1-10"
                  }}
                }}
                """
            else:
                prompt = f"""
                Anda adalah viral content strategist yang didukung Gemini 2.0-flash. Buat text post yang engaging untuk {platform} tentang: {topic}

                GENERASI TEXT POST LANJUTAN:

                Panduan platform:
                - TikTok: Casual, trendy, youth-focused, hook-driven
                - Instagram: Aesthetic, lifestyle, visual storytelling
                - YouTube: Informatif, searchable, community-building
                - Facebook: Conversational, community-focused, discussion-starter

                Generate JSON SEMPURNA dengan struktur yang ditingkatkan:
                {{
                  "variasi_konten": [
                    {{
                      "gaya": "viral_hook",
                      "konten": "konten menarik perhatian dengan hook",
                      "faktor_engagement": "mengapa engaging"
                    }},
                    {{
                      "gaya": "storytelling",
                      "konten": "konten berbasis narasi", 
                      "elemen_cerita": "komponen cerita yang digunakan"
                    }},
                    {{
                      "gaya": "edukatif",
                      "konten": "konten yang memberikan value",
                      "proposisi_nilai": "value apa yang diberikan"
                    }}
                  ],
                  "strategi_hashtag": {{
                    "hashtag_utama": ["hashtag topik utama"],
                    "hashtag_trending": ["hashtag trending saat ini"],
                    "hashtag_engagement": ["hashtag yang mendorong engagement"]
                  }},
                  "call_to_action": {{
                    "cta_utama": "call to action utama",
                    "cta_sekunder": "call to action cadangan",
                    "tipe_engagement": "jenis engagement yang diharapkan"
                  }},
                  "tips_optimasi": {{
                    "waktu_posting_terbaik": "waktu posting optimal",
                    "taktik_engagement": ["taktik spesifik untuk boost engagement"],
                    "potensi_viral": "skor potensi viral 1-10"
                  }}
                }}
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
            
            self._log(f"🎯 Advanced text post generation dengan Gemini 2.0-flash selesai", "SUCCESS")
            return post_content
            
        except Exception as e:
            self._log(f"Error generating text post: {e}", "ERROR")
            return self._generate_fallback_text_post(topic, platform, language)

    def _generate_fallback_text_post(self, topic: str, platform: str, language: str = "indonesian") -> Dict[str, Any]:
        """Generate fallback text post dengan language support"""
        if language == "english":
            return {
                "content_variations": [
                    {
                        "style": "viral_hook",
                        "content": f"🔥 Amazing tips about {topic} you need to know! This will definitely change your perspective. Share your experience in the comments!",
                        "engagement_factor": "curiosity and value"
                    }
                ],
                "hashtag_strategy": {
                    "primary_hashtags": [f"#{topic.replace(' ', '')}", "#tips", "#amazing"],
                    "trending_hashtags": ["#viral", "#trending"],
                    "engagement_hashtags": ["#share", "#comment"]
                },
                "call_to_action": {
                    "primary_cta": "Share your experience in the comments!",
                    "secondary_cta": "Tag someone who needs to see this!",
                    "engagement_type": "comments and shares"
                }
            }
        else:
            return {
                "variasi_konten": [
                    {
                        "gaya": "viral_hook", 
                        "konten": f"🔥 Tips {topic} yang wajib diketahui! Pasti akan mengubah perspektif kamu. Share pengalaman kamu di komentar!",
                        "faktor_engagement": "curiosity dan value"
                    }
                ],
                "strategi_hashtag": {
                    "hashtag_utama": [f"#{topic.replace(' ', '')}", "#tips", "#amazing"],
                    "hashtag_trending": ["#viral", "#trending"],
                    "hashtag_engagement": ["#share", "#komentar"]
                },
                "call_to_action": {
                    "cta_utama": "Share pengalaman kamu di komentar!",
                    "cta_sekunder": "Tag yang perlu lihat ini!",
                    "tipe_engagement": "komentar dan share"
                }
            }

    def check_api_status(self) -> Dict[str, Any]:
        """Check Gemini 2.0-flash API status"""
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
            
            # Test with Gemini 2.0-flash
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content("Test connection")
            
            return {
                "success": True,
                "model": "gemini-2.0-flash-exp",
                "message": "🚀 Gemini 2.0-flash API ready - Latest & Most Advanced Model!",
                "capabilities": [
                    "Advanced multi-modal understanding",
                    "Enhanced content generation", 
                    "Superior viral prediction",
                    "Platform-specific optimization",
                    "Advanced engagement analysis"
                ]
            }
            
        except Exception as e:
            try:
                # Fallback test
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Test")
                
                return {
                    "success": True,
                    "model": "gemini-pro",
                    "message": "Gemini Pro API ready (fallback from 2.0-flash)",
                    "note": "Upgrade to 2.0-flash for advanced features"
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
        """Interactive AI assistant menu dengan Gemini 2.0-flash features"""
        if not GENAI_AVAILABLE:
            print(f"{Fore.RED}❌ google-generativeai tidak tersedia!")
            print(f"{Fore.YELLOW}Install dengan: pip install google-generativeai")
            return
        
        if not self.model:
            print(f"{Fore.RED}❌ Gemini AI tidak tersedia!")
            print(f"{Fore.YELLOW}Buat file .env dengan GEMINI_API_KEY=your_api_key")
            return
        
        print(f"\n{Fore.LIGHTMAGENTA_EX}🚀 Gemini 2.0-flash AI Assistant")
        print("=" * 60)
        print(f"{Fore.LIGHTCYAN_EX}🎯 Powered by Latest & Most Advanced AI Model")
        print()
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 🎬 Advanced Video Analysis")
            print("2. ✍️ Enhanced Text Post Generation")
            print("3. 📱 Multi-Platform Content Strategy")
            print("4. 🔍 Check API Status & Capabilities")
            print("5. 🧹 Cleanup Temp Files")
            print("6. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-6): ").strip()
            
            if choice == "1":
                video_path = input(f"{Fore.CYAN}Path ke video: ").strip()
                if os.path.exists(video_path):
                    language = "english" if input(f"{Fore.CYAN}Language (en/id): ").strip().lower() == "en" else "indonesian"
                    analysis = self.analyze_video_content(video_path, language)
                    
                    print(f"\n{Fore.GREEN}🎯 ADVANCED VIDEO ANALYSIS (Gemini 2.0-flash):")
                    print(json.dumps(analysis, indent=2, ensure_ascii=False))
                else:
                    print(f"{Fore.RED}❌ File video tidak ditemukan!")
            
            elif choice == "2":
                topic = input(f"{Fore.CYAN}Topik: ").strip()
                platform = input(f"{Fore.CYAN}Platform (tiktok/instagram/youtube/facebook): ").strip()
                if topic and platform:
                    language = "english" if input(f"{Fore.CYAN}Language (en/id): ").strip().lower() == "en" else "indonesian"
                    post = self.generate_text_post(topic, platform, language)
                    
                    print(f"\n{Fore.GREEN}🎯 ENHANCED TEXT POST (Gemini 2.0-flash):")
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
                        
                        print(f"\n{Fore.GREEN}🎯 MULTI-PLATFORM STRATEGY (Gemini 2.0-flash):")
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
                    if "capabilities" in status:
                        print(f"\n🚀 Advanced Capabilities:")
                        for capability in status["capabilities"]:
                            print(f"  • {capability}")
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
    parser = argparse.ArgumentParser(description="Gemini 2.0-flash AI Assistant")
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
            if "capabilities" in status:
                print(f"\n🚀 Advanced Capabilities:")
                for capability in status["capabilities"]:
                    print(f"  • {capability}")
        else:
            print(f"{Fore.RED}❌ {status['message']}")
        return
    
    if args.video:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ Video file not found: {args.video}")
            sys.exit(1)
        
        analysis = assistant.analyze_video_content(args.video, args.language)
        print(f"\n{Fore.GREEN}🎯 ADVANCED VIDEO ANALYSIS (Gemini 2.0-flash):")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        if args.platform:
            platforms = [p.strip() for p in args.platform.split(',')]
            content = assistant.generate_platform_content(analysis, platforms, args.language)
            print(f"\n{Fore.GREEN}🎯 GENERATED CONTENT:")
            print(json.dumps(content, indent=2, ensure_ascii=False))
    
    elif args.topic and args.platform:
        post = assistant.generate_text_post(args.topic, args.platform, args.language)
        print(f"\n{Fore.GREEN}🎯 ENHANCED TEXT POST (Gemini 2.0-flash):")
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