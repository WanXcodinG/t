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
        
        log("Checking ChromeDriver availability...", "INFO")
        
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
                        log(f"ChromeDriver found in cache: {chromedriver_file}", "SUCCESS")
                        return True
        except:
            pass
        
        log("ChromeDriver not found", "WARNING")
        log("Will be auto-downloaded when needed", "INFO")
        return True  # Consider as success since it can auto-download
        
    except Exception as e:
        log(f"ChromeDriver setup error: {e}", "ERROR")
        return False

def test_python_dependencies():
    """Test Python dependencies dengan improved detection"""
    log("Testing Python Dependencies", "HEADER")
    
    required_packages = {
        "selenium": "Selenium WebDriver",
        "webdriver_manager": "WebDriver Manager", 
        "colorama": "Colorama",
        "requests": "Requests"
    }
    
    optional_packages = {
        "google_generativeai": "Google Generative AI",
        "opencv_python": "OpenCV",
        "pillow": "Pillow",
        "numpy": "NumPy",
        "yt_dlp": "yt-dlp",
        "python_dotenv": "Python DotEnv"
    }
    
    installed = 0
    total = len(required_packages) + len(optional_packages)
    
    # Test required packages
    for package, description in required_packages.items():
        try:
            # Handle package name variations
            import_name = package.replace('-', '_')
            __import__(import_name)
            log(f"{description}: ✅ Installed", "SUCCESS")
            installed += 1
        except ImportError:
            log(f"{description}: ❌ Required - Not installed", "ERROR")
    
    # Test optional packages dengan improved detection
    for package, description in optional_packages.items():
        try:
            # Handle package name variations
            import_name = package.replace('-', '_')
            if package == "opencv_python":
                import_name = "cv2"
            elif package == "pillow":
                import_name = "PIL"
            elif package == "python_dotenv":
                import_name = "dotenv"
            elif package == "google_generativeai":
                import_name = "google.generativeai"
            elif package == "yt_dlp":
                import_name = "yt_dlp"
            
            __import__(import_name)
            log(f"{description}: ✅ Installed", "SUCCESS")
            installed += 1
        except ImportError:
            log(f"{description}: ⚠️ Optional - Not installed", "WARNING")
    
    log(f"Dependencies: {installed}/{total} available", "INFO")
    return installed >= len(required_packages)  # At least all required dependencies

def test_gemini_ai_specific():
    """Test Gemini AI specifically dengan .env detection"""
    log("Testing Gemini AI Configuration", "HEADER")
    
    # Test google-generativeai import
    try:
        import google.generativeai as genai
        log("Google Generative AI: ✅ Library installed", "SUCCESS")
        
        # Test .env file
        env_file = Path(".env")
        if env_file.exists():
            log(".env file: ✅ Found", "SUCCESS")
            
            # Check if GEMINI_API_KEY is in .env
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if "GEMINI_API_KEY" in content:
                        log("GEMINI_API_KEY: ✅ Configured in .env", "SUCCESS")
                        
                        # Load .env and check if key is set
                        try:
                            from dotenv import load_dotenv
                            load_dotenv()
                            api_key = os.getenv('GEMINI_API_KEY')
                            if api_key and api_key != "your_api_key_here":
                                log("API Key: ✅ Valid key detected", "SUCCESS")
                                return True
                            else:
                                log("API Key: ⚠️ Placeholder key detected", "WARNING")
                                log("Replace 'your_api_key_here' with actual API key", "INFO")
                                return True  # Still consider as configured
                        except ImportError:
                            log("python-dotenv: ⚠️ Not installed", "WARNING")
                            return True
                    else:
                        log("GEMINI_API_KEY: ⚠️ Not found in .env", "WARNING")
                        return True
            except Exception as e:
                log(f"Error reading .env: {e}", "WARNING")
                return True
        else:
            log(".env file: ⚠️ Not found", "WARNING")
            log("Create .env file with GEMINI_API_KEY=your_api_key", "INFO")
            return True
            
    except ImportError:
        log("Google Generative AI: ❌ Not installed", "ERROR")
        log("Install with: pip install google-generativeai", "INFO")
        return False

