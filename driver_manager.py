#!/usr/bin/env python3
"""
Universal Driver Manager untuk Social Media Uploader
Mengatasi masalah ChromeDriver di semua platform dengan deteksi otomatis
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
        """Get Chrome browser version"""
        if self._chrome_version:
            return self._chrome_version
        
        try:
            if self.system == "windows":
                # Windows Chrome version detection
                import winreg
                
                # Try different registry paths
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
                            self._log(f"Chrome version detected: {version}", "SUCCESS")
                            return version
                    except:
                        continue
                
                # Fallback: Try command line
                result = subprocess.run([
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--version"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1]
                    self._chrome_version = version
                    return version
                    
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
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            version = result.stdout.strip().split()[-1]
                            self._chrome_version = version
                            self._log(f"Chrome version detected: {version}", "SUCCESS")
                            return version
                    except:
                        continue
                        
            elif self.system == "darwin":  # macOS
                # macOS Chrome version detection
                try:
                    result = subprocess.run([
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        version = result.stdout.strip().split()[-1]
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
        """Find existing ChromeDriver in various locations"""
        self._log("Searching for existing ChromeDriver...", "INFO")
        
        # Method 1: Check PATH
        chromedriver_path = shutil.which('chromedriver')
        if chromedriver_path and os.path.exists(chromedriver_path):
            if self._test_chromedriver(chromedriver_path):
                self._log(f"ChromeDriver found in PATH: {chromedriver_path}", "SUCCESS")
                return chromedriver_path
        
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
        
        # Method 3: Try WebDriver Manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Suppress WebDriver Manager logs
            os.environ['WDM_LOG_LEVEL'] = '0'
            os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
            
            chromedriver_path = ChromeDriverManager().install()
            if chromedriver_path and os.path.exists(chromedriver_path):
                if self._test_chromedriver(chromedriver_path):
                    self._log(f"ChromeDriver via WebDriver Manager: {chromedriver_path}", "SUCCESS")
                    return chromedriver_path
        except Exception as e:
            self._log(f"WebDriver Manager failed: {e}", "WARNING")
        
        return None

    def _test_chromedriver(self, path: str) -> bool:
        """Test if ChromeDriver is working"""
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def download_chromedriver(self, version: str = None) -> Optional[str]:
        """Download ChromeDriver for the detected Chrome version"""
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
        """Get compatible ChromeDriver version"""
        try:
            # For Chrome 115+, use new API
            if int(chrome_major_version) >= 115:
                url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{chrome_major_version}"
            else:
                url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_major_version}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                version = response.text.strip()
                self._log(f"ChromeDriver version: {version}", "INFO")
                return version
            else:
                # Fallback to latest
                if int(chrome_major_version) >= 115:
                    url = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
                else:
                    url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text.strip()
                    
        except Exception as e:
            self._log(f"Error getting ChromeDriver version: {e}", "WARNING")
        
        return None

    def _get_download_url(self, chromedriver_version: str) -> Optional[str]:
        """Get download URL for ChromeDriver"""
        try:
            # Determine platform suffix
            if self.system == "windows":
                if "64" in self.architecture:
                    platform_suffix = "win64"
                else:
                    platform_suffix = "win32"
                filename = "chromedriver.exe"
            elif self.system == "linux":
                if "64" in self.architecture:
                    platform_suffix = "linux64"
                else:
                    platform_suffix = "linux32"
                filename = "chromedriver"
            elif self.system == "darwin":  # macOS
                if "arm" in self.architecture or "aarch64" in self.architecture:
                    platform_suffix = "mac-arm64"
                else:
                    platform_suffix = "mac-x64"
                filename = "chromedriver"
            else:
                self._log(f"Unsupported platform: {self.system}", "ERROR")
                return None
            
            # Check if new API (Chrome 115+)
            major_version = int(chromedriver_version.split('.')[0])
            if major_version >= 115:
                # New Chrome for Testing API
                url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chromedriver_version}/{platform_suffix}/chromedriver-{platform_suffix}.zip"
            else:
                # Old ChromeDriver API
                url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_{platform_suffix}.zip"
            
            return url
            
        except Exception as e:
            self._log(f"Error building download URL: {e}", "ERROR")
            return None

    def _download_and_extract(self, url: str, version: str) -> Optional[str]:
        """Download and extract ChromeDriver"""
        try:
            # Download
            self._log("Downloading ChromeDriver...", "INFO")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Save zip file
            zip_path = self.drivers_dir / f"chromedriver_{version}.zip"
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
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
            for root, dirs, files in os.walk(self.drivers_dir):
                for file in files:
                    if file == chromedriver_name:
                        chromedriver_path = os.path.join(root, file)
                        
                        # Make executable on Unix systems
                        if self.system != "windows":
                            os.chmod(chromedriver_path, 0o755)
                        
                        # Test the driver
                        if self._test_chromedriver(chromedriver_path):
                            # Move to drivers directory root
                            final_path = self.drivers_dir / chromedriver_name
                            if chromedriver_path != str(final_path):
                                shutil.move(chromedriver_path, final_path)
                            
                            # Cleanup
                            zip_path.unlink()
                            
                            self._log(f"ChromeDriver ready: {final_path}", "SUCCESS")
                            return str(final_path)
            
            self._log("ChromeDriver not found in extracted files", "ERROR")
            return None
            
        except Exception as e:
            self._log(f"Error downloading/extracting ChromeDriver: {e}", "ERROR")
            return None

    def get_chromedriver_path(self, auto_download: bool = True) -> Optional[str]:
        """Get ChromeDriver path with auto-download fallback"""
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
        """Show troubleshooting tips"""
        self._log("ChromeDriver setup failed. Troubleshooting tips:", "ERROR")
        self._log("1. Install Google Chrome browser", "INFO")
        self._log("2. Download ChromeDriver from https://chromedriver.chromium.org/", "INFO")
        self._log("3. Place chromedriver in your PATH or project folder", "INFO")
        self._log("4. Install webdriver-manager: pip install webdriver-manager", "INFO")
        self._log("5. Check Chrome and ChromeDriver version compatibility", "INFO")

    def setup_selenium_service(self, headless: bool = False, additional_options: list = None):
        """Setup Selenium service with ChromeDriver"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Get ChromeDriver path
        chromedriver_path = self.get_chromedriver_path()
        if not chromedriver_path:
            raise Exception("ChromeDriver not available")
        
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
            '--disable-logging'
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
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-detection script
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self._log("Selenium WebDriver ready", "SUCCESS")
        return driver

    def check_system_requirements(self) -> Dict[str, Any]:
        """Check system requirements"""
        requirements = {
            "chrome_installed": False,
            "chrome_version": None,
            "chromedriver_available": False,
            "chromedriver_path": None,
            "webdriver_manager_available": False,
            "system_info": {
                "os": self.system,
                "architecture": self.architecture
            }
        }
        
        # Check Chrome
        chrome_version = self.get_chrome_version()
        if chrome_version:
            requirements["chrome_installed"] = True
            requirements["chrome_version"] = chrome_version
        
        # Check ChromeDriver
        chromedriver_path = self.find_existing_chromedriver()
        if chromedriver_path:
            requirements["chromedriver_available"] = True
            requirements["chromedriver_path"] = chromedriver_path
        
        # Check WebDriver Manager
        try:
            import webdriver_manager
            requirements["webdriver_manager_available"] = True
        except ImportError:
            pass
        
        return requirements

    def install_requirements(self):
        """Install missing requirements"""
        self._log("Installing missing requirements...", "INFO")
        
        # Install WebDriver Manager
        try:
            import webdriver_manager
            self._log("WebDriver Manager already installed", "SUCCESS")
        except ImportError:
            self._log("Installing WebDriver Manager...", "INFO")
            subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        
        # Install requests if not available
        try:
            import requests
        except ImportError:
            self._log("Installing requests...", "INFO")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"])

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
    parser.add_argument("--install", action="store_true", help="Install requirements")
    parser.add_argument("--test", action="store_true", help="Test driver setup")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    manager = UniversalDriverManager(debug=args.debug)
    
    if args.diagnostics:
        manager.run_diagnostics()
    elif args.install:
        manager.install_requirements()
    elif args.test:
        try:
            driver = manager.setup_selenium_service(headless=True)
            print(f"{Fore.GREEN}✅ Driver test successful!")
            driver.quit()
        except Exception as e:
            print(f"{Fore.RED}❌ Driver test failed: {e}")
    else:
        manager.run_diagnostics()