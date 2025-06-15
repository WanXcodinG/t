#!/usr/bin/env python3
"""
Chrome Installer untuk Windows
Auto-download dan install Chrome browser jika tidak ditemukan
"""

import os
import sys
import subprocess
import requests
import tempfile
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def log(message: str, level: str = "INFO"):
    """Enhanced logging dengan warna"""
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "HEADER": Fore.LIGHTBLUE_EX
    }
    
    color = colors.get(level, Fore.WHITE)
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "HEADER": "🔧"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def check_chrome_installed():
    """Check if Chrome is installed"""
    log("Checking Chrome installation...", "HEADER")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    import re
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        version = version_match.group(1)
                        log(f"Chrome found: {path}", "SUCCESS")
                        log(f"Version: {version}", "SUCCESS")
                        return True, path, version
            except:
                pass
    
    log("Chrome browser not found", "WARNING")
    return False, None, None

def download_chrome():
    """Download Chrome installer"""
    log("Downloading Chrome installer...", "INFO")
    
    # Chrome download URL
    chrome_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        installer_path = os.path.join(temp_dir, "chrome_installer.exe")
        
        # Download Chrome installer
        log("Downloading from Google...", "INFO")
        response = requests.get(chrome_url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading: {percent:.1f}%", end="", flush=True)
        
        print()  # New line after progress
        log(f"Chrome installer downloaded: {installer_path}", "SUCCESS")
        log(f"Size: {downloaded / (1024*1024):.2f} MB", "INFO")
        
        return installer_path
        
    except Exception as e:
        log(f"Failed to download Chrome: {e}", "ERROR")
        return None

def install_chrome(installer_path):
    """Install Chrome"""
    log("Installing Chrome...", "INFO")
    
    try:
        # Run Chrome installer silently
        log("Running Chrome installer (this may take a few minutes)...", "INFO")
        
        # Silent install command
        cmd = [installer_path, "/silent", "/install"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log("Chrome installation completed", "SUCCESS")
            return True
        else:
            log(f"Chrome installation failed: {result.stderr}", "ERROR")
            
            # Try alternative installation
            log("Trying alternative installation method...", "WARNING")
            
            # Just run the installer normally (user will see UI)
            subprocess.run([installer_path], timeout=300)
            log("Chrome installer launched. Please complete installation manually.", "INFO")
            
            return True
            
    except subprocess.TimeoutExpired:
        log("Chrome installation timeout", "ERROR")
        return False
    except Exception as e:
        log(f"Chrome installation error: {e}", "ERROR")
        return False

def verify_chrome_installation():
    """Verify Chrome installation"""
    log("Verifying Chrome installation...", "INFO")
    
    # Wait a bit for installation to complete
    import time
    time.sleep(5)
    
    # Check again
    found, path, version = check_chrome_installed()
    
    if found:
        log("Chrome installation verified successfully!", "SUCCESS")
        log(f"Chrome path: {path}", "INFO")
        log(f"Chrome version: {version}", "INFO")
        return True
    else:
        log("Chrome installation verification failed", "ERROR")
        return False

def cleanup_installer(installer_path):
    """Cleanup installer file"""
    try:
        if installer_path and os.path.exists(installer_path):
            os.remove(installer_path)
            # Also remove temp directory
            temp_dir = os.path.dirname(installer_path)
            os.rmdir(temp_dir)
            log("Installer cleanup completed", "INFO")
    except Exception as e:
        log(f"Cleanup error: {e}", "WARNING")

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🌐 Chrome Browser Installer untuk Windows")
    print("=" * 50)
    
    # Step 1: Check if Chrome is already installed
    found, path, version = check_chrome_installed()
    
    if found:
        log("Chrome is already installed and working!", "SUCCESS")
        return True
    
    # Step 2: Ask user confirmation
    print(f"\n{Fore.YELLOW}Chrome browser diperlukan untuk Social Media Uploader.")
    print(f"{Fore.YELLOW}Apakah Anda ingin menginstall Chrome sekarang?")
    
    choice = input(f"\n{Fore.WHITE}Install Chrome? (Y/n): ").strip().lower()
    
    if choice == 'n':
        log("Chrome installation cancelled by user", "WARNING")
        log("Please install Chrome manually from: https://www.google.com/chrome/", "INFO")
        return False
    
    # Step 3: Download Chrome installer
    installer_path = download_chrome()
    
    if not installer_path:
        log("Failed to download Chrome installer", "ERROR")
        return False
    
    # Step 4: Install Chrome
    try:
        if install_chrome(installer_path):
            # Step 5: Verify installation
            if verify_chrome_installation():
                log("Chrome installation completed successfully!", "SUCCESS")
                
                # Cleanup
                cleanup_installer(installer_path)
                
                print(f"\n{Fore.GREEN}🎉 Chrome berhasil diinstall!")
                print(f"{Fore.CYAN}Sekarang Anda dapat menjalankan Social Media Uploader.")
                print(f"\n{Fore.YELLOW}Next steps:")
                print("1. python social_media_uploader.py")
                print("2. python fix_all_drivers.py")
                
                return True
            else:
                log("Chrome installation verification failed", "ERROR")
                cleanup_installer(installer_path)
                return False
        else:
            log("Chrome installation failed", "ERROR")
            cleanup_installer(installer_path)
            return False
            
    except Exception as e:
        log(f"Installation process error: {e}", "ERROR")
        cleanup_installer(installer_path)
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print(f"\n{Fore.RED}❌ Chrome installation failed")
            print(f"{Fore.YELLOW}Manual installation:")
            print("1. Visit: https://www.google.com/chrome/")
            print("2. Download and install Chrome")
            print("3. Run: python social_media_uploader.py")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Installation cancelled by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error: {str(e)}")
        sys.exit(1)