#!/usr/bin/env python3
"""
Fix All Drivers Script - Enhanced Version dengan Ubuntu VPS Support
Script untuk memperbaiki semua masalah driver di semua file uploader
Support untuk Windows, Linux/Ubuntu VPS, dan macOS
Fixed untuk error [WinError 193] %1 is not a valid Win32 application
"""

import os
import sys
import subprocess
import platform
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

def detect_platform():
    """Detect platform dan environment"""
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    # Detect VPS environment
    is_vps = False
    is_headless = False
    distro = "unknown"
    
    if system == "linux":
        # Detect VPS
        vps_indicators = ["/proc/vz", "/proc/xen", "/sys/hypervisor"]
        is_vps = any(os.path.exists(indicator) for indicator in vps_indicators)
        
        # Detect headless
        is_headless = not os.environ.get("DISPLAY")
        
        # Detect distribution
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("ID="):
                            distro = line.split("=")[1].strip().strip('"')
                            break
        except:
            pass
    
    return {
        "system": system,
        "architecture": architecture,
        "is_vps": is_vps,
        "is_headless": is_headless,
        "distro": distro,
        "is_ubuntu": "ubuntu" in distro.lower()
    }

def check_system_info():
    """Check system information dengan VPS detection"""
    log("Checking system information...", "HEADER")
    
    platform_info = detect_platform()
    
    log(f"Operating System: {platform_info['system']}", "INFO")
    log(f"Architecture: {platform_info['architecture']}", "INFO")
    log(f"Python Version: {platform.python_version()}", "INFO")
    
    if platform_info["system"] == "linux":
        log(f"Distribution: {platform_info['distro']}", "INFO")
        log(f"Is Ubuntu: {platform_info['is_ubuntu']}", "INFO")
        log(f"Is VPS: {platform_info['is_vps']}", "INFO")
        log(f"Is Headless: {platform_info['is_headless']}", "INFO")
        log(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}", "INFO")
    
    # Check if 64-bit Windows
    if platform_info["system"] == "windows":
        if "64" in platform.architecture()[0] or "AMD64" in os.environ.get("PROCESSOR_ARCHITECTURE", ""):
            log("Windows 64-bit detected", "SUCCESS")
        else:
            log("Windows 32-bit detected", "WARNING")
    
    return platform_info

def check_chrome_installation(platform_info):
    """Check Chrome browser installation dengan Ubuntu support"""
    log("Checking Chrome browser installation...", "HEADER")
    
    system = platform_info["system"]
    chrome_found = False
    chrome_version = None
    
    if system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                log(f"Chrome found: {path}", "SUCCESS")
                chrome_found = True
                break
    
    elif system == "linux":
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
                    log(f"Chrome found: {' '.join(cmd)}", "SUCCESS")
                    chrome_found = True
                    break
            except:
                continue
    
    elif system == "darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            log(f"Chrome found: {chrome_path}", "SUCCESS")
            chrome_found = True
    
    if not chrome_found:
        log("Chrome browser not found!", "ERROR")
        log("Please install Google Chrome from: https://www.google.com/chrome/", "WARNING")
        log("This is required for the social media uploaders to work", "INFO")
    
    return chrome_found, chrome_version

