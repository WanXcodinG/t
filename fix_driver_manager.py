#!/usr/bin/env python3
"""
Fix Driver Manager Issues - ENHANCED VERSION
Memperbaiki masalah 'UniversalDriverManager' object has no attribute 'is_ubuntu'
dan compatibility issues lainnya
"""

import os
import sys
import shutil
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

def backup_file(file_path: str) -> str:
    """Create backup of file"""
    backup_path = f"{file_path}.backup"
    try:
        shutil.copy2(file_path, backup_path)
        log(f"Backup created: {backup_path}", "INFO")
        return backup_path
    except Exception as e:
        log(f"Failed to create backup: {e}", "WARNING")
        return None

def fix_driver_manager():
    """Fix driver manager compatibility issues"""
    log("Fixing driver manager compatibility issues...", "HEADER")
    
    try:
        # Check if driver_manager.py exists
        if not os.path.exists("driver_manager.py"):
            log("driver_manager.py not found", "ERROR")
            return False
        
        # Create backup
        backup_file("driver_manager.py")
        
        # Read current content
        with open("driver_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if fix is already applied
        if "self.is_ubuntu = \"ubuntu\" in self.distro.lower()" in content:
            log("Driver manager already fixed", "SUCCESS")
            return True
        
        # Apply multiple fixes
        fixes_applied = 0
        
        # Fix 1: Add is_ubuntu attribute
        if "self.distro = self._detect_linux_distro()" in content and "self.is_ubuntu" not in content:
            content = content.replace(
                "self.distro = self._detect_linux_distro()",
                "self.distro = self._detect_linux_distro()\n            self.is_ubuntu = \"ubuntu\" in self.distro.lower()"
            )
            fixes_applied += 1
            log("Fix 1: Added is_ubuntu attribute", "SUCCESS")
        
        # Fix 2: Add is_headless attribute if missing
        if "elif self.system == \"linux\":" in content and "self.is_headless = self._detect_headless_environment()" not in content:
            content = content.replace(
                "self.is_ubuntu = \"ubuntu\" in self.distro.lower()",
                "self.is_ubuntu = \"ubuntu\" in self.distro.lower()\n            self.is_headless = self._detect_headless_environment()"
            )
            fixes_applied += 1
            log("Fix 2: Added is_headless attribute", "SUCCESS")
        
        # Fix 3: Ensure _detect_headless_environment method exists
        if "_detect_headless_environment" not in content:
            # Add the method after _detect_linux_distro
            headless_method = '''
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
'''
            
            # Find insertion point after _detect_linux_distro method
            if "def _detect_linux_distro(self) -> str:" in content:
                # Find the end of _detect_linux_distro method
                lines = content.split('\n')
                in_method = False
                insert_index = -1
                
                for i, line in enumerate(lines):
                    if "def _detect_linux_distro(self) -> str:" in line:
                        in_method = True
                    elif in_method and line.strip() and not line.startswith('        ') and not line.startswith('\t'):
                        # Found end of method
                        insert_index = i
                        break
                
                if insert_index > 0:
                    lines.insert(insert_index, headless_method)
                    content = '\n'.join(lines)
                    fixes_applied += 1
                    log("Fix 3: Added _detect_headless_environment method", "SUCCESS")
        
        # Write fixed content if any fixes were applied
        if fixes_applied > 0:
            with open("driver_manager.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            log(f"Driver manager fixed: {fixes_applied} fixes applied", "SUCCESS")
            return True
        else:
            log("No fixes needed or could not apply fixes", "INFO")
            return True
            
    except Exception as e:
        log(f"Error fixing driver manager: {e}", "ERROR")
        return False

def fix_youtube_uploader():
    """Fix YouTube uploader parameter issue"""
    log("Fixing YouTube uploader parameter issue...", "HEADER")
    
    try:
        if not os.path.exists("youtube_api_uploader.py"):
            log("youtube_api_uploader.py not found", "WARNING")
            return True
        
        # Create backup
        backup_file("youtube_api_uploader.py")
        
        # Read current content
        with open("youtube_api_uploader.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if fix is already applied
        if "def __init__(self, debug: bool = False):" in content:
            log("YouTube uploader already fixed", "SUCCESS")
            return True
        
        # Fix: Remove headless parameter from __init__
        if "def __init__(self, headless: bool = False, debug: bool = False):" in content:
            content = content.replace(
                "def __init__(self, headless: bool = False, debug: bool = False):",
                "def __init__(self, debug: bool = False):"
            )
            
            # Remove headless assignment
            content = content.replace(
                "self.headless = headless\n        self.debug = debug",
                "self.debug = debug"
            )
            
            # Write fixed content
            with open("youtube_api_uploader.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            log("YouTube uploader fixed: removed headless parameter", "SUCCESS")
            return True
        else:
            log("YouTube uploader doesn't need fixing", "INFO")
            return True
            
    except Exception as e:
        log(f"Error fixing YouTube uploader: {e}", "ERROR")
        return False

def fix_social_media_uploader():
    """Fix social media uploader initialization"""
    log("Fixing social media uploader initialization...", "HEADER")
    
    try:
        if not os.path.exists("social_media_uploader.py"):
            log("social_media_uploader.py not found", "ERROR")
            return False
        
        # Create backup
        backup_file("social_media_uploader.py")
        
        # Read current content
        with open("social_media_uploader.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Fix: YouTube uploader initialization without headless parameter
        if "self.youtube_uploader = YouTubeAPIUploader(headless=headless, debug=debug)" in content:
            content = content.replace(
                "self.youtube_uploader = YouTubeAPIUploader(headless=headless, debug=debug)",
                "self.youtube_uploader = YouTubeAPIUploader(debug=debug)"
            )
            
            # Write fixed content
            with open("social_media_uploader.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            log("Social media uploader fixed: YouTube initialization", "SUCCESS")
            return True
        else:
            log("Social media uploader doesn't need fixing", "INFO")
            return True
            
    except Exception as e:
        log(f"Error fixing social media uploader: {e}", "ERROR")
        return False

def test_driver_manager():
    """Test driver manager after fix"""
    log("Testing driver manager...", "HEADER")
    
    try:
        # Clear import cache
        if 'driver_manager' in sys.modules:
            del sys.modules['driver_manager']
        
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager()
        
        # Test attributes
        required_attrs = ['is_ubuntu', 'distro', 'system', 'architecture']
        for attr in required_attrs:
            if hasattr(manager, attr):
                value = getattr(manager, attr)
                log(f"{attr} attribute: ✅ {value}", "SUCCESS")
            else:
                log(f"{attr} attribute: ❌ Missing", "ERROR")
                return False
        
        # Test methods
        try:
            chrome_version = manager.get_chrome_version()
            if chrome_version:
                log(f"Chrome detection: ✅ {chrome_version}", "SUCCESS")
            else:
                log("Chrome detection: ⚠️ Chrome not found", "WARNING")
        except Exception as e:
            log(f"Chrome detection: ⚠️ {e}", "WARNING")
        
        log("Driver manager test completed", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Driver manager test failed: {e}", "ERROR")
        return False

def test_youtube_uploader():
    """Test YouTube uploader after fix"""
    log("Testing YouTube uploader...", "HEADER")
    
    try:
        # Clear import cache
        if 'youtube_api_uploader' in sys.modules:
            del sys.modules['youtube_api_uploader']
        
        from youtube_api_uploader import YouTubeAPIUploader
        
        # Test initialization without headless parameter
        uploader = YouTubeAPIUploader(debug=False)
        log("YouTube uploader initialization: ✅ Success", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"YouTube uploader test failed: {e}", "ERROR")
        return False

def test_social_media_uploader():
    """Test social media uploader after fix"""
    log("Testing social media uploader...", "HEADER")
    
    try:
        # Clear import cache
        if 'social_media_uploader' in sys.modules:
            del sys.modules['social_media_uploader']
        
        from social_media_uploader import SocialMediaUploader
        
        uploader = SocialMediaUploader(debug=False)
        log("Social media uploader initialization: ✅ Success", "SUCCESS")
        
        # Test components
        components = {
            "YouTube Uploader": uploader.youtube_uploader,
            "TikTok Uploader": uploader.tiktok_uploader,
            "Facebook Uploader": uploader.facebook_uploader,
            "Instagram Uploader": uploader.instagram_uploader
        }
        
        for name, component in components.items():
            if component:
                log(f"{name}: ✅ Available", "SUCCESS")
            else:
                log(f"{name}: ❌ Not available", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"Social media uploader test failed: {e}", "ERROR")
        return False

def restore_backups():
    """Restore backups if fixes fail"""
    log("Restoring backups...", "WARNING")
    
    backup_files = [
        "driver_manager.py.backup",
        "youtube_api_uploader.py.backup",
        "social_media_uploader.py.backup"
    ]
    
    for backup_file in backup_files:
        if os.path.exists(backup_file):
            original_file = backup_file.replace(".backup", "")
            try:
                shutil.copy2(backup_file, original_file)
                log(f"Restored: {original_file}", "INFO")
            except Exception as e:
                log(f"Failed to restore {original_file}: {e}", "ERROR")

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 Fix Driver Manager Issues - ENHANCED")
    print("=" * 60)
    print(f"{Fore.YELLOW}Fixing compatibility issues in all uploader files")
    print()
    
    all_success = True
    
    # Step 1: Fix driver manager
    if fix_driver_manager():
        log("Driver manager fix applied", "SUCCESS")
    else:
        log("Driver manager fix failed", "ERROR")
        all_success = False
    
    # Step 2: Fix YouTube uploader
    if fix_youtube_uploader():
        log("YouTube uploader fix applied", "SUCCESS")
    else:
        log("YouTube uploader fix failed", "ERROR")
        all_success = False
    
    # Step 3: Fix social media uploader
    if fix_social_media_uploader():
        log("Social media uploader fix applied", "SUCCESS")
    else:
        log("Social media uploader fix failed", "ERROR")
        all_success = False
    
    if not all_success:
        log("Some fixes failed, restoring backups...", "ERROR")
        restore_backups()
        return False
    
    # Step 4: Test all components
    print(f"\n{Fore.CYAN}🧪 Testing fixed components...")
    
    test_results = []
    
    # Test driver manager
    test_results.append(("Driver Manager", test_driver_manager()))
    
    # Test YouTube uploader
    test_results.append(("YouTube Uploader", test_youtube_uploader()))
    
    # Test social media uploader
    test_results.append(("Social Media Uploader", test_social_media_uploader()))
    
    # Show results
    print(f"\n{Fore.LIGHTBLUE_EX}📊 TEST RESULTS:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = Fore.GREEN if result else Fore.RED
        print(f"{color}{test_name}: {status}")
        if result:
            passed += 1
    
    if passed == len(test_results):
        print(f"\n{Fore.GREEN}🎉 All fixes applied successfully!")
        print(f"\n{Fore.CYAN}You can now run:")
        print("python test_complete_system.py")
        print("python social_media_uploader.py")
        
        # Clean up backup files
        for backup_file in ["driver_manager.py.backup", "youtube_api_uploader.py.backup", "social_media_uploader.py.backup"]:
            if os.path.exists(backup_file):
                try:
                    os.remove(backup_file)
                except:
                    pass
        
        return True
    else:
        log(f"Some tests failed ({passed}/{len(test_results)} passed)", "ERROR")
        log("Restoring backups...", "WARNING")
        restore_backups()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print(f"\n{Fore.RED}❌ Fix failed")
            print(f"{Fore.YELLOW}Try running: python fix_all_drivers.py")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Fix cancelled by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error: {str(e)}")
        sys.exit(1)