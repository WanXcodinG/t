#!/usr/bin/env python3
"""
Universal Driver Manager untuk Social Media Uploader
Mengatasi masalah ChromeDriver di semua platform dengan deteksi otomatis
Fixed untuk error [WinError 193] %1 is not a valid Win32 application
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional, Dict, Any
import zipfile
import requests
import json
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class UniversalDriverManager:
    def __init__(self, debug: bool = False):
        """
        Initialize Universal Driver Manager
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.base_dir = Path(__file__).parent
        self.drivers_dir = self.base_dir / "drivers"
        self.drivers_dir.mkdir(exist_ok=True)
        
        # Platform detection
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        
        # Chrome version cache
        self._chrome_version = None
        
        # Fix for Windows architecture detection
        if self.system == "windows":
            # More accurate Windows architecture detection
            if "64" in platform.architecture()[0] or "AMD64" in os.environ.get("PROCESSOR_ARCHITECTURE", ""):
                self.architecture = "x64"
            else:
                self.architecture = "x86"

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

    def get_chrome_version(self) -> Optional[str]:
        """Get Chrome browser version dengan improved detection"""
        if self._chrome_version:
            return self._chrome_version
        
        try:
            if self.system == "windows":
                # Method 1: Registry detection
                try:
                    import winreg
                    
                    paths = [
                        r"SOFTWARE\Google\Chrome\BLBeacon",
                        r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon",
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                    ]
                    
                    for path in paths:
                        try:
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                                version = winreg.QueryValueEx(key, "version")[0]
                                self._chrome_version = version
                                self._log(f"Chrome version detected via registry: {version}", "SUCCESS")
                                return version
                        except:
                            continue
                except ImportError:
                    pass
                
                # Method 2: File version detection
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        try:
                            # Try to get version from file properties
                            result = subprocess.run([
                                chrome_path, "--version"
                            ], capture_output=True, text=True, timeout=10)
                            
                            if result.returncode == 0:
                                version_line = result.stdout.strip()
                                # Extract version number
                                import re
                                version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_line)
                                if version_match:
                                    version = version_match.group(1)
                                    self._chrome_version = version
                                    self._log(f"Chrome version detected via executable: {version}", "SUCCESS")
                                    return version
                        except:
                            continue
                            
            elif self.system == "linux":
                # Linux Chrome version detection
                commands = [
                    ["google-chrome", "--version"],
                    ["google-chrome-stable", "--version"],
                    ["chromium-browser", "--version"],
                    ["chromium", "--version"]
                ]
                
                for cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            import re
                            version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                            if version_match:
                                version = version_match.group(1)
                                self._chrome_version = version
                                self._log(f"Chrome version detected: {version}", "SUCCESS")
                                return version
                    except:
                        continue
                        
            elif self.system == "darwin":  # macOS
                try:
                    result = subprocess.run([
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        import re
                        version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            version = version_match.group(1)
                            self._chrome_version = version
                            self._log(f"Chrome version detected: {version}", "SUCCESS")
                            return version
                except:
                    pass
            
            self._log("Could not detect Chrome version", "WARNING")
            return None
            
        except Exception as e:
            self._log(f"Error detecting Chrome version: {e}", "ERROR")
            return None

    def find_existing_chromedriver(self) -> Optional[str]:
        """Find existing ChromeDriver dengan improved validation"""
        self._log("Searching for existing ChromeDriver...", "INFO")
        
        # Method 1: Check PATH
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path and os.path.exists(chromedriver_path):
            if self._test_chromedriver(chromedriver_path):
                self._log(f"ChromeDriver found in PATH: {chromedriver_path}", "SUCCESS")
                return chromedriver_path
            else:
                self._log(f"ChromeDriver in PATH is not working: {chromedriver_path}", "WARNING")
        
        # Method 2: Check common locations
        common_paths = []
        
        if self.system == "windows":
            common_paths = [
                r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
                r"C:\chromedriver\chromedriver.exe",
                r"C:\Windows\System32\chromedriver.exe",
                str(self.base_dir / "chromedriver.exe"),
                str(self.drivers_dir / "chromedriver.exe")
            ]
        elif self.system == "linux":
            common_paths = [
                "/usr/local/bin/chromedriver",
                "/usr/bin/chromedriver",
                "/opt/chromedriver/chromedriver",
                str(self.base_dir / "chromedriver"),
                str(self.drivers_dir / "chromedriver")
            ]
        elif self.system == "darwin":  # macOS
            common_paths = [
                "/usr/local/bin/chromedriver",
                "/opt/homebrew/bin/chromedriver",
                str(self.base_dir / "chromedriver"),
                str(self.drivers_dir / "chromedriver")
            ]
        
        for path in common_paths:
            if os.path.exists(path):
                if self._test_chromedriver(path):
                    self._log(f"ChromeDriver found at: {path}", "SUCCESS")
                    return path
                else:
                    self._log(f"ChromeDriver found but not working: {path}", "WARNING")
        
        # Method 3: Try WebDriver Manager with error handling
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Suppress WebDriver Manager logs
            os.environ['WDM_LOG_LEVEL'] = '0'
            os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
            
            self._log("Trying WebDriver Manager...", "INFO")
            chromedriver_path = ChromeDriverManager().install()
            
            if chromedriver_path and os.path.exists(chromedriver_path):
                # Fix for WebDriver Manager path issues
                if self.system == "windows" and not chromedriver_path.endswith('.exe'):
                    # Look for the actual executable
                    driver_dir = Path(chromedriver_path).parent
                    for file in driver_dir.rglob("chromedriver.exe"):
                        chromedriver_path = str(file)
                        break
                
                if self._test_chromedriver(chromedriver_path):
                    self._log(f"ChromeDriver via WebDriver Manager: {chromedriver_path}", "SUCCESS")
                    return chromedriver_path
                else:
                    self._log(f"WebDriver Manager ChromeDriver not working: {chromedriver_path}", "WARNING")
                    
        except Exception as e:
            self._log(f"WebDriver Manager failed: {e}", "WARNING")
        
        return None

    def _test_chromedriver(self, path: str) -> bool:
        """Test if ChromeDriver is working dengan improved validation"""
        try:
            # Check if file exists and is executable
            if not os.path.exists(path):
                return False
            
            # Check file size (should be > 1MB for valid ChromeDriver)
            file_size = os.path.getsize(path)
            if file_size < 1024 * 1024:  # Less than 1MB
                self._log(f"ChromeDriver file too small: {file_size} bytes", "WARNING")
                return False
            
            # Test execution
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "ChromeDriver" in result.stdout:
                return True
            else:
                self._log(f"ChromeDriver test failed: {result.stderr}", "WARNING")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("ChromeDriver test timeout", "WARNING")
            return False
        except Exception as e:
            self._log(f"ChromeDriver test error: {e}", "WARNING")
            return False

    def download_chromedriver(self, version: str = None) -> Optional[str]:
        """Download ChromeDriver dengan improved error handling"""
        if not version:
            version = self.get_chrome_version()
            if not version:
                self._log("Cannot download ChromeDriver without Chrome version", "ERROR")
                return None
        
        # Extract major version
        major_version = version.split('.')[0]
        
        self._log(f"Downloading ChromeDriver for Chrome {version}...", "INFO")
        
        try:
            # Get ChromeDriver version
            chromedriver_version = self._get_chromedriver_version(major_version)
            if not chromedriver_version:
                self._log("Could not determine ChromeDriver version", "ERROR")
                return None
            
            # Determine download URL
            download_url = self._get_download_url(chromedriver_version)
            if not download_url:
                self._log("Could not determine download URL", "ERROR")
                return None
            
            # Download and extract
            return self._download_and_extract(download_url, chromedriver_version)
            
        except Exception as e:
            self._log(f"Error downloading ChromeDriver: {e}", "ERROR")
            return None

    def _get_chromedriver_version(self, chrome_major_version: str) -> Optional[str]:
        """Get compatible ChromeDriver version dengan fallback"""
        try:
            # For Chrome 115+, use new API
            if int(chrome_major_version) >= 115:
                url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_major_version}"
                fallback_url = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
            else:
                url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_version}"
                fallback_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
            
            # Try specific version first
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    version = response.text.strip()
                    self._log(f"ChromeDriver version: {version}", "INFO")
                    return version
            except:
                pass
            
            # Try fallback
            try:
                response = requests.get(fallback_url, timeout=10)
                if response.status_code == 200:
                    version = response.text.strip()
                    self._log(f"ChromeDriver version (fallback): {version}", "INFO")
                    return version
            except:
                pass
                    
        except Exception as e:
            self._log(f"Error getting ChromeDriver version: {e}", "WARNING")
        
        # Last resort: use known stable version
        stable_versions = {
            "120": "120.0.6099.109",
            "119": "119.0.6045.105",
            "118": "118.0.5993.70"
        }
        
        if chrome_major_version in stable_versions:
            version = stable_versions[chrome_major_version]
            self._log(f"Using known stable version: {version}", "INFO")
            return version
        
        return None

    def _get_download_url(self, chromedriver_version: str) -> Optional[str]:
        """Get download URL dengan improved platform detection"""
        try:
            # Determine platform suffix
            if self.system == "windows":
                if self.architecture == "x64" or "64" in self.architecture:
                    platform_suffix = "win64"
                else:
                    platform_suffix = "win32"
            elif self.system == "linux":
                if "64" in self.architecture:
                    platform_suffix = "linux64"
                else:
                    platform_suffix = "linux32"
            elif self.system == "darwin":  # macOS
                if "arm" in self.architecture or "aarch64" in self.architecture:
                    platform_suffix = "mac-arm64"
                else:
                    platform_suffix = "mac-x64"
            else:
                self._log(f"Unsupported platform: {self.system}", "ERROR")
                return None
            
            # Check if new API (Chrome 115+)
            major_version = int(chromedriver_version.split('.')[0])
            
            if major_version >= 115:
                # New Chrome for Testing API
                urls = [
                    f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromedriver_version}/{platform_suffix}/chromedriver-{platform_suffix}.zip",
                    f"https://storage.googleapis.com/chrome-for-testing-public/{chromedriver_version}/{platform_suffix}/chromedriver-{platform_suffix}.zip"
                ]
            else:
                # Old ChromeDriver API
                urls = [
                    f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_suffix}.zip"
                ]
            
            # Test URLs
            for url in urls:
                try:
                    response = requests.head(url, timeout=10)
                    if response.status_code == 200:
                        self._log(f"Download URL found: {url}", "INFO")
                        return url
                except:
                    continue
            
            self._log("No working download URL found", "ERROR")
            return None
            
        except Exception as e:
            self._log(f"Error building download URL: {e}", "ERROR")
            return None

    def _download_and_extract(self, url: str, version: str) -> Optional[str]:
        """Download and extract ChromeDriver dengan improved error handling"""
        try:
            # Download
            self._log("Downloading ChromeDriver...", "INFO")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            
            # Save zip file
            zip_path = self.drivers_dir / f"chromedriver_{version}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            self._log(f"Downloaded {len(response.content)} bytes", "INFO")
            
            # Extract
            self._log("Extracting ChromeDriver...", "INFO")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.drivers_dir)
            
            # Find extracted chromedriver
            if self.system == "windows":
                chromedriver_name = "chromedriver.exe"
            else:
                chromedriver_name = "chromedriver"
            
            # Look for chromedriver in extracted folders
            found_chromedriver = None
            for root, dirs, files in os.walk(self.drivers_dir):
                for file in files:
                    if file == chromedriver_name:
                        candidate_path = os.path.join(root, file)
                        
                        # Check if it's a valid ChromeDriver
                        if self._test_chromedriver(candidate_path):
                            found_chromedriver = candidate_path
                            break
                
                if found_chromedriver:
                    break
            
            if found_chromedriver:
                # Move to drivers directory root
                final_path = self.drivers_dir / chromedriver_name
                if found_chromedriver != str(final_path):
                    shutil.move(found_chromedriver, final_path)
                
                # Make executable on Unix systems
                if self.system != "windows":
                    os.chmod(final_path, 0o755)
                
                # Cleanup
                try:
                    zip_path.unlink()
                    # Clean up extracted folders
                    for item in self.drivers_dir.iterdir():
                        if item.is_dir() and item.name != "chromedriver":
                            shutil.rmtree(item, ignore_errors=True)
                except:
                    pass
                
                # Final test
                if self._test_chromedriver(str(final_path)):
                    self._log(f"ChromeDriver ready: {final_path}", "SUCCESS")
                    return str(final_path)
                else:
                    self._log("Downloaded ChromeDriver failed validation", "ERROR")
                    return None
            else:
                self._log("ChromeDriver not found in extracted files", "ERROR")
                return None
            
        except Exception as e:
            self._log(f"Error downloading/extracting ChromeDriver: {e}", "ERROR")
            return None

    def get_chromedriver_path(self, auto_download: bool = True) -> Optional[str]:
        """Get ChromeDriver path dengan comprehensive fallback"""
        self._log("Initializing ChromeDriver...", "INFO")
        
        # Step 1: Try to find existing ChromeDriver
        existing_path = self.find_existing_chromedriver()
        if existing_path:
            return existing_path
        
        # Step 2: Auto-download if enabled
        if auto_download:
            self._log("ChromeDriver not found, attempting auto-download...", "WARNING")
            downloaded_path = self.download_chromedriver()
            if downloaded_path:
                return downloaded_path
        
        # Step 3: Show troubleshooting tips
        self._show_troubleshooting_tips()
        return None

    def _show_troubleshooting_tips(self):
        """Show comprehensive troubleshooting tips"""
        self._log("ChromeDriver setup failed. Troubleshooting tips:", "ERROR")
        self._log("1. Install Google Chrome browser", "INFO")
        self._log("2. Download ChromeDriver from https://chromedriver.chromium.org/", "INFO")
        self._log("3. Place chromedriver.exe in your PATH or project folder", "INFO")
        self._log("4. Install webdriver-manager: pip install webdriver-manager", "INFO")
        self._log("5. Check Chrome and ChromeDriver version compatibility", "INFO")
        self._log("6. Run: python driver_manager.py --diagnostics", "INFO")
        self._log("7. Try: python fix_all_drivers.py", "INFO")

    def setup_selenium_service(self, headless: bool = False, additional_options: list = None):
        """Setup Selenium service dengan comprehensive error handling"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Get ChromeDriver path
        chromedriver_path = self.get_chromedriver_path()
        if not chromedriver_path:
            raise Exception("ChromeDriver not available. Please run: python fix_all_drivers.py")
        
        # Setup Chrome options
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1280,800")
        
        if headless:
            chrome_options.add_argument('--headless=new')
        
        # Additional options
        default_options = [
            '--disable-extensions',
            '--disable-gpu',
            '--disable-notifications',
            '--disable-popup-blocking',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--log-level=3',
            '--silent',
            '--disable-logging',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ]
        
        for option in default_options:
            chrome_options.add_argument(option)
        
        if additional_options:
            for option in additional_options:
                chrome_options.add_argument(option)
        
        # Anti-detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Setup service
        service = Service(
            chromedriver_path,
            log_path=os.devnull,
            service_args=['--silent']
        )
        
        try:
            # Create driver
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Anti-detection script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self._log("Selenium WebDriver ready", "SUCCESS")
            return driver
            
        except Exception as e:
            self._log(f"Failed to create WebDriver: {e}", "ERROR")
            raise

    def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        print(f"\n{Fore.LIGHTBLUE_EX}🔍 DRIVER DIAGNOSTICS")
        print("=" * 50)
        
        # System info
        print(f"\n{Fore.YELLOW}System Information:")
        print(f"OS: {self.system}")
        print(f"Architecture: {self.architecture}")
        
        # Chrome check
        print(f"\n{Fore.YELLOW}Chrome Browser:")
        chrome_version = self.get_chrome_version()
        if chrome_version:
            print(f"✅ Chrome installed: {chrome_version}")
        else:
            print(f"❌ Chrome not found")
            print(f"   Download from: https://www.google.com/chrome/")
        
        # ChromeDriver check
        print(f"\n{Fore.YELLOW}ChromeDriver:")
        chromedriver_path = self.find_existing_chromedriver()
        if chromedriver_path:
            print(f"✅ ChromeDriver found: {chromedriver_path}")
            
            # Test ChromeDriver
            if self._test_chromedriver(chromedriver_path):
                print(f"✅ ChromeDriver working")
            else:
                print(f"❌ ChromeDriver not working")
        else:
            print(f"❌ ChromeDriver not found")
            
            # Try auto-download
            print(f"\n{Fore.CYAN}Attempting auto-download...")
            downloaded_path = self.download_chromedriver()
            if downloaded_path:
                print(f"✅ ChromeDriver downloaded: {downloaded_path}")
            else:
                print(f"❌ Auto-download failed")
        
        # Dependencies check
        print(f"\n{Fore.YELLOW}Dependencies:")
        
        try:
            import selenium
            print(f"✅ Selenium: {selenium.__version__}")
        except ImportError:
            print(f"❌ Selenium not installed")
        
        try:
            import webdriver_manager
            print(f"✅ WebDriver Manager available")
        except ImportError:
            print(f"❌ WebDriver Manager not installed")
        
        try:
            import requests
            print(f"✅ Requests available")
        except ImportError:
            print(f"❌ Requests not installed")
        
        # Test driver creation
        print(f"\n{Fore.YELLOW}Driver Test:")
        try:
            driver = self.setup_selenium_service(headless=True)
            print(f"✅ Driver creation successful")
            driver.quit()
        except Exception as e:
            print(f"❌ Driver creation failed: {e}")


# Global instance
driver_manager = UniversalDriverManager()

def get_chrome_driver(headless: bool = False, additional_options: list = None):
    """Get configured Chrome WebDriver"""
    return driver_manager.setup_selenium_service(headless, additional_options)

def check_driver_status():
    """Check driver status"""
    return driver_manager.check_system_requirements()

def run_driver_diagnostics():
    """Run driver diagnostics"""
    driver_manager.run_diagnostics()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Driver Manager")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics")
    parser.add_argument("--test", action="store_true", help="Test driver setup")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    manager = UniversalDriverManager(debug=args.debug)
    
    if args.diagnostics:
        manager.run_diagnostics()
    elif args.test:
        try:
            driver = manager.setup_selenium_service(headless=True)
            print(f"{Fore.GREEN}✅ Driver test successful!")
            driver.get("https://www.google.com")
            print(f"{Fore.GREEN}✅ Navigation test successful!")
            driver.quit()
        except Exception as e:
            print(f"{Fore.RED}❌ Driver test failed: {e}")
    else:
        manager.run_diagnostics()