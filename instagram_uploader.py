#!/usr/bin/env python3
"""
Instagram Uploader menggunakan Selenium
Mendukung upload Reels dan Posts dengan cookies JSON untuk auto-login
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

class InstagramUploader:
    def __init__(self, headless: bool = False, debug: bool = False):
        """
        Initialize Instagram Uploader
        
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
        self.cookies_path = self.cookies_dir / "instagram_cookies.json"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Instagram URLs
        self.home_url = "https://www.instagram.com"
        self.create_url = "https://www.instagram.com/create/select/"
        self.login_url = "https://www.instagram.com/accounts/login/"
        
        # Selectors untuk Instagram
        self.selectors = {
            'create_button': [
                "svg[aria-label='New post']",
                "a[href='/create/select/']",
                "[data-testid='new-post-button']",
                "div[role='menuitem']"
            ],
            'file_input': [
                "input[type='file']",
                "input[accept*='image']",
                "input[accept*='video']"
            ],
            'next_button': [
                "button:contains('Next')",
                "button[type='button']",
                "div[role='button']"
            ],
            'share_button': [
                "button:contains('Share')",
                "button[type='button']"
            ],
            'caption_textarea': [
                "textarea[aria-label='Write a caption...']",
                "textarea[placeholder*='caption']",
                "div[contenteditable='true']"
            ],
            'reels_tab': [
                "button:contains('Reels')",
                "[data-testid='reels-tab']"
            ],
            'post_tab': [
                "button:contains('Post')",
                "[data-testid='post-tab']"
            ]
        }

    def _log(self, message: str, level: str = "INFO"):
        """Enhanced logging dengan warna"""
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
        """Setup Chrome WebDriver dengan konfigurasi optimal untuk Instagram"""
        self._log("Setting up browser for Instagram...")
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1280,800")
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        # Instagram-specific options
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
            # Try to find ChromeDriver automatically
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Setup ChromeDriver dengan log suppression
                service = Service(
                    ChromeDriverManager().install(),
                    log_path=os.devnull,
                    service_args=['--silent']
                )
                
                # Suppress Selenium logs
                os.environ['WDM_LOG_LEVEL'] = '0'
                os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
                
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
            except Exception as e:
                self._log(f"WebDriver Manager failed: {e}", "WARNING")
                self._log("Trying system ChromeDriver...", "INFO")
                
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 30)
            
            self._log("Browser ready for Instagram", "SUCCESS")
            
        except Exception as e:
            self._log(f"Failed to setup browser: {str(e)}", "ERROR")
            self._log("Possible solutions:", "INFO")
            self._log("1. Install Chrome browser", "INFO")
            self._log("2. Update Chrome to latest version", "INFO")
            self._log("3. Install ChromeDriver manually", "INFO")
            self._log("4. Check if antivirus is blocking ChromeDriver", "INFO")
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

    def _find_element_by_text(self, text: str, tag: str = "*", timeout: int = 10) -> Optional[Any]:
        """Find element by text content"""
        try:
            xpath = f"//{tag}[contains(text(), '{text}')]"
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            return element
        except TimeoutException:
            return None

    def load_cookies(self) -> bool:
        """Load cookies from JSON file"""
        if not self.cookies_path.exists():
            self._log("Instagram cookies file not found", "WARNING")
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
            
            # Navigate to Instagram first
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
                            'domain': cookie.get('domain', '.instagram.com'),
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
                self._log("Instagram cookies cleared", "SUCCESS")
            else:
                self._log("No Instagram cookies to clear", "WARNING")
        except Exception as e:
            self._log(f"Failed to clear cookies: {str(e)}", "ERROR")

    def check_login_required(self) -> bool:
        """Check if login is required"""
        current_url = self.driver.current_url
        return "login" in current_url or "accounts/login" in current_url

    def wait_for_login(self, timeout: int = 180):
        """Wait for user to login manually"""
        self._log("Please login manually in the browser...", "WARNING")
        self._log(f"Waiting for login completion (timeout {timeout} seconds)...", "INFO")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            
            # Check if no longer on login page
            if not ("login" in current_url or "accounts/login" in current_url):
                if "instagram.com" in current_url:
                    self._log("Login successful!", "SUCCESS")
                    self.save_cookies()
                    return True
            
            time.sleep(2)
        
        raise TimeoutException("Timeout waiting for login")

    def upload_post(self, media_path: str, caption: str = "", is_reel: bool = False) -> Dict[str, Any]:
        """
        Upload post atau reel ke Instagram
        
        Args:
            media_path: Path to media file (image/video)
            caption: Caption for the post
            is_reel: True for Reels, False for regular post
            
        Returns:
            Dict with upload status
        """
        try:
            # Setup driver
            self._setup_driver()
            
            # Load cookies
            cookies_loaded = self.load_cookies()
            
            # Navigate to Instagram
            self._log("Navigating to Instagram...")
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
            
            # Click create button
            self._log("Looking for create button...")
            
            # Try multiple ways to find create button
            create_button = None
            
            # Method 1: Try SVG with aria-label
            try:
                create_button = self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='New post']")
                if create_button:
                    # Click the parent element
                    create_button = create_button.find_element(By.XPATH, "./..")
            except:
                pass
            
            # Method 2: Try direct link
            if not create_button:
                try:
                    create_button = self.driver.find_element(By.CSS_SELECTOR, "a[href='/create/select/']")
                except:
                    pass
            
            # Method 3: Navigate directly to create page
            if not create_button:
                self._log("Create button not found, navigating directly to create page...", "WARNING")
                self.driver.get(self.create_url)
                time.sleep(3)
            else:
                create_button.click()
                time.sleep(3)
            
            # Upload file
            self._log("Uploading media file...")
            
            # Find file input
            file_input = self._find_element_by_selectors(self.selectors['file_input'], timeout=10, visible=False)
            
            if not file_input:
                raise NoSuchElementException("File input not found")
            
            # Upload file
            abs_path = os.path.abspath(media_path)
            file_input.send_keys(abs_path)
            self._log("Media uploaded successfully", "SUCCESS")
            time.sleep(5)
            
            # Select Reels or Post
            if is_reel:
                self._log("Selecting Reels...")
                reels_tab = self._find_element_by_text("Reels", "button", timeout=5)
                if reels_tab:
                    reels_tab.click()
                    time.sleep(2)
            else:
                self._log("Selecting Post...")
                post_tab = self._find_element_by_text("Post", "button", timeout=5)
                if post_tab:
                    post_tab.click()
                    time.sleep(2)
            
            # Click Next button(s)
            self._log("Proceeding through upload steps...")
            
            # May need to click Next multiple times
            for step in range(3):
                next_button = self._find_element_by_text("Next", "button", timeout=10)
                if next_button:
                    next_button.click()
                    self._log(f"Next button clicked (step {step + 1})", "SUCCESS")
                    time.sleep(3)
                else:
                    break
            
            # Add caption
            if caption.strip():
                self._log("Adding caption...")
                
                caption_input = self._find_element_by_selectors(self.selectors['caption_textarea'])
                
                if caption_input:
                    caption_input.click()
                    time.sleep(1)
                    caption_input.send_keys(caption)
                    self._log("Caption added", "SUCCESS")
                else:
                    self._log("Caption input not found", "WARNING")
            
            # Click Share button
            self._log("Looking for Share button...")
            share_button = self._find_element_by_text("Share", "button", timeout=15)
            
            if not share_button:
                # Try alternative selectors
                share_button = self._find_element_by_selectors(self.selectors['share_button'])
            
            if not share_button:
                raise NoSuchElementException("Share button not found")
            
            # Click share button
            self.driver.execute_script("arguments[0].click();", share_button)
            self._log("Share button clicked", "SUCCESS")
            time.sleep(10)
            
            # Check for success
            self._log("Instagram post uploaded successfully!", "SUCCESS")
            
            return {
                "success": True,
                "message": "Post uploaded successfully",
                "media_path": media_path,
                "caption": caption,
                "is_reel": is_reel
            }
            
        except Exception as e:
            error_msg = f"Instagram upload failed: {str(e)}"
            self._log(error_msg, "ERROR")
            
            # Take screenshot for debugging
            self.take_screenshot(f"instagram_error_{int(time.time())}.png")
            
            return {
                "success": False,
                "message": error_msg,
                "media_path": media_path,
                "caption": caption,
                "is_reel": is_reel
            }
        
        finally:
            if self.driver:
                self._log("Closing browser...")
                self.driver.quit()

    def upload_reel(self, video_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Upload reel to Instagram (wrapper for upload_post with is_reel=True)
        
        Args:
            video_path: Path to video file
            caption: Caption for the reel
            
        Returns:
            Dict with upload status
        """
        return self.upload_post(video_path, caption, is_reel=True)

    def upload_photo(self, image_path: str, caption: str = "") -> Dict[str, Any]:
        """
        Upload photo to Instagram (wrapper for upload_post with is_reel=False)
        
        Args:
            image_path: Path to image file
            caption: Caption for the post
            
        Returns:
            Dict with upload status
        """
        return self.upload_post(image_path, caption, is_reel=False)

    def take_screenshot(self, filename: str = None):
        """Take screenshot for debugging"""
        if not filename:
            filename = f"instagram_screenshot_{int(time.time())}.png"
        
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
        """Check Instagram cookies status"""
        if not self.cookies_path.exists():
            self._log("Instagram cookies file not found", "WARNING")
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
            
            self._log(f"Total Instagram cookies: {len(cookies)}", "INFO")
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
            self._log(f"Error reading Instagram cookies: {str(e)}", "ERROR")
            return {"exists": True, "error": str(e)}


def main():
    """Main function for CLI"""
    parser = argparse.ArgumentParser(description="Instagram Uploader")
    parser.add_argument("--media", "-m", help="Path to media file (image/video)")
    parser.add_argument("--caption", "-c", default="", help="Caption for post")
    parser.add_argument("--reel", action="store_true", help="Upload as Reel")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--clear-cookies", action="store_true", help="Clear cookies")
    parser.add_argument("--check-cookies", action="store_true", help="Check cookies status")
    
    args = parser.parse_args()
    
    uploader = InstagramUploader(headless=args.headless, debug=args.debug)
    
    # Handle different actions
    if args.clear_cookies:
        uploader.clear_cookies()
        return
    
    if args.check_cookies:
        uploader.check_cookies_status()
        return
    
    if args.media:
        if not os.path.exists(args.media):
            print(f"{Fore.RED}❌ Media file not found: {args.media}")
            sys.exit(1)
        
        if args.reel:
            result = uploader.upload_reel(args.media, args.caption)
        else:
            result = uploader.upload_post(args.media, args.caption)
        
        if result["success"]:
            print(f"{Fore.GREEN}🎉 Instagram upload successful!")
        else:
            print(f"{Fore.RED}❌ Instagram upload failed: {result['message']}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print(f"{Fore.MAGENTA}📸 Instagram Uploader")
        print("=" * 40)
        
        while True:
            print(f"\n{Fore.YELLOW}Choose action:")
            print("1. 📸 Upload Photo")
            print("2. 🎬 Upload Reel")
            print("3. 📱 Upload Post (Auto-detect)")
            print("4. 🍪 Check cookies status")
            print("5. 🗑️ Clear cookies")
            print("6. ❌ Exit")
            
            choice = input(f"\n{Fore.WHITE}Choice (1-6): ").strip()
            
            if choice == "1":
                media_path = input(f"{Fore.CYAN}Image file path: ").strip()
                if not os.path.exists(media_path):
                    print(f"{Fore.RED}❌ Image file not found!")
                    continue
                
                caption = input(f"{Fore.CYAN}Caption (optional): ").strip()
                
                result = uploader.upload_photo(media_path, caption)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Instagram photo uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Instagram photo upload failed: {result['message']}")
            
            elif choice == "2":
                video_path = input(f"{Fore.CYAN}Video file path: ").strip()
                if not os.path.exists(video_path):
                    print(f"{Fore.RED}❌ Video file not found!")
                    continue
                
                caption = input(f"{Fore.CYAN}Caption (optional): ").strip()
                
                result = uploader.upload_reel(video_path, caption)
                
                if result["success"]:
                    print(f"{Fore.GREEN}🎉 Instagram Reel uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Instagram Reel upload failed: {result['message']}")
            
            elif choice == "3":
                media_path = input(f"{Fore.CYAN}Media file path: ").strip()
                if not os.path.exists(media_path):
                    print(f"{Fore.RED}❌ Media file not found!")
                    continue
                
                caption = input(f"{Fore.CYAN}Caption (optional): ").strip()
                
                # Auto-detect if it's a video (for Reel) or image (for Post)
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
                is_reel = any(media_path.lower().endswith(ext) for ext in video_extensions)
                
                result = uploader.upload_post(media_path, caption, is_reel)
                
                if result["success"]:
                    content_type = "Reel" if is_reel else "Post"
                    print(f"{Fore.GREEN}🎉 Instagram {content_type} uploaded successfully!")
                else:
                    print(f"{Fore.RED}❌ Instagram upload failed: {result['message']}")
            
            elif choice == "4":
                uploader.check_cookies_status()
            
            elif choice == "5":
                confirm = input(f"{Fore.YELLOW}Clear Instagram cookies? (y/N): ").strip().lower()
                if confirm == 'y':
                    uploader.clear_cookies()
            
            elif choice == "6":
                print(f"{Fore.YELLOW}👋 Goodbye!")
                break
            
            else:
                print(f"{Fore.RED}❌ Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Program stopped by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Fatal error: {str(e)}")
        sys.exit(1)