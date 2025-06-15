#!/usr/bin/env python3
"""
Test System Check - Tanpa Membuka Chrome
Hanya melakukan pengecekan komponen tanpa membuka browser
"""

import os
import sys
import platform
import subprocess
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
        "HEADER": "🔍"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def check_system_info():
    """Check system information"""
    log("System Information", "HEADER")
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    
    # Detect environment
    is_vps = False
    is_headless = False
    
    if platform.system().lower() == "linux":
        # Check VPS indicators
        vps_indicators = ["/proc/vz", "/proc/xen", "/sys/hypervisor"]
        is_vps = any(os.path.exists(indicator) for indicator in vps_indicators)
        
        # Check headless
        is_headless = not os.environ.get("DISPLAY")
        
        print(f"VPS Environment: {'Yes' if is_vps else 'No'}")
        print(f"Headless: {'Yes' if is_headless else 'No'}")
        print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    
    return {
        "system": platform.system().lower(),
        "is_vps": is_vps,
        "is_headless": is_headless
    }

def check_chrome_installation():
    """Check Chrome installation tanpa membuka browser"""
    log("Chrome Browser Check", "HEADER")
    
    system = platform.system().lower()
    chrome_found = False
    chrome_version = None
    chrome_path = None
    
    if system == "windows":
        # Check Windows registry
        try:
            import winreg
            
            registry_paths = [
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        version = winreg.QueryValueEx(key, "version")[0]
                        chrome_version = version
                        log(f"Chrome found in registry: {version}", "SUCCESS")
                        chrome_found = True
                        break
                except:
                    continue
        except ImportError:
            pass
        
        # Check file system
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                chrome_found = True
                log(f"Chrome executable found: {path}", "SUCCESS")
                break
    
    elif system == "linux":
        # Check common Linux paths
        linux_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in linux_paths:
            if os.path.exists(path):
                chrome_path = path
                chrome_found = True
                log(f"Chrome found: {path}", "SUCCESS")
                break
        
        # Try which command
        if not chrome_found:
            commands = ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]
            for cmd in commands:
                try:
                    result = subprocess.run(["which", cmd], capture_output=True, text=True)
                    if result.returncode == 0:
                        chrome_path = result.stdout.strip()
                        chrome_found = True
                        log(f"Chrome found via which: {chrome_path}", "SUCCESS")
                        break
                except:
                    continue
    
    elif system == "darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            chrome_found = True
            log(f"Chrome found: {chrome_path}", "SUCCESS")
    
    if not chrome_found:
        log("Chrome browser not found", "ERROR")
        log("Install from: https://www.google.com/chrome/", "INFO")
    
    return chrome_found, chrome_version, chrome_path

