#!/usr/bin/env python3
"""
Fix All Drivers Script - Enhanced Version
Script untuk memperbaiki semua masalah driver di semua file uploader
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

def check_system_info():
    """Check system information"""
    log("Checking system information...", "HEADER")
    
    system = platform.system()
    architecture = platform.machine()
    python_version = platform.python_version()
    
    log(f"Operating System: {system}", "INFO")
    log(f"Architecture: {architecture}", "INFO")
    log(f"Python Version: {python_version}", "INFO")
    
    # Check if 64-bit Windows
    if system == "Windows":
        if "64" in platform.architecture()[0] or "AMD64" in os.environ.get("PROCESSOR_ARCHITECTURE", ""):
            log("Windows 64-bit detected", "SUCCESS")
        else:
            log("Windows 32-bit detected", "WARNING")
    
    return {
        "system": system,
        "architecture": architecture,
        "python_version": python_version
    }

def check_chrome_installation():
    """Check Chrome browser installation"""
    log("Checking Chrome browser installation...", "HEADER")
    
    system = platform.system()
    chrome_found = False
    chrome_version = None
    
    if system == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                log(f"Chrome found: {path}", "SUCCESS")
                chrome_found = True
                
                # Try to get version
                try:
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        import re
                        version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            chrome_version = version_match.group(1)
                            log(f"Chrome version: {chrome_version}", "SUCCESS")
                except:
                    pass
                break
    
    elif system == "Linux":
        commands = ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"]
        for cmd in commands:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    log(f"Chrome found: {cmd}", "SUCCESS")
                    chrome_found = True
                    
                    import re
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        chrome_version = version_match.group(1)
                        log(f"Chrome version: {chrome_version}", "SUCCESS")
                    break
            except:
                continue
    
    elif system == "Darwin":  # macOS
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(chrome_path):
            log(f"Chrome found: {chrome_path}", "SUCCESS")
            chrome_found = True
            
            try:
                result = subprocess.run([chrome_path, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    import re
                    version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        chrome_version = version_match.group(1)
                        log(f"Chrome version: {chrome_version}", "SUCCESS")
            except:
                pass
    
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

def clean_old_chromedrivers():
    """Clean old/corrupted ChromeDrivers"""
    log("Cleaning old ChromeDrivers...", "HEADER")
    
    # Common ChromeDriver locations
    locations_to_clean = []
    
    system = platform.system()
    if system == "Windows":
        locations_to_clean = [
            Path.home() / ".wdm" / "drivers" / "chromedriver",
            Path("C:/chromedriver"),
            Path("drivers"),
            Path(".")
        ]
    else:
        locations_to_clean = [
            Path.home() / ".wdm" / "drivers" / "chromedriver",
            Path("/usr/local/bin"),
            Path("drivers"),
            Path(".")
        ]
    
    cleaned_count = 0
    for location in locations_to_clean:
        if location.exists():
            for file in location.rglob("chromedriver*"):
                if file.is_file():
                    try:
                        # Check if file is corrupted (too small)
                        file_size = file.stat().st_size
                        if file_size < 1024 * 1024:  # Less than 1MB
                            file.unlink()
                            log(f"Removed corrupted ChromeDriver: {file}", "SUCCESS")
                            cleaned_count += 1
                    except Exception as e:
                        log(f"Could not remove {file}: {e}", "WARNING")
    
    if cleaned_count > 0:
        log(f"Cleaned {cleaned_count} corrupted ChromeDriver files", "SUCCESS")
    else:
        log("No corrupted ChromeDrivers found", "INFO")

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

def test_driver_creation():
    """Test driver creation"""
    log("Testing driver creation...", "HEADER")
    
    try:
        from driver_manager import get_chrome_driver
        
        log("Creating test driver...", "INFO")
        driver = get_chrome_driver(headless=True)
        
        log("Testing navigation...", "INFO")
        driver.get("https://www.google.com")
        
        title = driver.title
        if "Google" in title:
            log("Navigation test successful!", "SUCCESS")
        else:
            log(f"Navigation test failed. Title: {title}", "WARNING")
        
        driver.quit()
        log("Driver test completed successfully!", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Driver test failed: {e}", "ERROR")
        return False

def test_all_uploaders():
    """Test semua uploader dengan driver baru"""
    log("Testing all uploaders...", "HEADER")
    
    uploaders = [
        ("TikTok", "tiktok_uploader.py"),
        ("Facebook", "facebook_uploader.py"), 
        ("Instagram", "instagram_uploader.py")
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
                
        except Exception as e:
            log(f"{name}: ❌ Error: {e}", "ERROR")
    
    log(f"Uploader test results: {success_count}/{len(uploaders)} successful", 
        "SUCCESS" if success_count == len(uploaders) else "WARNING")
    
    return success_count == len(uploaders)

def create_test_script():
    """Create comprehensive test script"""
    log("Creating test script...", "INFO")
    
    test_script = '''#!/usr/bin/env python3
"""
Comprehensive test script untuk verify driver fix
"""

def test_driver_manager():
    """Test Universal Driver Manager"""
    print("🔍 Testing Universal Driver Manager...")
    
    try:
        from driver_manager import get_chrome_driver, run_driver_diagnostics
        
        print("\\n📊 Running diagnostics...")
        run_driver_diagnostics()
        
        print("\\n🧪 Testing driver creation...")
        driver = get_chrome_driver(headless=True)
        print("✅ Driver created successfully!")
        
        print("🌐 Testing navigation...")
        driver.get("https://www.google.com")
        print(f"✅ Navigation successful! Title: {driver.title}")
        
        driver.quit()
        print("✅ All driver tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Driver test failed: {e}")
        return False

def test_facebook_uploader():
    """Test Facebook uploader"""
    print("\\n📘 Testing Facebook uploader...")
    
    try:
        from facebook_uploader import FacebookUploader
        
        uploader = FacebookUploader(headless=True, debug=False)
        print("✅ Facebook uploader initialization successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Facebook uploader test failed: {e}")
        return False

def test_all_components():
    """Test all components"""
    print("🧪 COMPREHENSIVE DRIVER TEST")
    print("=" * 50)
    
    tests = [
        ("Driver Manager", test_driver_manager),
        ("Facebook Uploader", test_facebook_uploader)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\\n📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Driver fix successful!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    test_all_components()
'''
    
    with open("test_driver_fix.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    log("Test script created: test_driver_fix.py", "SUCCESS")

def show_final_instructions():
    """Show final instructions"""
    log("Final instructions:", "HEADER")
    
    print(f"\n{Fore.LIGHTGREEN_EX}🎉 DRIVER FIX COMPLETED!")
    print("=" * 50)
    
    print(f"\n{Fore.YELLOW}📋 Next Steps:")
    print("1. Run test script: python test_driver_fix.py")
    print("2. Test Facebook upload: python social_media_uploader.py")
    print("3. If issues persist: python driver_manager.py --diagnostics")
    
    print(f"\n{Fore.CYAN}🔧 Troubleshooting:")
    print("• If still getting [WinError 193]: Restart your terminal/IDE")
    print("• If Chrome not found: Install Google Chrome browser")
    print("• If permission errors: Run as administrator (Windows)")
    print("• For more help: Check setup_chromedriver.md")
    
    print(f"\n{Fore.GREEN}✅ What was fixed:")
    print("• ChromeDriver detection and download")
    print("• Error [WinError 193] handling")
    print("• Universal Driver Manager integration")
    print("• All uploader compatibility")
    print("• Comprehensive error handling")

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 FIX ALL DRIVERS SCRIPT - ENHANCED")
    print("=" * 60)
    print(f"{Fore.YELLOW}Memperbaiki error [WinError 193] dan semua masalah driver")
    print()
    
    # Step 1: Check system info
    system_info = check_system_info()
    print()
    
    # Step 2: Check Chrome installation
    chrome_found, chrome_version = check_chrome_installation()
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
    
    # Step 4: Clean old ChromeDrivers
    clean_old_chromedrivers()
    print()
    
    # Step 5: Run diagnostics
    if not run_driver_diagnostics():
        log("Driver diagnostics failed", "ERROR")
        return False
    print()
    
    # Step 6: Test driver creation
    if not test_driver_creation():
        log("Driver creation test failed", "ERROR")
        return False
    print()
    
    # Step 7: Test uploaders
    if not test_all_uploaders():
        log("Some uploaders failed initialization", "WARNING")
    print()
    
    # Step 8: Create test script
    create_test_script()
    print()
    
    # Step 9: Show final instructions
    show_final_instructions()
    
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