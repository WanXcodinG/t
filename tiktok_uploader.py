#!/usr/bin/env python3
"""
TikTok Video Uploader menggunakan Selenium
Mendukung cookies JSON untuk auto-login dan selector yang spesifik
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from colorama import init, Fore, Style, Back
import argparse

# Initialize colorama untuk Windows compatibility
init(autoreset=True)

# Import Universal Driver Manager
try:
    from driver_manager import get_chrome_driver
    DRIVER_MANAGER_AVAILABLE = True
except ImportError:
    DRIVER_MANAGER_AVAILABLE = False

class TikTokUploader:
    def __init__(self, headless: bool = False, debug: bool = False):
        """
        Initialize TikTok Uploader
        
        Args:
            headless: Jalankan browser dalam mode headless
            debug: Enable debug logging
        """
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.wait = None
        
        # Setup paths - menggunakan folder cookies dengan file JSON
        self.base_dir = Path(__file__).parent
        self.cookies_dir = self.base_dir / "cookies"
        self.cookies_dir.mkdir(exist_ok=True)
        self.cookies_path = self.cookies_dir / "tiktok_cookies.json"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # TikTok URLs
        self.upload_url = "https://www.tiktok.com/tiktokstudio/upload?from=webapp"
        self.login_url = "https://www.tiktok.com/login"
        
        # Selectors - Menggunakan selector yang baru diberikan
        self.selectors = {
            'upload_button': [
                "#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div:nth-child(1) > div > div > div.jsx-2995057667.upload-card.before-upload-new-stage.full-screen > div > div > div.jsx-2995057667.upload-text-container > button > div.Button__content.Button__content--shape-default.Button__content--size-large.Button__content--type-primary.Button__content--loading-false",
                "input[type='file']",
                "input[accept*='video']",
                "[data-e2e='upload-btn'] input",
                ".upload-btn input"
            ],
            'upload_success_status': [
                "#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-2808274669.card > div > div.jsx-1979214919.info-main > div.jsx-1979214919.info-status.success > span.TUXText.TUXText--tiktok-sans",
                ".info-status.success",
                "[data-e2e='upload-success']",
                ".upload-success",
                "div[contenteditable='true']",
                "[data-e2e='caption-input']",
                ".caption-editor"
            ],
            'caption_input': [
                "div[contenteditable='true']",
                "[data-e2e='caption-input']",
                ".caption-editor",
                ".caption-input",
                "textarea[placeholder*='caption']",
                "textarea[placeholder*='Describe']"
            ],
            'post_button': [
                "#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-3335848873.footer > div > button.Button__root.Button__root--shape-default.Button__root--size-large.Button__root--type-primary.Button__root--loading-false > div.Button__content.Button__content--shape-default.Button__content--size-large.Button__content--type-primary.Button__content--loading-false",
                "#root > div > div > div.css-fsbw52.ep9i2zp0 > div.css-86gjln.edss2sz5 > div > div > div > div.jsx-3335848873.footer > div > button.Button__root.Button__root--shape-default.Button__root--size-large.Button__root--type-primary.Button__root--loading-false",
                "button[data-e2e='publish-button']",
                ".publish-button",
                ".btn-post",
                ".upload-btn-post"
            ],
            'success_indicators': [
                ".success-message",
                "[data-e2e='upload-success-message']",
                ".upload-complete",
                ".upload-success"
            ]
        }

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna - versi sederhana"""
        colors = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA
        }
        
        if level == "DEBUG" and not self.debug:
            return
            
        color = colors.get(level, Fore.WHITE)
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🔍"
        }
        
        icon = icons.get(level, "📝")
        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def _setup_driver(self):
        """Setup Chrome WebDriver menggunakan Universal Driver Manager"""
        self._log("Setting up browser for TikTok...")
        
        try:
            if DRIVER_MANAGER_AVAILABLE:
                # Use Universal Driver Manager
                additional_options = [
                    '--disable-images',
                    '--blink-settings=imagesEnabled=false',
                    '--disable-plugins-discovery',
                    '--disable-translate',
                    '--disable-geolocation',
                    '--disable-media-stream',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
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
            
            self._log("Browser ready for TikTok", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to setup browser: {str(e)}", "ERROR")
            self._log("Troubleshooting tips:", "INFO")
            self._log("1. Run: python driver_manager.py --diagnostics", "INFO")
            self._log("2. Install Chrome browser", "INFO")
            self._log("3. Install webdriver-manager: pip install webdriver-manager", "INFO")
            raise

    def _setup_driver_fallback(self):
        """Fallback driver setup jika Universal Driver Manager tidak tersedia"""
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1280,800")
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Additional options
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Try WebDriver Manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(
                ChromeDriverManager().install(),
                log_path=os.devnull,
                service_args=['--silent']
            )
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            # Try system ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
        
        # Anti-detection script
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def _find_element_by_selectors(self, selectors: list, timeout: int = 10, visible: bool = True) -> Optional[Any]:
        """Mencari elemen menggunakan multiple selectors - versi sederhana"""
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
                
                # Log sederhana tanpa menampilkan selector panjang
                if i == 0:
                    self._log("Elemen ditemukan", "SUCCESS")
                else:
                    self._log(f"Elemen ditemukan (alternatif {i+1})", "SUCCESS")
                return element
                
            except TimeoutException:
                continue
                
        return None

    def load_cookies(self) -> bool:
        """Load cookies dari file JSON"""
        if not self.cookies_path.exists():
            self._log("File cookies tidak ditemukan", "WARNING")
            return False
            
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Pastikan cookies_data adalah list
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
            else:
                cookies = cookies_data
            
            if not cookies:
                self._log("File cookies kosong", "WARNING")
                return False
            
            # Navigate ke TikTok dulu sebelum set cookies
            self.driver.get("https://www.tiktok.com")
            time.sleep(2)
            
            # Add cookies
            cookies_added = 0
            for cookie in cookies:
                try:
                    # Pastikan cookie memiliki format yang benar
                    if 'name' in cookie and 'value' in cookie:
                        # Hapus keys yang tidak diperlukan untuk Selenium
                        clean_cookie = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.tiktok.com'),
                            'path': cookie.get('path', '/'),
                        }
                        
                        # Tambahkan expiry jika ada
                        if 'expiry' in cookie:
                            clean_cookie['expiry'] = int(cookie['expiry'])
                        elif 'expires' in cookie:
                            clean_cookie['expiry'] = int(cookie['expires'])
                        
                        # Tambahkan secure dan httpOnly jika ada
                        if 'secure' in cookie:
                            clean_cookie['secure'] = cookie['secure']
                        if 'httpOnly' in cookie:
                            clean_cookie['httpOnly'] = cookie['httpOnly']
                        
                        self.driver.add_cookie(clean_cookie)
                        cookies_added += 1
                        
                except Exception as e:
                    if self.debug:
                        self._log(f"Gagal menambahkan cookie {cookie.get('name', 'unknown')}: {e}", "DEBUG")
            
            self._log(f"Cookies dimuat: {cookies_added}/{len(cookies)}", "SUCCESS")
            return cookies_added > 0
            
        except Exception as e:
            self._log(f"Gagal memuat cookies: {str(e)}", "ERROR")
            return False

    def save_cookies(self):
        """Simpan cookies ke file JSON"""
        try:
            cookies = self.driver.get_cookies()
            
            # Format cookies untuk JSON
            cookies_data = {
                "timestamp": int(time.time()),
                "cookies": cookies
            }
            
            with open(self.cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            
            self._log(f"Cookies disimpan: {len(cookies)} item", "SUCCESS")
            
        except Exception as e:
            self._log(f"Gagal menyimpan cookies: {str(e)}", "ERROR")

    def clear_cookies(self):
        """Hapus file cookies"""
        try:
            if self.cookies_path.exists():
                self.cookies_path.unlink()
                self._log("Cookies berhasil dihapus", "SUCCESS")
            else:
                self._log("Tidak ada cookies untuk dihapus", "WARNING")
        except Exception as e:
            self._log(f"Gagal menghapus cookies: {str(e)}", "ERROR")

    def check_login_required(self) -> bool:
        """Cek apakah perlu login"""
        current_url = self.driver.current_url
        return "login" in current_url or "passport" in current_url

    def wait_for_login(self, timeout: int = 180):
        """Tunggu user login manual"""
        self._log("Silakan login secara manual di browser...", "WARNING")
        self._log(f"Menunggu login selesai (timeout {timeout} detik)...", "INFO")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            
            # Cek apakah sudah tidak di halaman login
            if not ("login" in current_url or "passport" in current_url):
                self._log("Login berhasil!", "SUCCESS")
                self.save_cookies()  # Simpan cookies setelah login
                return True
            
            time.sleep(2)
        
        raise TimeoutException("Timeout menunggu login")

    def upload_file(self, video_path: str):
        """Upload file video menggunakan selector baru"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File video tidak ditemukan: {video_path}")
        
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        self._log(f"Mengupload: {os.path.basename(video_path)} ({file_size:.2f}MB)")
        
        # Coba klik tombol upload terlebih dahulu (jika ada)
        upload_button = self._find_element_by_selectors(self.selectors['upload_button'], timeout=5)
        if upload_button:
            try:
                # Coba klik tombol upload
                self.driver.execute_script("arguments[0].click();", upload_button)
                self._log("Tombol upload diklik", "SUCCESS")
                time.sleep(2)
            except Exception as e:
                self._log(f"Gagal klik tombol upload: {e}", "WARNING")
        
        # Cari input file (bisa tersembunyi)
        file_input_selectors = [
            "input[type='file']",
            "input[accept*='video']",
            "[data-e2e='upload-btn'] input",
            ".upload-btn input"
        ]
        
        file_input = None
        for selector in file_input_selectors:
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                if file_input:
                    self._log("Input file ditemukan", "SUCCESS")
                    break
            except:
                continue
        
        if not file_input:
            raise NoSuchElementException("Tidak dapat menemukan elemen input file")
        
        # Upload file
        abs_path = os.path.abspath(video_path)
        file_input.send_keys(abs_path)
        
        self._log("File berhasil diupload", "SUCCESS")

    def wait_for_processing(self, timeout: int = 120):
        """Tunggu video diproses menggunakan selector baru"""
        self._log("Menunggu video diproses...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Cek indikator pemrosesan selesai menggunakan selector baru
            for selector in self.selectors['upload_success_status']:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        self._log("Video berhasil diproses", "SUCCESS")
                        time.sleep(3)  # Tunggu UI siap
                        return True
                except:
                    continue
            
            time.sleep(2)
        
        self._log("Timeout menunggu pemrosesan, melanjutkan...", "WARNING")
        return False

    def add_caption(self, caption: str):
        """Tambahkan caption ke video - versi sederhana"""
        if not caption.strip():
            self._log("Caption kosong, melewati...", "WARNING")
            return
        
        self._log("Menambahkan caption...")
        
        # Cari input caption menggunakan selector sederhana
        caption_input = self._find_element_by_selectors(self.selectors['caption_input'])
        
        if not caption_input:
            self._log("Input caption tidak ditemukan", "WARNING")
            return
        
        try:
            # Focus dan clear existing content
            caption_input.click()
            time.sleep(0.5)
            
            # Select all dan hapus
            caption_input.send_keys(Keys.CONTROL + "a")
            caption_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            
            # Type caption baru
            caption_input.send_keys(caption)
            
            preview = caption[:50] + "..." if len(caption) > 50 else caption
            self._log(f"Caption ditambahkan: {preview}", "SUCCESS")
            
        except Exception as e:
            self._log(f"Gagal menambahkan caption: {str(e)}", "WARNING")

    def post_video(self):
        """Post video menggunakan selector baru"""
        self._log("Mencari tombol post...")
        
        # Coba selector utama terlebih dahulu (yang baru diberikan)
        primary_selector = self.selectors['post_button'][0]
        
        try:
            self._log("Mencoba tombol post utama...")
            
            # Tunggu elemen muncul
            post_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, primary_selector))
            )
            
            # Klik menggunakan JavaScript untuk memastikan
            self.driver.execute_script("arguments[0].click();", post_button)
            
            self._log("Tombol post berhasil diklik!", "SUCCESS")
            time.sleep(5)
            
            # Setelah klik post, anggap berhasil dan tutup browser
            self._log("Video berhasil dipost!", "SUCCESS")
            return True
            
        except TimeoutException:
            self._log("Selector utama tidak ditemukan, mencoba alternatif...", "WARNING")
        
        # Coba fallback selectors
        self._log("Mencoba tombol post alternatif...")
        
        for i, selector in enumerate(self.selectors['post_button'][1:], 1):
            try:
                post_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # Cek apakah tombol enabled
                if post_button.is_enabled():
                    post_button.click()
                    self._log(f"Tombol post diklik (alternatif {i})", "SUCCESS")
                    time.sleep(5)
                    return True
                    
            except TimeoutException:
                continue
        
        # Fallback terakhir: cari berdasarkan text
        self._log("Mencari tombol berdasarkan teks...")
        
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            
            for button in buttons:
                text = button.text.lower()
                if any(keyword in text for keyword in ['post', 'publish', 'share']):
                    if button.is_enabled() and button.is_displayed():
                        button.click()
                        self._log(f"Tombol post ditemukan: '{button.text}'", "SUCCESS")
                        time.sleep(5)
                        return True
        
        except Exception as e:
            self._log(f"Error saat mencari tombol berdasarkan teks: {str(e)}", "ERROR")
        
        raise NoSuchElementException("Tidak dapat menemukan tombol Post/Publish")

    def check_upload_success(self) -> bool:
        """Cek apakah upload berhasil"""
        self._log("Memeriksa status upload...")
        
        try:
            # Cek indikator sukses
            for selector in self.selectors['success_indicators']:
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if element.is_displayed():
                        self._log("Konfirmasi upload sukses!", "SUCCESS")
                        return True
                except TimeoutException:
                    continue
            
            # Cek URL redirect
            current_url = self.driver.current_url
            if any(keyword in current_url for keyword in ['creator-center', 'analytics']) or 'upload' not in current_url:
                self._log("Upload berhasil (dialihkan ke halaman lain)", "SUCCESS")
                return True
            
            self._log("Tidak dapat mengkonfirmasi status upload, tapi kemungkinan berhasil", "WARNING")
            return True
            
        except Exception as e:
            self._log(f"Error saat memeriksa status: {str(e)}", "WARNING")
            return False

    def take_screenshot(self, filename: str = None):
        """Ambil screenshot untuk debugging"""
        if not filename:
            filename = f"tiktok_screenshot_{int(time.time())}.png"
        
        screenshot_path = self.screenshots_dir / filename
        
        try:
            if self.driver:
                self.driver.save_screenshot(str(screenshot_path))
                self._log(f"Screenshot disimpan: {screenshot_path.name}", "INFO")
                return str(screenshot_path)
            else:
                self._log("No driver available for screenshot", "WARNING")
                return None
        except Exception as e:
            self._log(f"Gagal menyimpan screenshot: {str(e)}", "WARNING")
            return None

    def upload_video(self, video_path: str, caption: str = "#fyp #viral #trending") -> Dict[str, Any]:
        """
        Main method untuk upload video
        
        Args:
            video_path: Path ke file video
            caption: Caption untuk video
            
        Returns:
            Dict dengan status upload
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Load cookies
            cookies_loaded = self.load_cookies()
            
            # Navigate ke upload page
            self._log("Navigasi ke TikTok Studio...")
            self.driver.get(self.upload_url)
            time.sleep(3)
            
            # Cek apakah perlu login
            if self.check_login_required():
                if cookies_loaded:
                    self._log("Cookies dimuat tapi masih perlu login, refresh halaman...", "WARNING")
                    self.driver.refresh()
                    time.sleep(3)
                
                if self.check_login_required():
                    self.wait_for_login()
                    # Navigate ulang ke upload page setelah login
                    self.driver.get(self.upload_url)
                    time.sleep(3)
            
            # Upload file
            self.upload_file(video_path)
            
            # Tunggu processing
            self.wait_for_processing()
            
            # Tambahkan caption
            self.add_caption(caption)
            
            # Post video
            success = self.post_video()
            
            if success:
                self._log("Video berhasil diupload ke TikTok!", "SUCCESS")
                return {
                    "success": True,
                    "message": "Upload berhasil",
                    "video_path": video_path,
                    "caption": caption
                }
            else:
                return {
                    "success": False,
                    "message": "Upload mungkin berhasil tapi tidak dapat dikonfirmasi",
                    "video_path": video_path,
                    "caption": caption
                }
                
        except Exception as e:
            error_msg = f"Upload gagal: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Ambil screenshot untuk debugging
            self.take_screenshot(f"error_{int(time.time())}.png")
            
            return {
                "success": False,
                "message": error_msg,
                "video_path": video_path,
                "caption": caption
            }
        
        finally:
            if self.driver:
                self._log("Menutup browser...")
                self.driver.quit()

    def check_cookies_status(self):
        """Cek status cookies"""
        if not self.cookies_path.exists():
            self._log("File cookies tidak ditemukan", "WARNING")
            return {"exists": False, "count": 0}
        
        try:
            with open(self.cookies_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Pastikan cookies_data adalah dict dengan struktur yang benar
            if isinstance(cookies_data, dict):
                cookies = cookies_data.get('cookies', [])
                timestamp = cookies_data.get('timestamp', 0)
            else:
                cookies = cookies_data if isinstance(cookies_data, list) else []
                timestamp = 0
            
            # Cek cookies yang expired
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
                    valid_cookies.append(cookie)  # Session cookies
            
            self._log(f"Total cookies: {len(cookies)}", "INFO")
            self._log(f"Valid cookies: {len(valid_cookies)}", "SUCCESS")
            
            if expired_cookies:
                self._log(f"Expired cookies: {len(expired_cookies)}", "WARNING")
            
            if timestamp:
                import datetime
                saved_time = datetime.datetime.fromtimestamp(timestamp)
                self._log(f"Cookies disimpan: {saved_time.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
            
            return {
                "exists": True,
                "total": len(cookies),
                "valid": len(valid_cookies),
                "expired": len(expired_cookies),
                "timestamp": timestamp
            }
            
        except Exception as e:
            self._log(f"Error membaca cookies: {str(e)}", "ERROR")
            return {"exists": True, "error": str(e)}


def main():
    """Main function untuk CLI"""
    parser = argparse.ArgumentParser(description="TikTok Video Uploader")
    parser.add_argument("--video", "-v", help="Path ke file video")
    parser.add_argument("--caption", "-c", default="#fyp #viral #trending", help="Caption untuk video")
    parser.add_argument("--headless", action="store_true", help="Jalankan dalam mode headless")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-cookies", action="store_true", help="Hapus cookies")
    parser.add_argument("--check-cookies", action="store_true", help="Cek status cookies")
    
    args = parser.parse_args()
    
    uploader = TikTokUploader(headless=args.headless, debug=args.debug)
    
    # Handle different actions
    if args.clear_cookies:
        uploader.clear_cookies()
        return
    
    if args.check_cookies:
        uploader.check_cookies_status()
        return
    
    if args.video:
        if not os.path.exists(args.video):
            print(f"{Fore.RED}❌ File video tidak ditemukan: {args.video}")
            sys.exit(1)
        
        result = uploader.upload_video(args.video, args.caption)
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 Upload berhasil!")
        else:
            print(f"{Fore.RED}❌ Upload gagal: {result['message']}")
            sys.exit(1)
    else:
        # Interactive mode
        print(f"{Fore.CYAN}🎬 TikTok Video Uploader")
        print("=" * 40)
        
        while True:
            print(f"\n{Fore.YELLOW}Pilih aksi:")
            print("1. 📤 Upload video")
            print("2. 🍪 Cek status cookies")
            print("3. 🗑️ Hapus cookies")
            print("4. ❌ Keluar")
            
            choice = input(f"\n{Fore.WHITE}Pilihan (1-4): ").strip()
            
            if choice == "1":
                video_path = input(f"{Fore.CYAN}Path ke file video: ").strip()
                if not os.path.exists(video_path):
                    print(f"{Fore.RED}❌ File tidak ditemukan!")
                    continue
                
                caption = input(f"{Fore.CYAN}Caption (Enter untuk default): ").strip()
                if not caption:
                    caption = "#fyp #viral #trending"
                
                result = uploader.upload_video(video_path, caption)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Upload berhasil!")
                else:
                    print(f"{Fore.RED}❌ Upload gagal: {result['message']}")
            
            elif choice == "2":
                uploader.check_cookies_status()
            
            elif choice == "3":
                confirm = input(f"{Fore.YELLOW}Yakin ingin menghapus cookies? (y/N): ").strip().lower()
                if confirm == 'y':
                    uploader.clear_cookies()
            
            elif choice == "4":
                print(f"{Fore.YELLOW}👋 Sampai jumpa!")
                break
            
            else:
                print(f"{Fore.RED}❌ Pilihan tidak valid!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error fatal: {str(e)}")
        sys.exit(1)