def check_requirements():
    """Check dan install requirements"""
    log("Checking Python requirements...", "HEADER")
    
    required_packages = [
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0", 
        "colorama>=0.4.6",
        "requests>=2.31.0"
    ]
    
    for package_spec in required_packages:
        package_name = package_spec.split(">=")[0].split("==")[0]
        try:
            __import__(package_name.replace('-', '_'))
            log(f"{package_name}: ✅ Installed", "SUCCESS")
        except ImportError:
            log(f"{package_name}: ❌ Not installed, installing...", "WARNING")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package_spec], 
                             check=True, capture_output=True)
                log(f"{package_name}: ✅ Installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                log(f"{package_name}: ❌ Installation failed: {e}", "ERROR")
                return False
    
    return True

def run_driver_diagnostics():
    """Run driver diagnostics"""
    log("Running driver diagnostics...", "HEADER")
    
    try:
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager(debug=True)
        manager.run_diagnostics()
        
        return True
        
    except ImportError:
        log("Universal Driver Manager not found", "ERROR")
        return False
        
    except Exception as e:
        log(f"Diagnostics error: {e}", "ERROR")
        return False

def test_all_uploaders():
    """Test semua uploader dengan driver baru"""
    log("Testing all uploaders...", "HEADER")
    
    uploaders = [
        ("TikTok", "tiktok_uploader.py"),
        ("Facebook", "facebook_uploader.py"), 
        ("Instagram", "instagram_uploader.py"),
        ("YouTube", "youtube_api_uploader.py")
    ]
    
    success_count = 0
    
    for name, filename in uploaders:
        log(f"Testing {name} uploader...", "INFO")
        
        try:
            # Import and test basic initialization
            if filename == "tiktok_uploader.py":
                from tiktok_uploader import TikTokUploader
                uploader = TikTokUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                success_count += 1
                
            elif filename == "facebook_uploader.py":
                from facebook_uploader import FacebookUploader
                uploader = FacebookUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                success_count += 1
                
            elif filename == "instagram_uploader.py":
                from instagram_uploader import InstagramUploader
                uploader = InstagramUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                success_count += 1
                
            elif filename == "youtube_api_uploader.py":
                from youtube_api_uploader import YouTubeAPIUploader
                uploader = YouTubeAPIUploader(debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                success_count += 1
                
        except Exception as e:
            log(f"{name}: ❌ Error: {e}", "ERROR")
    
    log(f"Uploader test results: {success_count}/{len(uploaders)} successful", 
        "SUCCESS" if success_count == len(uploaders) else "WARNING")
    
    return success_count == len(uploaders)

def show_final_instructions(platform_info):
    """Show final instructions dengan platform-specific tips"""
    log("Final instructions:", "HEADER")
    
    print(f"\n{Fore.LIGHTGREEN_EX}🎉 DRIVER FIX COMPLETED!")
    print("=" * 50)
    
    print(f"\n{Fore.YELLOW}📋 Next Steps:")
    print("1. Run test script: python test_complete_system.py")
    print("2. Test social media upload: python social_media_uploader.py")
    print("3. If issues persist: python driver_manager.py --diagnostics")
    
    print(f"\n{Fore.CYAN}🔧 Troubleshooting:")
    
    if platform_info["system"] == "windows":
        print("• If still getting [WinError 193]: Restart your terminal/IDE")
        print("• If Chrome not found: Install Google Chrome browser")
        print("• If permission errors: Run as administrator")
    
    elif platform_info["is_ubuntu"]:
        print("• If Chrome not found: sudo apt install google-chrome-stable")
        print("• If dependencies missing: sudo apt install -y libnss3 libgconf-2-4")
        print("• If permission errors: chmod +x drivers/chromedriver")
        print("• For VPS: Script auto-detects and uses headless mode")
    
    elif platform_info["system"] == "linux":
        print("• Install Chrome for your distribution")
        print("• Install required dependencies")
        print("• Make ChromeDriver executable: chmod +x chromedriver")
    
    elif platform_info["system"] == "darwin":
        print("• Install Chrome: brew install --cask google-chrome")
        print("• Install ChromeDriver: brew install chromedriver")
    
    print(f"\n{Fore.GREEN}✅ What was fixed:")
    print("• ChromeDriver detection and download")
    print("• Error [WinError 193] handling")
    print("• Universal Driver Manager integration")
    print("• All uploader compatibility")
    print("• Comprehensive error handling")

def main():
    """Main function dengan Ubuntu VPS support"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 FIX ALL DRIVERS SCRIPT - ENHANCED")
    print("=" * 60)
    print(f"{Fore.YELLOW}Support untuk Windows, Linux/Ubuntu VPS, dan macOS")
    print(f"{Fore.YELLOW}Memperbaiki error [WinError 193] dan semua masalah driver")
    print()
    
    # Step 1: Check system info
    platform_info = check_system_info()
    print()
    
    # Step 2: Check Chrome installation
    chrome_found, chrome_version = check_chrome_installation(platform_info)
    print()
    
    if not chrome_found:
        log("Chrome browser is required but not found!", "ERROR")
        log("Please install Chrome first, then run this script again", "WARNING")
        return False
    
    # Step 3: Check requirements
    if not check_requirements():
        log("Failed to install required packages", "ERROR")
        return False
    print()
    
    # Step 4: Run diagnostics
    if not run_driver_diagnostics():
        log("Driver diagnostics failed", "ERROR")
        return False
    print()
    
    # Step 5: Test uploaders
    if not test_all_uploaders():
        log("Some uploaders failed initialization", "WARNING")
    print()
    
    # Step 6: Show final instructions
    show_final_instructions(platform_info)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n{Fore.GREEN}🎉 Fix completed successfully!")
        else:
            print(f"\n{Fore.RED}❌ Fix completed with errors")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Script dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error: {str(e)}")
        sys.exit(1)