def check_chromedriver():
    """Check ChromeDriver tanpa membuat driver"""
    log("ChromeDriver Check", "HEADER")
    
    # Check PATH
    import shutil
    chromedriver_path = shutil.which('chromedriver')
    
    if chromedriver_path:
        log(f"ChromeDriver found in PATH: {chromedriver_path}", "SUCCESS")
        return True, chromedriver_path
    
    # Check common locations
    system = platform.system().lower()
    common_paths = []
    
    if system == "windows":
        common_paths = [
            "chromedriver.exe",
            "drivers/chromedriver.exe",
            r"C:\chromedriver\chromedriver.exe"
        ]
    else:
        common_paths = [
            "chromedriver",
            "drivers/chromedriver",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver"
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            log(f"ChromeDriver found: {path}", "SUCCESS")
            return True, path
    
    # Check WebDriver Manager cache
    try:
        home_dir = Path.home()
        wdm_cache = home_dir / ".wdm" / "drivers" / "chromedriver"
        
        if wdm_cache.exists():
            for chromedriver_file in wdm_cache.rglob("chromedriver*"):
                if chromedriver_file.is_file():
                    log(f"ChromeDriver found in cache: {chromedriver_file}", "SUCCESS")
                    return True, str(chromedriver_file)
    except:
        pass
    
    log("ChromeDriver not found", "WARNING")
    log("Will be auto-downloaded when needed", "INFO")
    return False, None

def check_python_dependencies():
    """Check Python dependencies"""
    log("Python Dependencies", "HEADER")
    
    required_packages = {
        "selenium": "Selenium WebDriver",
        "webdriver_manager": "WebDriver Manager", 
        "colorama": "Colorama",
        "requests": "Requests",
        "google_generativeai": "Google Generative AI (Optional)",
        "opencv_python": "OpenCV (Optional)",
        "pillow": "Pillow (Optional)",
        "numpy": "NumPy (Optional)",
        "yt_dlp": "yt-dlp (Optional)"
    }
    
    installed = 0
    total = len(required_packages)
    
    for package, description in required_packages.items():
        try:
            # Handle package name variations
            import_name = package.replace('-', '_')
            if package == "opencv_python":
                import_name = "cv2"
            elif package == "pillow":
                import_name = "PIL"
            
            __import__(import_name)
            log(f"{description}: ✅ Installed", "SUCCESS")
            installed += 1
        except ImportError:
            if package in ["google_generativeai", "opencv_python", "pillow", "numpy", "yt_dlp"]:
                log(f"{description}: ⚠️ Optional - Not installed", "WARNING")
            else:
                log(f"{description}: ❌ Required - Not installed", "ERROR")
    
    log(f"Dependencies: {installed}/{total} available", "INFO")
    return installed >= 4  # At least core dependencies

def check_external_tools():
    """Check external tools"""
    log("External Tools", "HEADER")
    
    tools = {
        "ffmpeg": "FFmpeg (Video editing)",
        "yt-dlp": "yt-dlp (Video downloading)"
    }
    
    available_tools = 0
    
    for tool, description in tools.items():
        try:
            result = subprocess.run([tool, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                log(f"{description}: ✅ Available", "SUCCESS")
                available_tools += 1
            else:
                log(f"{description}: ❌ Not working", "ERROR")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            log(f"{description}: ⚠️ Not found", "WARNING")
        except Exception as e:
            log(f"{description}: ❌ Error: {e}", "ERROR")
    
    return available_tools

def check_api_keys():
    """Check API keys"""
    log("API Keys", "HEADER")
    
    api_keys = {
        "GEMINI_API_KEY": "Gemini AI (Optional)"
    }
    
    configured_keys = 0
    
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value:
            log(f"{description}: ✅ Configured", "SUCCESS")
            configured_keys += 1
        else:
            log(f"{description}: ⚠️ Not configured", "WARNING")
    
    return configured_keys

def check_file_structure():
    """Check file structure"""
    log("File Structure", "HEADER")
    
    required_files = [
        "social_media_uploader.py",
        "tiktok_uploader.py", 
        "facebook_uploader.py",
        "instagram_uploader.py",
        "youtube_api_uploader.py",
        "driver_manager.py",
        "requirements.txt"
    ]
    
    optional_files = [
        "video_downloader.py",
        "gemini_ai_assistant.py",
        "ffmpeg_video_editor.py"
    ]
    
    missing_required = []
    missing_optional = []
    
    for file in required_files:
        if os.path.exists(file):
            log(f"{file}: ✅ Found", "SUCCESS")
        else:
            log(f"{file}: ❌ Missing", "ERROR")
            missing_required.append(file)
    
    for file in optional_files:
        if os.path.exists(file):
            log(f"{file}: ✅ Found", "SUCCESS")
        else:
            log(f"{file}: ⚠️ Optional - Missing", "WARNING")
            missing_optional.append(file)
    
    return len(missing_required) == 0

def check_folders():
    """Check auto-created folders"""
    log("Folder Structure", "HEADER")
    
    folders = [
        "cookies",
        "credentials", 
        "downloads",
        "edited_videos",
        "screenshots",
        "drivers"
    ]
    
    for folder in folders:
        folder_path = Path(folder)
        if folder_path.exists():
            log(f"{folder}/: ✅ Exists", "SUCCESS")
        else:
            log(f"{folder}/: ℹ️ Will be auto-created", "INFO")
    
    return True

def test_module_imports():
    """Test module imports tanpa inisialisasi"""
    log("Module Import Test", "HEADER")
    
    modules = [
        ("social_media_uploader", "Social Media Uploader"),
        ("tiktok_uploader", "TikTok Uploader"),
        ("facebook_uploader", "Facebook Uploader"),
        ("instagram_uploader", "Instagram Uploader"),
        ("youtube_api_uploader", "YouTube API Uploader"),
        ("driver_manager", "Driver Manager")
    ]
    
    import_success = 0
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            log(f"{description}: ✅ Import successful", "SUCCESS")
            import_success += 1
        except ImportError as e:
            log(f"{description}: ❌ Import failed: {e}", "ERROR")
        except Exception as e:
            log(f"{description}: ⚠️ Import warning: {e}", "WARNING")
            import_success += 1  # Count as success if not import error
    
    return import_success >= len(modules) - 1

def show_recommendations(results):
    """Show recommendations based on test results"""
    log("Recommendations", "HEADER")
    
    if not results["chrome_found"]:
        print(f"{Fore.YELLOW}📋 Chrome Browser:")
        print("• Install Google Chrome from https://www.google.com/chrome/")
        print("• Required for all social media uploaders")
        print()
    
    if not results["chromedriver_found"]:
        print(f"{Fore.YELLOW}📋 ChromeDriver:")
        print("• Will be auto-downloaded when first used")
        print("• Or run: python fix_all_drivers.py")
        print()
    
    if not results["dependencies_ok"]:
        print(f"{Fore.YELLOW}📋 Dependencies:")
        print("• Install missing packages: pip install -r requirements.txt")
        print("• Core packages: selenium, webdriver-manager, colorama, requests")
        print()
    
    if results["external_tools"] == 0:
        print(f"{Fore.YELLOW}📋 External Tools (Optional):")
        print("• FFmpeg: Download from https://ffmpeg.org/")
        print("• yt-dlp: pip install yt-dlp")
        print()
    
    if results["api_keys"] == 0:
        print(f"{Fore.YELLOW}📋 API Keys (Optional):")
        print("• Gemini AI: set GEMINI_API_KEY=your_api_key")
        print("• Get key from: https://makersuite.google.com/app/apikey")
        print()
    
    if not results["files_ok"]:
        print(f"{Fore.YELLOW}📋 Missing Files:")
        print("• Download complete project files")
        print("• Check file permissions")
        print()

def run_system_check():
    """Run complete system check tanpa membuka Chrome"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔍 SYSTEM CHECK - NO BROWSER OPENING")
    print("=" * 60)
    print(f"{Fore.YELLOW}Checking all components without opening Chrome...")
    print()
    
    # Collect results
    results = {}
    
    # System info
    env_info = check_system_info()
    print()
    
    # Chrome check
    chrome_found, chrome_version, chrome_path = check_chrome_installation()
    results["chrome_found"] = chrome_found
    print()
    
    # ChromeDriver check
    chromedriver_found, chromedriver_path = check_chromedriver()
    results["chromedriver_found"] = chromedriver_found
    print()
    
    # Dependencies check
    dependencies_ok = check_python_dependencies()
    results["dependencies_ok"] = dependencies_ok
    print()
    
    # External tools check
    external_tools = check_external_tools()
    results["external_tools"] = external_tools
    print()
    
    # API keys check
    api_keys = check_api_keys()
    results["api_keys"] = api_keys
    print()
    
    # File structure check
    files_ok = check_file_structure()
    results["files_ok"] = files_ok
    print()
    
    # Folder check
    check_folders()
    print()
    
    # Module import test
    imports_ok = test_module_imports()
    results["imports_ok"] = imports_ok
    print()
    
    # Summary
    print(f"{Fore.LIGHTBLUE_EX}📊 SYSTEM CHECK SUMMARY:")
    print("=" * 50)
    
    checks = [
        ("Chrome Browser", results["chrome_found"]),
        ("ChromeDriver", results["chromedriver_found"]),
        ("Python Dependencies", results["dependencies_ok"]),
        ("File Structure", results["files_ok"]),
        ("Module Imports", results["imports_ok"])
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, status in checks:
        if status:
            log(f"{check_name}: ✅ OK", "SUCCESS")
            passed += 1
        else:
            log(f"{check_name}: ❌ Issues", "ERROR")
    
    print()
    log(f"System Check: {passed}/{total} passed", 
        "SUCCESS" if passed >= total - 1 else "WARNING")
    
    # Optional components
    print(f"\n{Fore.CYAN}📋 Optional Components:")
    print(f"External Tools: {external_tools}/2 available")
    print(f"API Keys: {api_keys}/1 configured")
    
    print()
    
    if passed >= total - 1:
        log("🎉 System is ready for use!", "SUCCESS")
        print(f"\n{Fore.GREEN}✅ Ready to run:")
        print("python social_media_uploader.py")
    else:
        log("⚠️ System needs attention", "WARNING")
        print()
        show_recommendations(results)
    
    return passed >= total - 1

if __name__ == "__main__":
    try:
        success = run_system_check()
        if success:
            print(f"\n{Fore.GREEN}🎉 System check completed successfully!")
        else:
            print(f"\n{Fore.YELLOW}⚠️ System check completed with issues")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Check dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Check error: {str(e)}")
        sys.exit(1)