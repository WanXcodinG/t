#!/usr/bin/env python3
"""
Universal Driver Manager untuk Social Media Uploader
Mengatasi masalah ChromeDriver di semua platform dengan deteksi otomatis
Support untuk Windows, Linux/Ubuntu VPS, dan macOS
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
        
        # Initialize platform-specific attributes
        self.is_vps = False
        self.is_ubuntu = False
        self.is_headless = False
        self.distro = "unknown"
        
        # Detect environment
        self._detect_environment()
        
        # Chrome version cache
        self._chrome_version = None

    def _detect_environment(self):
        """Detect environment (VPS, Ubuntu, headless)"""
        try:
            # Fix for Windows architecture detection
            if self.system == "windows":
                if "64" in platform.architecture()[0] or "AMD64" in os.environ.get("PROCESSOR_ARCHITECTURE", ""):
                    self.architecture = "x64"
                else:
                    self.architecture = "x86"
            
            # Ubuntu/Linux specific detection
            elif self.system == "linux":
                self.distro = self._detect_linux_distro()
                self.is_ubuntu = "ubuntu" in self.distro.lower()
                self.is_headless = self._detect_headless_environment()
                self.is_vps = self._detect_vps_environment()
        except Exception as e:
            if self.debug:
                self._log(f"Environment detection error: {e}", "DEBUG")

    def _detect_vps_environment(self) -> bool:
        """Detect if running on VPS"""
        try:
            # Check for common VPS indicators
            vps_indicators = [
                "/proc/vz",  # OpenVZ
                "/proc/xen",  # Xen
                "/sys/hypervisor",  # General hypervisor
            ]
            
            for indicator in vps_indicators:
                if os.path.exists(indicator):
                    return True
            
            # Check for cloud providers
            try:
                with open("/sys/class/dmi/id/product_name", "r") as f:
                    product = f.read().strip().lower()
                    if any(cloud in product for cloud in ["kvm", "qemu", "vmware", "virtualbox", "xen"]):
                        return True
            except:
                pass
            
            # Check environment variables
            if any(var in os.environ for var in ["AWS_REGION", "GOOGLE_CLOUD_PROJECT", "AZURE_SUBSCRIPTION_ID"]):
                return True
            
            return False
            
        except Exception:
            return False

    def _detect_linux_distro(self) -> str:
        """Detect Linux distribution"""
        try:
            # Try /etc/os-release first
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
            
            # Try lsb_release
            try:
                result = subprocess.run(["lsb_release", "-i"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.split(":")[1].strip()
            except:
                pass
            
            # Fallback checks
            if os.path.exists("/etc/ubuntu-release"):
                return "ubuntu"
            elif os.path.exists("/etc/debian_version"):
                return "debian"
            elif os.path.exists("/etc/redhat-release"):
                return "redhat"
            elif os.path.exists("/etc/centos-release"):
                return "centos"
            
            return "linux"
            
        except Exception:
            return "linux"

    def _detect_headless_environment(self) -> bool:
        """Detect if running in headless environment (no GUI)"""
        try:
            # Check DISPLAY variable
            if not os.environ.get("DISPLAY"):
                return True
            
            # Check if X11 is available
            try:
                subprocess.run(["xset", "q"], capture_output=True, timeout=5)
                return False  # X11 available
            except:
                return True  # No X11
                
        except Exception:
            return True

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
                            result = subprocess.run([
                                chrome_path, "--version"
                            ], capture_output=True, text=True, timeout=10)
                            
                            if result.returncode == 0:
                                version_line = result.stdout.strip()
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
                # Enhanced Linux Chrome version detection
                commands = [
                    ["google-chrome", "--version"],
                    ["google-chrome-stable", "--version"],
                    ["/usr/bin/google-chrome", "--version"],
                    ["/usr/bin/google-chrome-stable", "--version"],
                    ["/opt/google/chrome/chrome", "--version"],
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
                "/snap/bin/chromium.chromedriver",  # Snap package
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
            
            # Make executable on Unix systems
            if self.system != "windows":
                os.chmod(path, 0o755)
            
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
            # For now, just return None to avoid complex download logic
            self._log("Auto-download not implemented in this version", "WARNING")
        
        return None

    def setup_selenium_service(self, headless: bool = None, additional_options: list = None):
        """Setup Selenium service dengan comprehensive error handling"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Auto-detect headless mode for VPS
        if headless is None:
            headless = self.is_vps or self.is_headless
        
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
            self._log("Running in headless mode", "INFO")
        
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
        
        if self.system == "linux":
            print(f"Distribution: {self.distro}")
            print(f"Is Ubuntu: {self.is_ubuntu}")
            print(f"Is VPS: {self.is_vps}")
            print(f"Is Headless: {self.is_headless}")
            print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
        
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


# Global instance
driver_manager = UniversalDriverManager()

def get_chrome_driver(headless: bool = None, additional_options: list = None):
    """Get configured Chrome WebDriver dengan auto-headless untuk VPS"""
    return driver_manager.setup_selenium_service(headless, additional_options)

def check_driver_status():
    """Check driver status"""
    return driver_manager.get_chromedriver_path() is not None

def run_driver_diagnostics():
    """Run driver diagnostics"""
    driver_manager.run_diagnostics()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Driver Manager")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    manager = UniversalDriverManager(debug=args.debug)
    
    if args.diagnostics:
        manager.run_diagnostics()
    else:
        manager.run_diagnostics()