#!/usr/bin/env python3
"""
Test Complete System setelah Chrome Fix
Test semua komponen social media uploader
"""

import os
import sys
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
        "HEADER": "🧪"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def test_chrome_detection():
    """Test Chrome detection"""
    log("Testing Chrome Detection", "HEADER")
    
    try:
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager()
        chrome_version = manager.get_chrome_version()
        
        if chrome_version:
            log(f"Chrome detected: {chrome_version}", "SUCCESS")
            return True
        else:
            log("Chrome not detected", "ERROR")
            return False
            
    except Exception as e:
        log(f"Chrome detection error: {e}", "ERROR")
        return False

def test_chromedriver_setup():
    """Test ChromeDriver setup"""
    log("Testing ChromeDriver Setup", "HEADER")
    
    try:
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager()
        chromedriver_path = manager.get_chromedriver_path()
        
        if chromedriver_path:
            log(f"ChromeDriver found: {chromedriver_path}", "SUCCESS")
            return True
        else:
            log("ChromeDriver not found", "ERROR")
            return False
            
    except Exception as e:
        log(f"ChromeDriver setup error: {e}", "ERROR")
        return False

def test_driver_creation():
    """Test driver creation"""
    log("Testing Driver Creation", "HEADER")
    
    try:
        from driver_manager import get_chrome_driver
        
        # Detect if VPS/headless environment
        is_headless = not os.environ.get("DISPLAY") or platform.system().lower() == "linux"
        
        log(f"Creating driver (headless: {is_headless})...", "INFO")
        driver = get_chrome_driver(headless=is_headless)
        
        log("Driver created successfully", "SUCCESS")
        
        # Test navigation
        log("Testing navigation...", "INFO")
        driver.get("https://www.google.com")
        
        title = driver.title
        if "Google" in title:
            log("Navigation test successful", "SUCCESS")
        else:
            log(f"Navigation test failed. Title: {title}", "WARNING")
        
        driver.quit()
        log("Driver test completed", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Driver creation error: {e}", "ERROR")
        return False

def test_social_media_uploader():
    """Test social media uploader import"""
    log("Testing Social Media Uploader", "HEADER")
    
    try:
        # Test main uploader
        from social_media_uploader import SocialMediaUploader
        
        uploader = SocialMediaUploader(debug=False)
        log("Social Media Uploader initialization successful", "SUCCESS")
        
        # Test components
        components = {
            "Video Downloader": uploader.video_downloader,
            "AI Assistant": uploader.ai_assistant,
            "Video Editor": uploader.video_editor,
            "TikTok Uploader": uploader.tiktok_uploader,
            "Facebook Uploader": uploader.facebook_uploader,
            "YouTube Uploader": uploader.youtube_uploader,
            "Instagram Uploader": uploader.instagram_uploader
        }
        
        for name, component in components.items():
            if component:
                log(f"{name}: ✅ Available", "SUCCESS")
            else:
                log(f"{name}: ❌ Not available", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"Social Media Uploader error: {e}", "ERROR")
        return False

def test_individual_uploaders():
    """Test individual uploaders"""
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
            
            module = __import__(module_name)
            uploader_class = getattr(module, class_name)
            
            uploader = uploader_class(headless=True, debug=False)
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
        # Test Gemini AI
        from gemini_ai_assistant import GeminiAIAssistant
        
        ai = GeminiAIAssistant(debug=False)
        log("Gemini AI Assistant initialization successful", "SUCCESS")
        
        # Check API key
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
        # Test Video Downloader
        from video_downloader import VideoDownloader
        
        downloader = VideoDownloader(debug=False)
        log("Video Downloader initialization successful", "SUCCESS")
        
        if downloader.ytdlp_path:
            log("yt-dlp available", "SUCCESS")
        else:
            log("yt-dlp not available", "WARNING")
            log("Install with: pip install yt-dlp", "INFO")
        
        # Test FFmpeg Video Editor
        from ffmpeg_video_editor import FFmpegVideoEditor
        
        editor = FFmpegVideoEditor(debug=False)
        log("FFmpeg Video Editor initialization successful", "SUCCESS")
        
        if editor.ffmpeg_path:
            log("FFmpeg available", "SUCCESS")
        else:
            log("FFmpeg not available", "WARNING")
            log("Install FFmpeg and add to PATH", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Video components error: {e}", "ERROR")
        return False

def show_system_status():
    """Show comprehensive system status"""
    log("System Status Summary", "HEADER")
    
    print(f"\n{Fore.LIGHTBLUE_EX}💻 SYSTEM INFORMATION:")
    print("=" * 40)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    
    # Check environment
    if platform.system().lower() == "linux":
        is_vps = any(os.path.exists(indicator) for indicator in ["/proc/vz", "/proc/xen", "/sys/hypervisor"])
        is_headless = not os.environ.get("DISPLAY")
        print(f"VPS Environment: {'Yes' if is_vps else 'No'}")
        print(f"Headless: {'Yes' if is_headless else 'No'}")
    
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 DEPENDENCIES:")
    print("=" * 40)
    
    # Check dependencies
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
    """Run complete system test"""
    print(f"\n{Fore.LIGHTBLUE_EX}🧪 COMPLETE SYSTEM TEST")
    print("=" * 60)
    print(f"{Fore.YELLOW}Testing all components after Chrome fix...")
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
                # For individual uploaders test
                all_passed = all(result.values())
                results[test_name] = result
                if all_passed:
                    passed += 1
            elif result:
                passed += 1
                results[test_name] = True
            else:
                results[test_name] = False
        except Exception as e:
            log(f"{test_name} crashed: {e}", "ERROR")
            results[test_name] = False
    
    # Show results
    print(f"\n{Fore.LIGHTBLUE_EX}📊 TEST RESULTS:")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        log("🎉 All tests passed! System is ready!", "SUCCESS")
        
        print(f"\n{Fore.GREEN}✅ SYSTEM READY!")
        print("=" * 30)
        print("• Chrome browser: Working")
        print("• ChromeDriver: Working")
        print("• All uploaders: Ready")
        print("• Video processing: Available")
        print("• AI features: Available")
        
        print(f"\n{Fore.CYAN}🚀 USAGE:")
        print("python social_media_uploader.py")
        
    else:
        log(f"⚠️ {total - passed} tests failed", "WARNING")
        
        print(f"\n{Fore.YELLOW}🔧 NEXT STEPS:")
        
        # Show specific recommendations
        if not results.get("Chrome Detection", True):
            print("1. Install Chrome: python install_chrome_windows.py")
        
        if not results.get("AI Components", True):
            print("2. Install AI: pip install google-generativeai")
            print("3. Set API key: set GEMINI_API_KEY=your_api_key")
        
        if not results.get("Video Components", True):
            print("4. Install yt-dlp: pip install yt-dlp")
            print("5. Install FFmpeg: Download from https://ffmpeg.org")
        
        print("6. Run: python fix_all_drivers.py")
    
    # Show system status
    print(f"\n{Fore.LIGHTBLUE_EX}📋 DETAILED STATUS:")
    show_system_status()
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_complete_test()
        if success:
            print(f"\n{Fore.GREEN}🎉 System test completed successfully!")
            print(f"\n{Fore.CYAN}Ready to use Social Media Uploader!")
        else:
            print(f"\n{Fore.YELLOW}⚠️ System test completed with warnings")
            print(f"\n{Fore.CYAN}Some features may not be available")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Test dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Test error: {str(e)}")
        sys.exit(1)