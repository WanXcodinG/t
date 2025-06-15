#!/usr/bin/env python3
"""
Universal Driver Manager untuk Social Media Uploader
Mengatasi masalah ChromeDriver di semua platform dengan deteksi otomatis
Support untuk Windows, Linux/Ubuntu VPS, dan macOS
Fixed untuk error [WinError 193] %1 is not a valid Win32 application
Enhanced Chrome detection untuk Windows
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
        self.is_vps = self._detect_vps_environment()
        
        # Ubuntu/Linux specific detection
        if self.system == "linux":
            self.distro = self._detect_linux_distro()
            self.is_ubuntu = "ubuntu" in self.distro.lower()
            self.is_headless = self._detect_headless_environment()
        else:
            self.distro = "unknown"
            self.is_ubuntu = False
            self.is_headless = False
        
        # Fix for Windows architecture detection
        if self.system == "windows":
            # More accurate Windows architecture detection
            if "64" in platform.architecture()[0] or "AMD64" in os.environ.get("PROCESSOR_ARCHITECTURE", ""):
                self.architecture = "x64"
            else:
                self.architecture = "x86"
        
        # Chrome version cache
        self._chrome_version = None

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

    def install_chrome_ubuntu(self) -> bool:
        """Install Chrome on Ubuntu VPS"""
        if not self.is_ubuntu:
            self._log("Not Ubuntu, skipping Chrome installation", "WARNING")
            return False
        
        self._log("Installing Chrome on Ubuntu...", "INFO")
        
        try:
            # Update package list
            self._log("Updating package list...", "INFO")
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            
            # Install dependencies
            self._log("Installing dependencies...", "INFO")
            dependencies = [
                "wget", "gnupg", "software-properties-common", 
                "apt-transport-https", "ca-certificates"
            ]
            subprocess.run(["sudo", "apt", "install", "-y"] + dependencies, 
                         check=True, capture_output=True)
            
            # Add Google Chrome repository
            self._log("Adding Google Chrome repository...", "INFO")
            
            # Download and add Google signing key
            subprocess.run([
                "wget", "-q", "-O", "-", 
                "https://dl.google.com/linux/linux_signing_key.pub"
            ], stdout=subprocess.PIPE, check=True)
            
            key_result = subprocess.run([
                "wget", "-q", "-O", "-", 
                "https://dl.google.com/linux/linux_signing_key.pub"
            ], capture_output=True, check=True)
            
            subprocess.run([
                "sudo", "apt-key", "add", "-"
            ], input=key_result.stdout, check=True)
            
            # Add repository
            subprocess.run([
                "sudo", "sh", "-c", 
                'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
            ], check=True)
            
            # Update package list again
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            
            # Install Chrome
            self._log("Installing Google Chrome...", "INFO")
            subprocess.run([
                "sudo", "apt", "install", "-y", "google-chrome-stable"
            ], check=True, capture_output=True)
            
            self._log("Chrome installed successfully!", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self._log(f"Failed to install Chrome: {e}", "ERROR")
            
            # Try alternative installation
            self._log("Trying alternative Chrome installation...", "WARNING")
            try:
                # Download Chrome deb package directly
                subprocess.run([
                    "wget", "-O", "/tmp/google-chrome-stable.deb",
                    "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"
                ], check=True, capture_output=True)
                
                # Install with dpkg
                subprocess.run([
                    "sudo", "dpkg", "-i", "/tmp/google-chrome-stable.deb"
                ], capture_output=True)
                
                # Fix dependencies
                subprocess.run([
                    "sudo", "apt", "install", "-f", "-y"
                ], check=True, capture_output=True)
                
                self._log("Chrome installed via alternative method!", "SUCCESS")
                return True
                
            except Exception as e2:
                self._log(f"Alternative installation also failed: {e2}", "ERROR")
                return False
        
        except Exception as e:
            self._log(f"Unexpected error installing Chrome: {e}", "ERROR")
            return False

    def install_chrome_dependencies_ubuntu(self) -> bool:
        """Install Chrome dependencies for headless operation on Ubuntu"""
        if not self.is_ubuntu:
            return True
        
        self._log("Installing Chrome dependencies for Ubuntu VPS...", "INFO")
        
        try:
            # Essential packages for headless Chrome
            packages = [
                "libnss3", "libgconf-2-4", "libxss1", "libappindicator1",
                "libindicator7", "gconf-service", "libgconf-2-4",
                "libxss1", "libappindicator1", "fonts-liberation",
                "libappindicator3-1", "libasound2", "libatk-bridge2.0-0",
                "libdrm2", "libxcomposite1", "libxdamage1", "libxrandr2",
                "libgbm1", "libxkbcommon0", "libgtk-3-0", "libxshmfence1"
            ]
            
            # Install packages
            subprocess.run([
                "sudo", "apt", "install", "-y"
            ] + packages, check=True, capture_output=True)
            
            self._log("Chrome dependencies installed successfully!", "SUCCESS")
            return True
            
        except subprocess.CalledProcessError as e:
            self._log(f"Failed to install Chrome dependencies: {e}", "ERROR")
            return False
        except Exception as e:
            self._log(f"Unexpected error installing dependencies: {e}", "ERROR")
            return False

    def get_chrome_version(self) -> Optional[str]:
        """Enhanced Chrome version detection untuk Windows"""
        if self._chrome_version:
            return self._chrome_version
        
        try:
            if self.system == "windows":
                # Method 1: Enhanced Registry detection
                try:
                    import winreg
                    
                    # Try multiple registry paths
                    registry_paths = [
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"),
                        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\BLBeacon"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Update\Clients\{8A69D345-D564-463c-AFF1-A69D9E530F96}"),
                        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Google\Update\Clients\{8A69D345-D564-463c-AFF1-A69D9E530F96}")
                    ]
                    
                    for hkey, path in registry_paths:
                        try:
                            with winreg.OpenKey(hkey, path) as key:
                                # Try different value names
                                value_names = ["version", "pv", "Version"]
                                for value_name in value_names:
                                    try:
                                        version = winreg.QueryValueEx(key, value_name)[0]
                                        if version and len(version.split('.')) >= 3:
                                            self._chrome_version = version
                                            self._log(f"Chrome version detected via registry: {version}", "SUCCESS")
                                            return version
                                    except FileNotFoundError:
                                        continue
                        except (FileNotFoundError, PermissionError):
                            continue
                except ImportError:
                    if self.debug:
                        self._log("winreg not available", "DEBUG")
                
                # Method 2: Enhanced File version detection
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                    os.path.expanduser(r"~\AppData\Roaming\Google\Chrome\Application\chrome.exe")
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        try:
                            # Try to get version via executable
                            result = subprocess.run([
                                chrome_path, "--version"
                            ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                            
                            if result.returncode == 0:
                                version_line = result.stdout.strip()
                                import re
                                version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', version_line)
                                if version_match:
                                    version = version_match.group(1)
                                    self._chrome_version = version
                                    self._log(f"Chrome version detected via executable: {version}", "SUCCESS")
                                    return version
                        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                            continue
                
                # Method 3: Try PowerShell for version detection
                try:
                    powershell_cmd = '''
                    $chrome = Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" -ErrorAction SilentlyContinue
                    if ($chrome) {
                        $version = (Get-Item $chrome.'(Default)').VersionInfo.ProductVersion
                        Write-Output $version
                    }
                    '''
                    
                    result = subprocess.run([
                        "powershell", "-Command", powershell_cmd
                    ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        version = result.stdout.strip()
                        if len(version.split('.')) >= 3:
                            self._chrome_version = version
                            self._log(f"Chrome version detected via PowerShell: {version}", "SUCCESS")
                            return version
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                # Method 4: Check if Chrome is in PATH
                try:
                    chrome_in_path = shutil.which('chrome')
                    if chrome_in_path:
                        result = subprocess.run([
                            chrome_in_path, "--version"
                        ], capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                        
                        if result.returncode == 0:
                            import re
                            version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                            if version_match:
                                version = version_match.group(1)
                                self._chrome_version = version
                                self._log(f"Chrome version detected via PATH: {version}", "SUCCESS")
                                return version
                except:
                    pass
                            
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
        """Find existing ChromeDriver dengan improved validation untuk Ubuntu"""
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
            if self.system == "windows":
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=15,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
            else:
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
        """Download ChromeDriver dengan improved error handling untuk Ubuntu"""
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
        """Get download URL dengan improved platform detection untuk Ubuntu"""
        try:
            # Determine platform suffix
            if self.system == "windows":
                if self.architecture == "x64" or "64" in self.architecture:
                    platform_suffix = "win64"
                else:
                    platform_suffix = "win32"
            elif self.system == "linux":
                if "64" in self.architecture or "x86_64" in self.architecture:
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
        """Download and extract ChromeDriver dengan improved error handling untuk Ubuntu"""
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
        """Get ChromeDriver path dengan comprehensive fallback untuk Ubuntu"""
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
        """Show comprehensive troubleshooting tips untuk Ubuntu"""
        self._log("ChromeDriver setup failed. Troubleshooting tips:", "ERROR")
        
        if self.system == "linux":
            if self.is_ubuntu:
                self._log("Ubuntu VPS specific tips:", "INFO")
                self._log("1. Install Chrome: python driver_manager.py --install-chrome", "INFO")
                self._log("2. Install dependencies: sudo apt install -y libnss3 libgconf-2-4", "INFO")
                self._log("3. Check if running headless: echo $DISPLAY", "INFO")
            else:
                self._log("Linux specific tips:", "INFO")
                self._log("1. Install Chrome browser for your distribution", "INFO")
                self._log("2. Install required dependencies", "INFO")
            
            self._log("4. Download ChromeDriver manually: https://chromedriver.chromium.org/", "INFO")
            self._log("5. Place in /usr/local/bin/ and make executable: chmod +x chromedriver", "INFO")
        else:
            self._log("1. Install Google Chrome browser", "INFO")
            self._log("2. Download ChromeDriver from https://chromedriver.chromium.org/", "INFO")
            self._log("3. Place chromedriver.exe in your PATH or project folder", "INFO")
        
        self._log("6. Install webdriver-manager: pip install webdriver-manager", "INFO")
        self._log("7. Check Chrome and ChromeDriver version compatibility", "INFO")
        self._log("8. Run: python driver_manager.py --diagnostics", "INFO")
        self._log("9. Try: python fix_all_drivers.py", "INFO")

    def setup_selenium_service(self, headless: bool = None, additional_options: list = None):
        """Setup Selenium service dengan comprehensive error handling untuk Ubuntu"""
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
            self._log("Running in headless mode (VPS detected)", "INFO")
        
        # Ubuntu VPS specific options
        if self.is_ubuntu and (self.is_vps or self.is_headless):
            ubuntu_options = [
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--single-process',  # Important for VPS
                '--no-zygote',       # Important for VPS
                '--disable-setuid-sandbox'
            ]
            
            for option in ubuntu_options:
                chrome_options.add_argument(option)
        
        # Additional options
        default_options = [
            '--disable-extensions',
            '--disable-gpu',
            '--disable-notifications',
            '--disable-popup-blocking',
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
        if self.system == "windows":
            service = Service(
                chromedriver_path,
                log_path=os.devnull,
                service_args=['--silent'],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
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
        """Run comprehensive diagnostics untuk Ubuntu VPS"""
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
            if self.is_ubuntu:
                print(f"   Install with: python driver_manager.py --install-chrome")
            else:
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
        
        # Ubuntu specific checks
        if self.is_ubuntu:
            print(f"\n{Fore.YELLOW}Ubuntu VPS Checks:")
            
            # Check Chrome dependencies
            required_packages = ["libnss3", "libgconf-2-4", "libxss1"]
            for package in required_packages:
                try:
                    result = subprocess.run(["dpkg", "-l", package], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {package}: installed")
                    else:
                        print(f"❌ {package}: not installed")
                except:
                    print(f"❓ {package}: unknown")
        
        # Test driver creation
        print(f"\n{Fore.YELLOW}Driver Test:")
        try:
            driver = self.setup_selenium_service(headless=True)
            print(f"✅ Driver creation successful")
            
            # Test navigation
            driver.get("https://www.google.com")
            print(f"✅ Navigation test successful")
            
            driver.quit()
        except Exception as e:
            print(f"❌ Driver creation failed: {e}")

    def install_chrome_command(self):
        """Install Chrome via command line"""
        if self.is_ubuntu:
            success = self.install_chrome_ubuntu()
            if success:
                # Also install dependencies
                self.install_chrome_dependencies_ubuntu()
            return success
        else:
            self._log("Chrome auto-installation only supported on Ubuntu", "ERROR")
            return False


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

def install_chrome_ubuntu():
    """Install Chrome on Ubuntu"""
    return driver_manager.install_chrome_command()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Driver Manager")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics")
    parser.add_argument("--test", action="store_true", help="Test driver setup")
    parser.add_argument("--install-chrome", action="store_true", help="Install Chrome on Ubuntu")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    manager = UniversalDriverManager(debug=args.debug)
    
    if args.install_chrome:
        if manager.install_chrome_command():
            print(f"{Fore.GREEN}✅ Chrome installation completed!")
        else:
            print(f"{Fore.RED}❌ Chrome installation failed!")
    elif args.diagnostics:
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