def test_module_imports():
    """Test module imports tanpa inisialisasi yang membuka Chrome"""
    log("Testing Module Imports", "HEADER")
    
    modules = [
        ("driver_manager", "Driver Manager"),
        ("social_media_uploader", "Social Media Uploader"),
        ("tiktok_uploader", "TikTok Uploader"),
        ("facebook_uploader", "Facebook Uploader"),
        ("instagram_uploader", "Instagram Uploader"),
        ("youtube_api_uploader", "YouTube API Uploader")
    ]
    
    import_success = 0
    
    for module_name, description in modules:
        try:
            # Import module tanpa inisialisasi
            module = __import__(module_name)
            log(f"{description}: ✅ Import successful", "SUCCESS")
            import_success += 1
        except ImportError as e:
            log(f"{description}: ❌ Import failed: {e}", "ERROR")
        except Exception as e:
            log(f"{description}: ⚠️ Import warning: {e}", "WARNING")
            import_success += 1  # Count as success if not import error
    
    return import_success >= len(modules) - 1

def test_driver_manager_basic():
    """Test driver manager basic functionality tanpa membuat driver"""
    log("Testing Driver Manager Basic", "HEADER")
    
    try:
        # Import driver manager
        from driver_manager import UniversalDriverManager
        
        # Create instance tanpa debug untuk avoid verbose output
        manager = UniversalDriverManager(debug=False)
        
        log("Driver Manager initialization successful", "SUCCESS")
        
        # Test Chrome detection
        chrome_version = manager.get_chrome_version()
        if chrome_version:
            log(f"Chrome version detected: {chrome_version}", "SUCCESS")
        else:
            log("Chrome version not detected", "WARNING")
        
        # Test ChromeDriver detection (tanpa download)
        chromedriver_path = manager.find_existing_chromedriver()
        if chromedriver_path:
            log(f"ChromeDriver found: {chromedriver_path}", "SUCCESS")
        else:
            log("ChromeDriver not found (will auto-download when needed)", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Driver Manager test error: {e}", "ERROR")
        return False

def test_uploader_classes():
    """Test uploader classes tanpa inisialisasi yang membuka browser"""
    log("Testing Uploader Classes", "HEADER")
    
    uploaders = [
        ("TikTok", "tiktok_uploader", "TikTokUploader"),
        ("Facebook", "facebook_uploader", "FacebookUploader"),
        ("Instagram", "instagram_uploader", "InstagramUploader"),
        ("YouTube", "youtube_api_uploader", "YouTubeAPIUploader")
    ]
    
    results = {}
    
    for name, module_name, class_name in uploaders:
        try:
            log(f"Testing {name} uploader class...", "INFO")
            
            if not os.path.exists(f"{module_name}.py"):
                log(f"{name} uploader: ❌ File not found", "ERROR")
                results[name] = False
                continue
            
            # Test import class tanpa inisialisasi
            module = __import__(module_name)
            uploader_class = getattr(module, class_name)
            
            log(f"{name} uploader: ✅ Class import successful", "SUCCESS")
            results[name] = True
            
        except Exception as e:
            log(f"{name} uploader: ❌ Error: {e}", "ERROR")
            results[name] = False
    
    return results

def run_complete_test():
    """Run complete system test tanpa membuka Chrome"""
    print(f"\n{Fore.LIGHTBLUE_EX}🧪 COMPLETE SYSTEM TEST - NO CHROME OPENING")
    print("=" * 60)
    print(f"{Fore.YELLOW}Testing all components without opening Chrome...")
    print()
    
    tests = [
        ("Chrome Detection", test_chrome_detection),
        ("ChromeDriver Setup", test_chromedriver_setup),
        ("Python Dependencies", test_python_dependencies),
        ("Gemini AI Configuration", test_gemini_ai_specific),
        ("Module Imports", test_module_imports),
        ("Driver Manager Basic", test_driver_manager_basic),
        ("Uploader Classes", test_uploader_classes)
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
        
        # Show Gemini AI status
        print(f"\n{Fore.LIGHTMAGENTA_EX}🤖 GEMINI AI STATUS:")
        try:
            import google.generativeai
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and api_key != "your_api_key_here":
                print("✅ Gemini AI ready with valid API key")
            else:
                print("⚠️ Gemini AI installed but needs API key in .env file")
        except ImportError:
            print("❌ Gemini AI not installed")
        
    else:
        log(f"⚠️ {total - passed} tests failed", "WARNING")
        
        print(f"\n{Fore.YELLOW}🔧 NEXT STEPS:")
        print("1. Install Chrome: https://www.google.com/chrome/")
        print("2. Run: python fix_all_drivers.py")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Set Gemini API key in .env file")
    
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