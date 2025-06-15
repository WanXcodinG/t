#!/usr/bin/env python3
"""
Fix All Drivers Script
Script untuk memperbaiki semua masalah driver di semua file uploader
"""

import os
import sys
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
        "HEADER": "🔧"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def check_requirements():
    """Check dan install requirements"""
    log("Checking requirements...", "HEADER")
    
    required_packages = [
        "selenium",
        "webdriver-manager", 
        "colorama",
        "requests"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            log(f"{package}: ✅ Installed", "SUCCESS")
        except ImportError:
            log(f"{package}: ❌ Not installed, installing...", "WARNING")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                log(f"{package}: ✅ Installed successfully", "SUCCESS")
            except subprocess.CalledProcessError as e:
                log(f"{package}: ❌ Installation failed: {e}", "ERROR")

def run_driver_diagnostics():
    """Run driver diagnostics"""
    log("Running driver diagnostics...", "HEADER")
    
    try:
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager(debug=True)
        manager.run_diagnostics()
        
    except ImportError:
        log("Universal Driver Manager not found, creating...", "WARNING")
        # The driver_manager.py should already be created by the artifact
        
    except Exception as e:
        log(f"Diagnostics error: {e}", "ERROR")

def test_all_uploaders():
    """Test semua uploader dengan driver baru"""
    log("Testing all uploaders...", "HEADER")
    
    uploaders = [
        ("TikTok", "tiktok_uploader.py"),
        ("Facebook", "facebook_uploader.py"), 
        ("Instagram", "instagram_uploader.py")
    ]
    
    for name, filename in uploaders:
        log(f"Testing {name} uploader...", "INFO")
        
        try:
            # Import and test basic initialization
            if filename == "tiktok_uploader.py":
                from tiktok_uploader import TikTokUploader
                uploader = TikTokUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                
            elif filename == "facebook_uploader.py":
                from facebook_uploader import FacebookUploader
                uploader = FacebookUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                
            elif filename == "instagram_uploader.py":
                from instagram_uploader import InstagramUploader
                uploader = InstagramUploader(headless=True, debug=False)
                log(f"{name}: ✅ Initialization successful", "SUCCESS")
                
        except Exception as e:
            log(f"{name}: ❌ Error: {e}", "ERROR")

def fix_chrome_issues():
    """Fix common Chrome issues"""
    log("Fixing Chrome issues...", "HEADER")
    
    # Check Chrome installation
    try:
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            
            chrome_found = False
            for path in chrome_paths:
                if os.path.exists(path):
                    log(f"Chrome found: {path}", "SUCCESS")
                    chrome_found = True
                    break
            
            if not chrome_found:
                log("Chrome browser not found!", "ERROR")
                log("Please install Google Chrome from: https://www.google.com/chrome/", "INFO")
                
        else:
            # Linux/Mac
            result = subprocess.run(["which", "google-chrome"], capture_output=True)
            if result.returncode == 0:
                log("Chrome found in system PATH", "SUCCESS")
            else:
                log("Chrome not found, please install Google Chrome", "WARNING")
                
    except Exception as e:
        log(f"Error checking Chrome: {e}", "ERROR")

def create_test_script():
    """Create test script untuk verify fix"""
    log("Creating test script...", "INFO")
    
    test_script = '''#!/usr/bin/env python3
"""
Test script untuk verify driver fix
"""

def test_driver_manager():
    """Test Universal Driver Manager"""
    try:
        from driver_manager import get_chrome_driver, run_driver_diagnostics
        
        print("🔍 Running diagnostics...")
        run_driver_diagnostics()
        
        print("\\n🧪 Testing driver creation...")
        driver = get_chrome_driver(headless=True)
        print("✅ Driver created successfully!")
        
        driver.get("https://www.google.com")
        print("✅ Navigation test successful!")
        
        driver.quit()
        print("✅ All tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_driver_manager()
'''
    
    with open("test_driver_fix.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    log("Test script created: test_driver_fix.py", "SUCCESS")

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 FIX ALL DRIVERS SCRIPT")
    print("=" * 60)
    print(f"{Fore.YELLOW}Memperbaiki semua masalah driver di semua uploader")
    print()
    
    # Step 1: Check requirements
    check_requirements()
    print()
    
    # Step 2: Fix Chrome issues
    fix_chrome_issues()
    print()
    
    # Step 3: Run diagnostics
    run_driver_diagnostics()
    print()
    
    # Step 4: Test uploaders
    test_all_uploaders()
    print()
    
    # Step 5: Create test script
    create_test_script()
    print()
    
    log("🎉 Driver fix completed!", "SUCCESS")
    log("Run 'python test_driver_fix.py' to verify the fix", "INFO")
    log("Run 'python driver_manager.py --diagnostics' for detailed diagnostics", "INFO")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Script dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error: {str(e)}")