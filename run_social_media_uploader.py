#!/usr/bin/env python3
"""
Run Social Media Uploader dengan error handling yang enhanced
Script wrapper untuk menjalankan social media uploader dengan safe mode
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
        "HEADER": "🚀"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def check_prerequisites():
    """Check prerequisites sebelum menjalankan uploader"""
    log("Checking prerequisites...", "HEADER")
    
    issues = []
    
    # Check Chrome
    try:
        from driver_manager import UniversalDriverManager
        manager = UniversalDriverManager()
        
        chrome_version = manager.get_chrome_version()
        if chrome_version:
            log(f"Chrome: ✅ {chrome_version}", "SUCCESS")
        else:
            log("Chrome: ❌ Not found", "ERROR")
            issues.append("Chrome browser not installed")
    except Exception as e:
        log(f"Chrome check failed: {e}", "ERROR")
        issues.append("Chrome detection error")
    
    # Check ChromeDriver
    try:
        from driver_manager import UniversalDriverManager
        manager = UniversalDriverManager()
        
        chromedriver_path = manager.get_chromedriver_path()
        if chromedriver_path:
            log("ChromeDriver: ✅ Available", "SUCCESS")
        else:
            log("ChromeDriver: ❌ Not found", "ERROR")
            issues.append("ChromeDriver not available")
    except Exception as e:
        log(f"ChromeDriver check failed: {e}", "ERROR")
        issues.append("ChromeDriver detection error")
    
    # Check Python packages
    required_packages = ["selenium", "colorama", "requests"]
    for package in required_packages:
        try:
            __import__(package)
            log(f"{package}: ✅ Installed", "SUCCESS")
        except ImportError:
            log(f"{package}: ❌ Missing", "ERROR")
            issues.append(f"Missing package: {package}")
    
    return issues

def fix_issues_automatically():
    """Try to fix issues automatically"""
    log("Attempting automatic fixes...", "HEADER")
    
    try:
        # Run fix all drivers
        log("Running fix_all_drivers.py...", "INFO")
        import subprocess
        result = subprocess.run([sys.executable, "fix_all_drivers.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log("Automatic fix completed successfully", "SUCCESS")
            return True
        else:
            log("Automatic fix failed", "ERROR")
            return False
            
    except Exception as e:
        log(f"Automatic fix error: {e}", "ERROR")
        return False

def run_social_media_uploader():
    """Run social media uploader dengan error handling"""
    log("Starting Social Media Uploader...", "HEADER")
    
    try:
        # Import and run
        from social_media_uploader import SocialMediaUploader
        
        # Detect environment
        is_headless = False
        if platform.system().lower() == "linux":
            is_headless = not os.environ.get("DISPLAY")
        
        log(f"Environment: {platform.system()}, Headless: {is_headless}", "INFO")
        
        # Create uploader instance
        uploader = SocialMediaUploader(debug=False)
        
        # Run interactive mode
        uploader.run_interactive()
        
        return True
        
    except ImportError as e:
        log(f"Import error: {e}", "ERROR")
        log("Some dependencies may be missing", "WARNING")
        return False
    except Exception as e:
        log(f"Runtime error: {e}", "ERROR")
        return False

def show_manual_instructions():
    """Show manual instructions jika automatic fix gagal"""
    print(f"\n{Fore.YELLOW}📋 MANUAL FIX INSTRUCTIONS:")
    print("=" * 50)
    
    print(f"\n{Fore.CYAN}1. Install Chrome Browser:")
    if platform.system().lower() == "windows":
        print("   • Download from: https://www.google.com/chrome/")
        print("   • Or run: python install_chrome_windows.py")
    else:
        print("   • Ubuntu: sudo apt install google-chrome-stable")
        print("   • Or run: python driver_manager.py --install-chrome")
    
    print(f"\n{Fore.CYAN}2. Install Python Dependencies:")
    print("   pip install -r requirements.txt")
    
    print(f"\n{Fore.CYAN}3. Setup API Keys (Optional):")
    print("   set GEMINI_API_KEY=your_gemini_api_key")
    
    print(f"\n{Fore.CYAN}4. Test Setup:")
    print("   python test_complete_system.py")
    
    print(f"\n{Fore.CYAN}5. Run Uploader:")
    print("   python social_media_uploader.py")

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🚀 SOCIAL MEDIA UPLOADER LAUNCHER")
    print("=" * 60)
    print(f"{Fore.YELLOW}Safe launcher dengan automatic error detection & fixing")
    print()
    
    # Step 1: Check prerequisites
    issues = check_prerequisites()
    
    if not issues:
        log("All prerequisites met! Starting uploader...", "SUCCESS")
        
        # Run uploader
        if run_social_media_uploader():
            log("Social Media Uploader completed successfully", "SUCCESS")
        else:
            log("Social Media Uploader encountered errors", "ERROR")
        
        return True
    
    # Step 2: Show issues
    log(f"Found {len(issues)} issues:", "WARNING")
    for issue in issues:
        print(f"  • {issue}")
    
    # Step 3: Ask for automatic fix
    print(f"\n{Fore.YELLOW}Would you like to try automatic fixes?")
    choice = input(f"{Fore.WHITE}Auto-fix issues? (Y/n): ").strip().lower()
    
    if choice != 'n':
        if fix_issues_automatically():
            log("Issues fixed! Checking again...", "SUCCESS")
            
            # Check again
            issues = check_prerequisites()
            if not issues:
                log("All issues resolved! Starting uploader...", "SUCCESS")
                
                if run_social_media_uploader():
                    log("Social Media Uploader completed successfully", "SUCCESS")
                    return True
                else:
                    log("Social Media Uploader encountered errors", "ERROR")
                    return False
            else:
                log("Some issues remain after automatic fix", "WARNING")
                show_manual_instructions()
                return False
        else:
            log("Automatic fix failed", "ERROR")
            show_manual_instructions()
            return False
    else:
        log("Automatic fix skipped", "INFO")
        show_manual_instructions()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print(f"\n{Fore.RED}❌ Setup incomplete")
            print(f"{Fore.YELLOW}Please follow the manual instructions above")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Launcher cancelled by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Launcher error: {str(e)}")
        sys.exit(1)