#!/usr/bin/env python3
"""
Facebook Uploader Unified untuk Status dan Media menggunakan Selenium
Mendukung text status, media (image/video), dan AI content generation
Fixed untuk error [WinError 193] dengan Universal Driver Manager
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from colorama import init, Fore, Style
import argparse

# Initialize colorama
init(autoreset=True)

# Import Universal Driver Manager
try:
    from driver_manager import get_chrome_driver
    DRIVER_MANAGER_AVAILABLE = True
except ImportError:
    DRIVER_MANAGER_AVAILABLE = False

# Import AI Assistant
try:
    from gemini_ai_assistant import GeminiAIAssistant
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class FacebookUploader:
    def __init__(self, headless: bool = False, debug: bool = False):
        """
        Initialize Facebook Uploader
        
        Args:
            headless: Run browser in headless mode
            debug: Enable debug logging
        """
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.wait = None
        
        # Setup paths
        self.base_dir = Path(__file__).parent
        self.cookies_dir = self.base_dir / "cookies"
        self.cookies_dir.mkdir(exist_ok=True)
        self.cookies_path = self.cookies_dir / "facebook_cookies.json"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Initialize AI Assistant
        self.ai_assistant = GeminiAIAssistant(debug=debug) if AI_AVAILABLE else None
        
        # Facebook URLs
        self.home_url = "https://www.facebook.com"
        self.login_url = "https://www.facebook.com/login"
        
        # Enhanced selectors untuk Facebook
        self.selectors = {
            'status_input': [
                "div[data-testid='status-attachment-mentions-input']",
                "div[role='textbox'][data-testid='status-attachment-mentions-input']",
                "div[contenteditable='true'][data-testid='status-attachment-mentions-input']",
                "div[aria-label*='What\\'s on your mind']",
                "div[aria-label*='Apa yang Anda pikirkan']",
                "div[contenteditable='true'][aria-label*='mind']",
                "div[contenteditable='true'][role='textbox']"
            ],
            'photo_video_button': [
                "div[aria-label='Photo/video']",
                "div[aria-label='Foto/video']",
                "div[data-testid='photo-video-button']",
                "input[accept*='image']",
                "input[accept*='video']",
                "div[role='button'][aria-label*='Photo']",
                "div[role='button'][aria-label*='Foto']"
            ],
            'file_input': [
                "input[type='file']",
                "input[accept*='video']",
                "input[accept*='image']",
                "input[accept*='image/jpeg,image/png,image/webp,image/gif,video/mp4,video/quicktime,video/x-msvideo']"
            ],
            'post_button': [
                "div[aria-label='Post']",
                "div[aria-label='Posting']",
                "div[data-testid='react-composer-post-button']",
                "div[role='button'][tabindex='0']",
                "button[type='submit']",
                "div[role='button'][aria-label*='Post']"
            ],
            'create_post_button': [
                "div[role='button'][aria-label*='Create a post']",
                "div[role='button'][aria-label*='Buat postingan']",
                "div[data-testid='status-attachment-mentions-input']"
            ]
        }

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

    def _setup_driver(self):
        """Setup Chrome WebDriver menggunakan Universal Driver Manager"""
        self._log("Setting up browser for Facebook...")
        
        try:
            if DRIVER_MANAGER_AVAILABLE:
                # Use Universal Driver Manager
                additional_options = [
                    '--disable-notifications',
                    '--disable-popup-blocking',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
                
                self.driver = get_chrome_driver(
                    headless=self.headless,
                    additional_options=additional_options
                )
                
            else:
                # Fallback to manual setup
                self._log("Universal Driver Manager not available, using fallback...", "WARNING")
                self._setup_driver_fallback()
            
            # Setup wait
            self.wait = WebDriverWait(self.driver, 30)
            
            self._log("Browser ready for Facebook", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to setup browser: {str(e)}", "ERROR")
            self._log("Troubleshooting tips:", "INFO")
            self._log("1. Run: python fix_all_drivers.py", "INFO")
            self._log("2. Install Google Chrome browser", "INFO")
            self._log("3. Download ChromeDriver from https://chromedriver.chromium.org/", "INFO")
            self._log("4. Place chromedriver.exe in your PATH or project folder", "INFO")
            self._log("5. Install webdriver-manager: pip install webdriver-manager", "INFO")
            raise

    def _setup_driver_fallback(self):
        """Fallback driver setup jika Universal Driver Manager tidak tersedia"""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1280,800")
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Additional options for Facebook
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Suppress logs
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try WebDriver Manager first
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                
                service = Service(
                    ChromeDriverManager().install(),
                    log_path=os.devnull,
                    service_args=['--silent']
                )
                
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e:
                self._log(f"WebDriver Manager failed: {e}", "WARNING")
                self._log("Trying system ChromeDriver...", "INFO")
                
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self._log(f"Failed to setup browser: {str(e)}", "ERROR")
            raise

    def _find_element_by_selectors(self, selectors: list, timeout: int = 10, visible: bool = True) -> Optional[Any]:
        """Find element using multiple selectors"""
        for i, selector in enumerate(selectors):
            try:
                if visible:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                else:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                
                if i == 0:
                    self._log("Element found", "SUCCESS")
                else:
                    self._log(f"Element found (alternative {i+1})", "SUCCESS")
                return element
                
            except TimeoutException:
                continue
                
        return None

    def load_cookies(self) -> bool:
        """Load cookies from JSON file"""
        if not self.cookies_path.exists():
            self._log("Facebook cookies file not found", "WARNING")
            return False
            
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
            else:
                cookies = cookies_data
            
            if not cookies:
                self._log("Cookies file is empty", "WARNING")
                return False
            
            # Navigate to Facebook first
            self.driver.get(self.home_url)
            time.sleep(3)
            
            # Add cookies
            cookies_added = 0
            for cookie in cookies:
                try:
                    if 'name' in cookie and 'value' in cookie:
                        clean_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.facebook.com'),
                            'path': cookie.get('path', '/'),
                        }
                        
                        if 'expiry' in cookie:
                            clean_cookie['expiry'] = int(cookie['expiry'])
                        elif 'expires' in cookie:
                            clean_cookie['expiry'] = int(cookie['expires'])
                        
                        if 'secure' in cookie:
                            clean_cookie['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            clean_cookie['httpOnly'] = cookie['httpOnly']
                        
                        self.driver.add_cookie(clean_cookie)
                        cookies_added += 1
                        
                except Exception as e:
                    if self.debug:
                        self._log(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}", "DEBUG")
            
            self._log(f"Cookies loaded: {cookies_added}/{len(cookies)}", "SUCCESS")
            return cookies_added > 0
            
        except Exception as e:
            self._log(f"Failed to load cookies: {str(e)}", "ERROR")
            return False

    def save_cookies(self):
        """Save cookies to JSON file"""
        try:
            cookies = self.driver.get_cookies()
            
            cookies_data = {
                "timestamp": int(time.time()),
                "cookies": cookies
            }
            
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            
            self._log(f"Cookies saved: {len(cookies)} items", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to save cookies: {str(e)}", "ERROR")

    def clear_cookies(self):
        """Clear cookies file"""
        try:
            if self.cookies_path.exists():
                self.cookies_path.unlink()
                self._log("Facebook cookies cleared", "SUCCESS")
            else:
                self._log("No Facebook cookies to clear", "WARNING")
        except Exception as e:
            self._log(f"Failed to clear cookies: {str(e)}", "ERROR")

    def check_login_required(self) -> bool:
        """Check if login is required"""
        current_url = self.driver.current_url
        return "login" in current_url or "checkpoint" in current_url

    def wait_for_login(self, timeout: int = 180):
        """Wait for user to login manually"""
        self._log("Please login manually in the browser...", "WARNING")
        self._log(f"Waiting for login completion (timeout {timeout} seconds)...", "INFO")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            
            # Check if no longer on login page
            if not ("login" in current_url or "checkpoint" in current_url):
                if "facebook.com" in current_url:
                    self._log("Login successful!", "SUCCESS")
                    self.save_cookies()
                    return True
            
            time.sleep(2)
        
        raise TimeoutException("Timeout waiting for login")

    def generate_ai_content(self, prompt: str, content_type: str = "status") -> Dict[str, Any]:
        """Generate AI content berdasarkan prompt"""
        if not self.ai_assistant:
            self._log("AI Assistant tidak tersedia", "WARNING")
            return self._generate_fallback_content(prompt, content_type)
        
        try:
            self._log(f"Generating AI content untuk: {prompt[:50]}...", "AI")
            
            # Build AI prompt berdasarkan content type
            if content_type == "status":
                ai_prompt = f"""
                Buat status Facebook yang menarik dan engaging berdasarkan topik: "{prompt}"
                
                Requirements:
                1. Tulis dalam bahasa Indonesia yang natural dan friendly
                2. Buat hook yang menarik di awal
                3. Tambahkan call-to-action yang engaging
                4. Sertakan 5-10 hashtag yang relevan dan trending
                5. Panjang ideal 100-300 karakter
                6. Gaya: conversational, relatable, dan shareable
                
                Format output sebagai JSON dengan keys:
                - title: Judul singkat
                - content: Konten status lengkap
                - hashtags: Array hashtag
                - cta: Call to action
                """
            
            elif content_type == "media":
                ai_prompt = f"""
                Buat caption Facebook untuk media (foto/video) dengan tema: "{prompt}"
                
                Requirements:
                1. Caption yang mendeskripsikan dan menarik perhatian
                2. Gunakan bahasa Indonesia yang engaging
                3. Tambahkan pertanyaan untuk encourage engagement
                4. Sertakan hashtag yang relevan
                5. Panjang ideal 50-200 karakter
                6. Gaya: visual storytelling, engaging
                
                Format output sebagai JSON dengan keys:
                - title: Judul singkat
                - content: Caption lengkap
                - hashtags: Array hashtag
                - cta: Call to action
                """
            
            elif content_type == "random":
                topics = [
                    "motivasi hari ini", "tips produktivitas", "cerita inspiratif",
                    "fakta menarik", "quote bijak", "tips kesehatan",
                    "teknologi terbaru", "lifestyle tips", "food review",
                    "travel experience", "hobby sharing", "life update"
                ]
                
                selected_topic = random.choice(topics)
                ai_prompt = f"""
                Buat status Facebook random yang menarik dengan topik: "{selected_topic}"
                
                Requirements:
                1. Konten original dan kreatif
                2. Bahasa Indonesia yang natural
                3. Relatable untuk audience umum
                4. Tambahkan element surprise atau insight
                5. Sertakan hashtag trending
                6. Gaya: spontan tapi berkualitas
                
                Format output sebagai JSON dengan keys:
                - title: Judul singkat
                - content: Konten status lengkap
                - hashtags: Array hashtag
                - cta: Call to action
                - topic: Topik yang dipilih
                """
            
            # Simulate AI response (replace with actual AI call)
            time.sleep(2)  # Simulate processing
            
            # Generate content based on prompt
            if "motivasi" in prompt.lower() or content_type == "random":
                ai_content = {
                    "title": "Motivasi Hari Ini",
                    "content": f"🌟 {prompt}\n\nSetiap hari adalah kesempatan baru untuk menjadi versi terbaik dari diri kita. Jangan biarkan kemarin menghalangi hari ini, dan jangan biarkan hari ini menghalangi masa depan yang cerah!\n\nApa yang memotivasi kalian hari ini? Share di komentar! 💪",
                    "hashtags": ["#motivasi", "#inspirasi", "#semangat", "#positivevibes", "#mindset", "#success", "#growth", "#motivation"],
                    "cta": "Share motivasi kalian di komentar!"
                }
            
            elif "tips" in prompt.lower():
                ai_content = {
                    "title": "Tips Berguna",
                    "content": f"💡 Tips: {prompt}\n\nHal kecil yang bisa membuat perbedaan besar dalam hidup kita. Kadang solusi terbaik adalah yang paling sederhana!\n\nAda tips lain yang ingin kalian share? Yuk berbagi di komentar! 🤝",
                    "hashtags": ["#tips", "#lifehacks", "#productivity", "#lifestyle", "#sharing", "#helpful", "#advice"],
                    "cta": "Share tips kalian juga di komentar!"
                }
            
            elif "cerita" in prompt.lower() or "story" in prompt.lower():
                ai_content = {
                    "title": "Cerita Menarik",
                    "content": f"📖 {prompt}\n\nSetiap orang punya cerita yang menarik untuk dibagikan. Kadang dari cerita sederhana kita bisa belajar hal yang luar biasa.\n\nApa cerita menarik kalian hari ini? 😊",
                    "hashtags": ["#cerita", "#story", "#sharing", "#experience", "#life", "#memories", "#storytelling"],
                    "cta": "Ceritakan pengalaman kalian di komentar!"
                }
            
            else:
                # General content
                ai_content = {
                    "title": "Update Status",
                    "content": f"✨ {prompt}\n\nSemoga hari kalian menyenangkan dan penuh berkah! Jangan lupa untuk selalu bersyukur dan berbagi kebaikan.\n\nHow's your day going? 😊",
                    "hashtags": ["#update", "#sharing", "#positivevibes", "#grateful", "#blessed", "#goodday"],
                    "cta": "Share kabar kalian di komentar!"
                }
            
            # Add topic if random
            if content_type == "random":
                ai_content["topic"] = prompt
            
            self._log("AI content generated successfully", "SUCCESS")
            return ai_content
            
        except Exception as e:
            self._log(f"AI content generation error: {e}", "WARNING")
            return self._generate_fallback_content(prompt, content_type)

    def _generate_fallback_content(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """Generate fallback content jika AI tidak tersedia"""
        fallback_templates = {
            "status": {
                "title": "Status Update",
                "content": f"{prompt}\n\nSemoga hari kalian menyenangkan! 😊",
                "hashtags": ["#update", "#sharing", "#facebook"],
                "cta": "Share pendapat kalian di komentar!"
            },
            "media": {
                "title": "Media Post",
                "content": f"{prompt}\n\nCheck out this amazing content!",
                "hashtags": ["#media", "#sharing", "#content"],
                "cta": "Like dan share jika kalian suka!"
            },
            "random": {
                "title": "Random Post",
                "content": "Semoga hari kalian penuh berkah dan kebahagiaan! ✨",
                "hashtags": ["#random", "#positivevibes", "#blessed"],
                "cta": "Share kabar kalian di komentar!"
            }
        }
        
        return fallback_templates.get(content_type, fallback_templates["status"])

    def create_facebook_post(self, content: str = "", media_path: str = "", 
                           use_ai: bool = False, ai_prompt: str = "", 
                           content_type: str = "status") -> Dict[str, Any]:
        """
        Create Facebook post dengan opsi AI content generation
        
        Args:
            content: Text content untuk post
            media_path: Path ke media file (optional)
            use_ai: Gunakan AI untuk generate content
            ai_prompt: Prompt untuk AI (jika use_ai=True)
            content_type: Jenis konten (status/media/random)
            
        Returns:
            Dict dengan status upload
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Load cookies
            cookies_loaded = self.load_cookies()
            
            # Navigate to Facebook
            self._log("Navigating to Facebook...")
            self.driver.get(self.home_url)
            time.sleep(3)
            
            # Check if login required
            if self.check_login_required():
                if cookies_loaded:
                    self._log("Cookies loaded but still need login, refreshing...", "WARNING")
                    self.driver.refresh()
                    time.sleep(3)
                
                if self.check_login_required():
                    self.wait_for_login()
                    self.driver.get(self.home_url)
                    time.sleep(3)
            
            # Generate AI content if requested
            final_content = content
            ai_content = {}
            
            if use_ai and ai_prompt:
                self._log("Generating AI content...", "AI")
                ai_content = self.generate_ai_content(ai_prompt, content_type)
                
                if ai_content:
                    # Use AI generated content
                    final_content = ai_content.get("content", content)
                    self._log(f"AI content generated: {final_content[:100]}...", "SUCCESS")
            
            # Find and click status input area
            self._log("Looking for status input...")
            
            # Try to find create post button first
            create_post_btn = self._find_element_by_selectors(self.selectors['create_post_button'], timeout=5)
            if create_post_btn:
                create_post_btn.click()
                time.sleep(2)
            
            # Find status input
            status_input = self._find_element_by_selectors(self.selectors['status_input'])
            
            if not status_input:
                raise NoSuchElementException("Status input not found")
            
            # Click status input to activate
            status_input.click()
            time.sleep(2)
            
            # Add media if provided
            if media_path and os.path.exists(media_path):
                self._log("Adding media to post...")
                
                # Look for photo/video button
                photo_video_btn = self._find_element_by_selectors(self.selectors['photo_video_button'], timeout=5)
                
                if photo_video_btn:
                    photo_video_btn.click()
                    time.sleep(2)
                
                # Find file input
                file_input = self._find_element_by_selectors(self.selectors['file_input'], timeout=10, visible=False)
                
                if file_input:
                    abs_path = os.path.abspath(media_path)
                    file_input.send_keys(abs_path)
                    self._log("Media uploaded successfully", "SUCCESS")
                    time.sleep(5)  # Wait for upload
                else:
                    self._log("File input not found", "WARNING")
            
            # Add text content
            if final_content.strip():
                self._log("Adding text content...")
                
                # Find the active text input (might have changed after media upload)
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                
                for text_input in text_inputs:
                    if text_input.is_displayed():
                        try:
                            text_input.click()
                            time.sleep(1)
                            
                            # Clear existing content
                            text_input.send_keys(Keys.CONTROL + "a")
                            text_input.send_keys(Keys.BACKSPACE)
                            time.sleep(0.5)
                            
                            # Add new content
                            text_input.send_keys(final_content)
                            self._log("Text content added", "SUCCESS")
                            break
                        except:
                            continue
            
            # Find and click post button
            self._log("Looking for post button...")
            post_button = self._find_element_by_selectors(self.selectors['post_button'])
            
            if not post_button:
                # Fallback: look for button with "Post" text
                buttons = self.driver.find_elements(By.TAG_NAME, "div")
                for button in buttons:
                    if button.text.lower() in ['post', 'posting', 'share', 'bagikan']:
                        if button.is_enabled() and button.is_displayed():
                            post_button = button
                            break
            
            if not post_button:
                raise NoSuchElementException("Post button not found")
            
            # Click post button
            self.driver.execute_script("arguments[0].click();", post_button)
            self._log("Post button clicked", "SUCCESS")
            time.sleep(5)
            
            # Check for success
            self._log("Facebook post created successfully!", "SUCCESS")
            
            return {
                "success": True,
                "message": "Post created successfully",
                "content": final_content,
                "media_path": media_path,
                "ai_content": ai_content if use_ai else None,
                "content_type": content_type
            }
            
        except Exception as e:
            error_msg = f"Facebook post creation failed: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Take screenshot for debugging
            self.take_screenshot(f"facebook_error_{int(time.time())}.png")
            
            return {
                "success": False,
                "message": error_msg,
                "content": final_content if 'final_content' in locals() else content,
                "media_path": media_path
            }
        
        finally:
            if self.driver:
                self._log("Closing browser...")
                self.driver.quit()

    def upload_status(self, status_text: str = "", media_path: str = "") -> Dict[str, Any]:
        """
        Upload status to Facebook (legacy method for compatibility)
        """
        return self.create_facebook_post(
            content=status_text,
            media_path=media_path,
            content_type="status"
        )

    def upload_reels(self, video_path: str, description: str = "") -> Dict[str, Any]:
        """
        Upload reels to Facebook (legacy method for compatibility)
        """
        return self.create_facebook_post(
            content=description,
            media_path=video_path,
            content_type="media"
        )

    def take_screenshot(self, filename: str = None):
        """Take screenshot for debugging"""
        if not filename:
            filename = f"facebook_screenshot_{int(time.time())}.png"
        
        screenshot_path = self.screenshots_dir / filename
        
        try:
            if self.driver:
                self.driver.save_screenshot(str(screenshot_path))
                self._log(f"Screenshot saved: {screenshot_path.name}", "INFO")
                return str(screenshot_path)
            else:
                self._log("No driver available for screenshot", "WARNING")
                return None
        except Exception as e:
            self._log(f"Failed to save screenshot: {str(e)}", "WARNING")
            return None

    def check_cookies_status(self):
        """Check Facebook cookies status"""
        if not self.cookies_path.exists():
            self._log("Facebook cookies file not found", "WARNING")
            return {"exists": False, "count": 0}
        
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
                timestamp = cookies_data.get('timestamp', 0)
            else:
                cookies = cookies_data if isinstance(cookies_data, list) else []
                timestamp = 0
            
            # Check expired cookies
            current_time = time.time()
            valid_cookies = []
            expired_cookies = []
            
            for cookie in cookies:
                if 'expiry' in cookie:
                    if cookie['expiry'] > current_time:
                        valid_cookies.append(cookie)
                    else:
                        expired_cookies.append(cookie)
                elif 'expires' in cookie:
                    if cookie['expires'] > current_time:
                        valid_cookies.append(cookie)
                    else:
                        expired_cookies.append(cookie)
                else:
                    valid_cookies.append(cookie)
            
            self._log(f"Total Facebook cookies: {len(cookies)}", "INFO")
            self._log(f"Valid cookies: {len(valid_cookies)}", "SUCCESS")
            
            if expired_cookies:
                self._log(f"Expired cookies: {len(expired_cookies)}", "WARNING")
            
            if timestamp:
                import datetime
                saved_time = datetime.datetime.fromtimestamp(timestamp)
                self._log(f"Cookies saved: {saved_time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
            
            return {
                "exists": True,
                "total": len(cookies),
                "valid": len(valid_cookies),
                "expired": len(expired_cookies),
                "timestamp": timestamp
            }
            
        except Exception as e:
            self._log(f"Error reading Facebook cookies: {str(e)}", "ERROR")
            return {"exists": True, "error": str(e)}

    def interactive_facebook_menu(self):
        """Interactive menu untuk Facebook posting"""
        print(f"\n{Fore.BLUE}📘 Facebook Unified Uploader")
        print("=" * 50)
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih jenis post:")
            print("1. 📝 Text Status Only")
            print("2. 🖼️ Text + Media (Image/Video)")
            print("3. 🤖 AI Generated Status")
            print("4. 🎲 Random AI Content")
            print("5. 🍪 Check Cookies Status")
            print("6. 🗑️ Clear Cookies")
            print("7. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-7): ").strip()
            
            if choice == "1":
                self._interactive_text_status()
            elif choice == "2":
                self._interactive_text_media()
            elif choice == "3":
                self._interactive_ai_status()
            elif choice == "4":
                self._interactive_random_ai()
            elif choice == "5":
                self.check_cookies_status()
            elif choice == "6":
                confirm = input(f"{Fore.YELLOW}Clear Facebook cookies? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.clear_cookies()
            elif choice == "7":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")

    def _interactive_text_status(self):
        """Interactive text status posting"""
        print(f"\n{Fore.CYAN}📝 TEXT STATUS POSTING:")
        
        status_text = input(f"{Fore.WHITE}Masukkan status text: ").strip()
        if not status_text:
            print(f"{Fore.RED}❌ Status text tidak boleh kosong!")
            return
        
        result = self.create_facebook_post(
            content=status_text,
            content_type="status"
        )
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Status berhasil dipost!")
        else:
            print(f"{Fore.RED}❌ Status gagal: {result['message']}")

    def _interactive_text_media(self):
        """Interactive text + media posting"""
        print(f"\n{Fore.CYAN}🖼️ TEXT + MEDIA POSTING:")
        
        media_path = input(f"{Fore.WHITE}Path ke file media: ").strip()
        if not os.path.exists(media_path):
            print(f"{Fore.RED}❌ File media tidak ditemukan!")
            return
        
        caption = input(f"{Fore.WHITE}Caption untuk media (optional): ").strip()
        
        result = self.create_facebook_post(
            content=caption,
            media_path=media_path,
            content_type="media"
        )
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Post dengan media berhasil!")
        else:
            print(f"{Fore.RED}❌ Post gagal: {result['message']}")

    def _interactive_ai_status(self):
        """Interactive AI generated status"""
        print(f"\n{Fore.CYAN}🤖 AI GENERATED STATUS:")
        
        if not self.ai_assistant:
            print(f"{Fore.RED}❌ AI Assistant tidak tersedia!")
            print(f"{Fore.YELLOW}Install dengan: pip install google-generativeai")
            print(f"{Fore.YELLOW}Set API key: set GEMINI_API_KEY=your_api_key")
            return
        
        print(f"{Fore.YELLOW}Contoh prompt:")
        print("• motivasi untuk hari senin")
        print("• tips produktivitas kerja")
        print("• cerita inspiratif tentang kesuksesan")
        print("• review makanan enak")
        print("• sharing pengalaman traveling")
        
        ai_prompt = input(f"\n{Fore.WHITE}Masukkan prompt untuk AI: ").strip()
        if not ai_prompt:
            print(f"{Fore.RED}❌ Prompt tidak boleh kosong!")
            return
        
        result = self.create_facebook_post(
            use_ai=True,
            ai_prompt=ai_prompt,
            content_type="status"
        )
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ AI status berhasil dipost!")
            if result.get("ai_content"):
                ai_content = result["ai_content"]
                print(f"\n{Fore.CYAN}📋 AI Generated Content:")
                print(f"Title: {ai_content.get('title', 'N/A')}")
                print(f"Content: {ai_content.get('content', 'N/A')[:100]}...")
                print(f"Hashtags: {', '.join(ai_content.get('hashtags', []))}")
        else:
            print(f"{Fore.RED}❌ AI status gagal: {result['message']}")

    def _interactive_random_ai(self):
        """Interactive random AI content"""
        print(f"\n{Fore.CYAN}🎲 RANDOM AI CONTENT:")
        
        if not self.ai_assistant:
            print(f"{Fore.RED}❌ AI Assistant tidak tersedia!")
            return
        
        print(f"{Fore.YELLOW}AI akan generate konten random yang menarik...")
        
        confirm = input(f"{Fore.WHITE}Generate random AI content? (Y/n): ").strip().lower()
        if confirm == 'n':
            return
        
        # Generate random prompt
        random_prompts = [
            "motivasi untuk memulai hari",
            "tips hidup sehat dan bahagia",
            "cerita inspiratif singkat",
            "fakta menarik yang jarang diketahui",
            "quote bijak untuk kehidupan",
            "tips produktivitas sederhana",
            "sharing pengalaman positif",
            "refleksi tentang kehidupan"
        ]
        
        random_prompt = random.choice(random_prompts)
        
        result = self.create_facebook_post(
            use_ai=True,
            ai_prompt=random_prompt,
            content_type="random"
        )
        
        if result["success"]:
            print(f"{Fore.GREEN}✅ Random AI content berhasil dipost!")
            if result.get("ai_content"):
                ai_content = result["ai_content"]
                print(f"\n{Fore.CYAN}📋 Generated Content:")
                print(f"Topic: {ai_content.get('topic', random_prompt)}")
                print(f"Title: {ai_content.get('title', 'N/A')}")
                print(f"Content: {ai_content.get('content', 'N/A')[:150]}...")
        else:
            print(f"{Fore.RED}❌ Random AI content gagal: {result['message']}")


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="Facebook Unified Uploader")
    parser.add_argument("--content", "-c", help="Text content untuk post")
    parser.add_argument("--media", "-m", help="Path ke media file")
    parser.add_argument("--ai", action="store_true", help="Gunakan AI untuk generate content")
    parser.add_argument("--prompt", "-p", help="Prompt untuk AI content generation")
    parser.add_argument("--type", choices=['status', 'media', 'random'], default='status', help="Content type")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-cookies", action="store_true", help="Clear cookies")
    parser.add_argument("--check-cookies", action="store_true", help="Check cookies status")
    
    args = parser.parse_args()
    
    uploader = FacebookUploader(headless=args.headless, debug=args.debug)
    
    # Handle different actions
    if args.clear_cookies:
        uploader.clear_cookies()
        return
    
    if args.check_cookies:
        uploader.check_cookies_status()
        return
    
    if args.content or args.media or args.ai:
        # Command line mode
        result = uploader.create_facebook_post(
            content=args.content or "",
            media_path=args.media or "",
            use_ai=args.ai,
            ai_prompt=args.prompt or "",
            content_type=args.type
        )
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 Facebook post berhasil!")
            if result.get("ai_content"):
                print(f"{Fore.CYAN}AI Content: {result['ai_content']['title']}")
        else:
            print(f"{Fore.RED}❌ Facebook post gagal: {result['message']}")
            sys.exit(1)
    
    else:
        # Interactive mode
        uploader.interactive_facebook_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)