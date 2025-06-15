#!/usr/bin/env python3
"""
Fix Driver Manager Issues
Memperbaiki masalah 'UniversalDriverManager' object has no attribute 'is_ubuntu'
"""

import os
import sys
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

def fix_driver_manager():
    """Fix driver manager compatibility issues"""
    log("Fixing driver manager compatibility issues...", "HEADER")
    
    try:
        # Check if driver_manager.py exists
        if not os.path.exists("driver_manager.py"):
            log("driver_manager.py not found", "ERROR")
            return False
        
        # Read current content
        with open("driver_manager.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if fix is already applied
        if "self.is_ubuntu = \"ubuntu\" in self.distro.lower()" in content:
            log("Driver manager already fixed", "SUCCESS")
            return True
        
        # Apply fix for is_ubuntu attribute
        if "self.distro = self._detect_linux_distro()" in content:
            # Add is_ubuntu attribute after distro detection
            content = content.replace(
                "self.distro = self._detect_linux_distro()",
                "self.distro = self._detect_linux_distro()\n            self.is_ubuntu = \"ubuntu\" in self.distro.lower()"
            )
            
            # Write fixed content
            with open("driver_manager.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            log("Driver manager fixed successfully", "SUCCESS")
            return True
        else:
            log("Could not find location to apply fix", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error fixing driver manager: {e}", "ERROR")
        return False

def test_driver_manager():
    """Test driver manager after fix"""
    log("Testing driver manager...", "HEADER")
    
    try:
        from driver_manager import UniversalDriverManager
        
        manager = UniversalDriverManager()
        
        # Test attributes
        if hasattr(manager, 'is_ubuntu'):
            log("is_ubuntu attribute: ✅ Available", "SUCCESS")
        else:
            log("is_ubuntu attribute: ❌ Missing", "ERROR")
            return False
        
        if hasattr(manager, 'distro'):
            log(f"distro attribute: ✅ {manager.distro}", "SUCCESS")
        else:
            log("distro attribute: ❌ Missing", "ERROR")
            return False
        
        # Test methods
        try:
            chrome_version = manager.get_chrome_version()
            log(f"Chrome detection: ✅ Working", "SUCCESS")
        except Exception as e:
            log(f"Chrome detection: ⚠️ {e}", "WARNING")
        
        log("Driver manager test completed", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"Driver manager test failed: {e}", "ERROR")
        return False

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 Fix Driver Manager Issues")
    print("=" * 50)
    
    # Step 1: Fix driver manager
    if fix_driver_manager():
        log("Driver manager fix applied", "SUCCESS")
    else:
        log("Driver manager fix failed", "ERROR")
        return False
    
    # Step 2: Test driver manager
    if test_driver_manager():
        log("Driver manager working correctly", "SUCCESS")
        
        print(f"\n{Fore.GREEN}🎉 Driver manager fixed successfully!")
        print(f"\n{Fore.CYAN}You can now run:")
        print("python test_complete_system.py")
        print("python social_media_uploader.py")
        
        return True
    else:
        log("Driver manager still has issues", "ERROR")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Fix cancelled by user")
    except Exception as e:
        print(f"{Fore.RED}💥 Error: {str(e)}")
        sys.exit(1)