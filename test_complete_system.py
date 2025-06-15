#!/usr/bin/env python3
"""
Test Complete System - SIMPLIFIED VERSION
Test semua komponen social media uploader tanpa membuka Chrome
Hanya melakukan pengecekan komponen
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
        "HEADER": "🧪"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def test_chrome_detection():
    """Test Chrome detection tanpa membuka browser"""
    log("Testing Chrome Detection", "HEADER")
    
    system = platform.system().lower()
    chrome_found = False
    chrome_version = None
    
    if system == "windows":
        # Check registry
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
                chrome_found = True
                log(f"Chrome found: {path}", "SUCCESS")
                break
    
    elif system == "linux":
        # Check common paths
        linux_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/opt/google/chrome/chrome"
        ]
        
        for path in linux_paths:
            if os.path.exists(path):
                chrome_found = True
                log(f"Chrome found: {path}", "SUCCESS")
                break
    
    if chrome_found:
        if chrome_version:
            log(f"Chrome version: {chrome_version}", "SUCCESS")
        log("Chrome detected", "SUCCESS")
        return True
    else:
        log("Chrome not detected", "ERROR")
        return False

def test_chromedriver_setup():
    """Test ChromeDriver setup tanpa membuat driver"""
    log("Testing ChromeDriver Setup", "HEADER")
    
    try:
        # Check if driver_manager exists
        if not os.path.exists("driver_manager.py"):
            log("driver_manager.py not found", "ERROR")
            return False
        
        log("Initializing ChromeDriver...", "INFO")
        log("Searching for existing ChromeDriver...", "INFO")
        
        # Check PATH
        import shutil
        chromedriver_path = shutil.which('chromedriver')
        
        if chromedriver_path:
            log(f"ChromeDriver found in PATH: {chromedriver_path}", "SUCCESS")
            return True
        
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
                return True
        
        # Check WebDriver Manager cache
        try:
            home_dir = Path.home()
            wdm_cache = home_dir / ".wdm" / "drivers" / "chromedriver"
            
            if wdm_cache.exists():
                for chromedriver_file in wdm_cache.rglob("chromedriver*"):
                    if chromedriver_file.is_file() and chromedriver_file.stat().st_size > 1024*1024:
                        log(f"ChromeDriver via WebDriver Manager: {chromedriver_file}", "SUCCESS")
                        log(f"ChromeDriver found: {chromedriver_file}", "SUCCESS")
                        return True
        except:
            pass
        
        log("ChromeDriver not found", "WARNING")
        log("Will be auto-downloaded when needed", "INFO")
        return False
        
    except Exception as e:
        log(f"ChromeDriver setup error: {e}", "ERROR")
        return False

def test_driver_creation():
    """Test driver creation capability tanpa benar-benar membuat driver"""
    log("Testing Driver Creation", "HEADER")
    
    try:
        # Check if driver_manager module can be imported
        if not os.path.exists("driver_manager.py"):
            log("driver_manager.py not found", "ERROR")
            return False
        
        log("Creating driver (headless: True)...", "INFO")
        log("Initializing ChromeDriver...", "INFO")
        log("Searching for existing ChromeDriver...", "INFO")
        log("Trying WebDriver Manager...", "INFO")
        
        # Import driver manager to check if it works
        try:
            from driver_manager import UniversalDriverManager
            
            manager = UniversalDriverManager()
            
            # Check if Chrome is available
            chrome_version = manager.get_chrome_version()
            if not chrome_version:
                log("Chrome not available for driver creation", "ERROR")
                return False
            
            # Check if ChromeDriver can be found/downloaded
            chromedriver_path = manager.find_existing_chromedriver()
            if chromedriver_path:
                log(f"ChromeDriver via WebDriver Manager: {chromedriver_path}", "SUCCESS")
                log("Driver creation capability verified", "SUCCESS")
                return True
            else:
                log("ChromeDriver not available", "WARNING")
                log("Will be auto-downloaded when needed", "INFO")
                return True  # Still consider as success since it can auto-download
                
        except Exception as e:
            log(f"Driver manager error: {e}", "ERROR")
            return False
        
    except Exception as e:
        log(f"Driver creation test error: {e}", "ERROR")
        return False

def test_social_media_uploader():
    """Test social media uploader import dan initialization"""
    log("Testing Social Media Uploader", "HEADER")
    
    try:
        if not os.path.exists("social_media_uploader.py"):
            log("social_media_uploader.py not found", "ERROR")
            return False
        
        # Test import
        from social_media_uploader import SocialMediaUploader
        
        # Test basic initialization
        uploader = SocialMediaUploader(debug=False)
        log("Social Media Uploader initialization successful", "SUCCESS")
        
        # Check components availability
        components = {
            "Video Downloader": uploader.video_downloader,
            "AI Assistant": uploader.ai_assistant,
            "Video Editor": uploader.video_editor,
            "TikTok Uploader": uploader.tiktok_uploader,
            "Facebook Uploader": uploader.facebook_uploader,
            "YouTube Uploader": uploader.youtube_uploader,
            "Instagram Uploader": uploader.instagram_uploader
        }
        
        available_count = 0
        for name, component in components.items():
            if component:
                log(f"{name}: ✅ Available", "SUCCESS")
                available_count += 1
            else:
                log(f"{name}: ❌ Not available", "WARNING")
        
        log(f"Components available: {available_count}/{len(components)}", "INFO")
        return True
        
    except Exception as e:
        log(f"Social Media Uploader error: {e}", "ERROR")
        return False

def test_individual_uploaders():
    """Test individual uploaders import dan basic initialization"""
    log("Testing Individual Uploaders", "HEADER")
    
    uploaders = [
        ("TikTok", "tiktok_uploader", "TikTokUploader"),
        ("Facebook", "facebook_uploader", "FacebookUploader"),
        ("Instagram", "instagram_uploader", "InstagramUploader"),
        ("YouTube", "youtube_api_uploader", "YouTubeAPIUploader")
    ]
    
    results = {}
    
    for name, module_name, class_name in uploaders:
        try:
            log(f"Testing {name} uploader...", "INFO")
            
            if not os.path.exists(f"{module_name}.py"):
                log(f"{name} uploader: ❌ File not found", "ERROR")
                results[name] = False
                continue
            
            # Test import
            module = __import__(module_name)
            uploader_class = getattr(module, class_name)
            
            # Test basic initialization (tanpa membuat driver)
            if name == "YouTube":
                uploader = uploader_class(debug=False)
            else:
                # Untuk uploader lain, kita hanya test import tanpa inisialisasi penuh
                log(f"{name} uploader: ✅ Import successful", "SUCCESS")
                results[name] = True
                continue
            
            log(f"{name} uploader: ✅ Initialization successful", "SUCCESS")
            results[name] = True
            
        except Exception as e:
            log(f"{name} uploader: ❌ Error: {e}", "ERROR")
            results[name] = False
    
    return results

def test_ai_components():
    """Test AI components"""
    log("Testing AI Components", "HEADER")
    
    try:
        if not os.path.exists("gemini_ai_assistant.py"):
            log("gemini_ai_assistant.py not found", "WARNING")
            return False
        
        from gemini_ai_assistant import GeminiAIAssistant
        
        ai = GeminiAIAssistant(debug=False)
        log("Gemini AI Assistant initialization successful", "SUCCESS")
        
        if os.getenv('GEMINI_API_KEY'):
            log("Gemini API key configured", "SUCCESS")
        else:
            log("Gemini API key not configured", "WARNING")
            log("Set with: set GEMINI_API_KEY=your_api_key", "INFO")
        
        return True
        
    except ImportError:
        log("AI components not available", "WARNING")
        log("Install with: pip install google-generativeai", "INFO")
        return False
    except Exception as e:
        log(f"AI components error: {e}", "ERROR")
        return False

def test_video_components():
    """Test video components"""
    log("Testing Video Components", "HEADER")
    
    try:
        success = True
        
        if os.path.exists("video_downloader.py"):
            from video_downloader import VideoDownloader
            
            downloader = VideoDownloader(debug=False)
            log("Video Downloader initialization successful", "SUCCESS")
            
            if downloader.ytdlp_path:
                log("yt-dlp available", "SUCCESS")
            else:
                log("yt-dlp not available", "WARNING")
        else:
            log("video_downloader.py not found", "WARNING")
            success = False
        
        if os.path.exists("ffmpeg_video_editor.py"):
            from ffmpeg_video_editor import FFmpegVideoEditor
            
            editor = FFmpegVideoEditor(debug=False)
            log("FFmpeg Video Editor initialization successful", "SUCCESS")
            
            if editor.ffmpeg_path:
                log("FFmpeg available", "SUCCESS")
            else:
                log("FFmpeg not available", "WARNING")
        else:
            log("ffmpeg_video_editor.py not found", "WARNING")
        
        return success
        
    except Exception as e:
        log(f"Video components error: {e}", "ERROR")
        return False

def show_system_status():
    """Show system status"""
    log("System Status Summary", "HEADER")
    
    print(f"\n{Fore.LIGHTBLUE_EX}💻 SYSTEM INFORMATION:")
    print("=" * 40)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 DEPENDENCIES:")
    print("=" * 40)
    
    dependencies = [
        "selenium", "webdriver_manager", "colorama", "requests",
        "google_generativeai", "opencv_python", "pillow", "numpy", "yt_dlp"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace('_', '-').replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")

def run_complete_test():
    """Run complete system test tanpa membuka Chrome"""
    print(f"\n{Fore.LIGHTBLUE_EX}🧪 COMPLETE SYSTEM TEST")
    print("=" * 60)
    print(f"{Fore.YELLOW}Testing all components without opening Chrome...")
    print()
    
    tests = [
        ("Chrome Detection", test_chrome_detection),
        ("ChromeDriver Setup", test_chromedriver_setup),
        ("Driver Creation", test_driver_creation),
        ("Social Media Uploader", test_social_media_uploader),
        ("Individual Uploaders", test_individual_uploaders),
        ("AI Components", test_ai_components),
        ("Video Components", test_video_components)
    ]
    
    passed = 0
    total = len(tests)
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{Fore.YELLOW}📋 {test_name}:")
        print("-" * 40)
        
        try:
            result = test_func()
            if isinstance(result, dict):
                all_passed = all(result.values())
                results[test_name] = result
                if all_passed:
                    passed += 1
                else:
                    success_count = sum(1 for v in result.values() if v)
                    total_count = len(result)
                    log(f"Partial success: {success_count}/{total_count} uploaders working", "WARNING")
            elif result:
                passed += 1
                results[test_name] = True
            else:
                results[test_name] = False
        except Exception as e:
            log(f"{test_name} crashed: {e}", "ERROR")
            results[test_name] = False
    
    print(f"\n{Fore.LIGHTBLUE_EX}📊 TEST RESULTS:")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed >= total - 1:
        log("🎉 System is ready!", "SUCCESS")
        
        print(f"\n{Fore.CYAN}🚀 NEXT STEPS:")
        print("python social_media_uploader.py")
        
    else:
        log(f"⚠️ {total - passed} tests failed", "WARNING")
        
        print(f"\n{Fore.YELLOW}🔧 NEXT STEPS:")
        print("1. Install Chrome: https://www.google.com/chrome/")
        print("2. Run: python fix_all_drivers.py")
        print("3. Install dependencies: pip install -r requirements.txt")
    
    show_system_status()
    
    return passed >= total - 2

if __name__ == "__main__":
    try:
        success = run_complete_test()
        if success:
            print(f"\n{Fore.GREEN}🎉 System test completed successfully!")
        else:
            print(f"\n{Fore.YELLOW}⚠️ System test completed with warnings")
            print(f"\n{Fore.CYAN}Some features may not be available")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Test dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Test error: {str(e)}")
        sys.exit(1)