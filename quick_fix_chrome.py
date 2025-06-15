#!/usr/bin/env python3
"""
Quick Fix untuk Chrome Detection Issue
Memperbaiki masalah Chrome tidak terdeteksi di Windows
"""

import os
import sys
import subprocess
import winreg
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

def check_chrome_registry():
    """Check Chrome in Windows Registry"""
    log("Checking Chrome in Windows Registry...", "HEADER")
    
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Google\Chrome\BLBeacon"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\BLBeacon"),
    ]
    
    for hkey, path in registry_paths:
        try:
            with winreg.OpenKey(hkey, path) as key:
                try:
                    version = winreg.QueryValueEx(key, "version")[0]
                    log(f"Chrome found in registry: {version}", "SUCCESS")
                    return True, version
                except:
                    try:
                        chrome_path = winreg.QueryValueEx(key, "")[0]
                        log(f"Chrome path in registry: {chrome_path}", "SUCCESS")
                        return True, "Unknown version"
                    except:
                        pass
        except:
            continue
    
    log("Chrome not found in registry", "WARNING")
    return False, None

def find_chrome_executable():
    """Find Chrome executable in common locations"""
    log("Searching for Chrome executable...", "HEADER")
    
    # Common Chrome installation paths
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Users\Public\Desktop\Google Chrome.lnk",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk"
    ]
    
    # Add user-specific paths
    username = os.getenv('USERNAME', '')
    if username:
        chrome_paths.extend([
            f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
            f"C:\\Users\\{username}\\Desktop\\Google Chrome.lnk",
            f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Google Chrome.lnk"
        ])
    
    found_paths = []
    
    for path in chrome_paths:
        if os.path.exists(path):
            log(f"Found: {path}", "SUCCESS")
            found_paths.append(path)
            
            # Try to get version if it's an executable
            if path.endswith('.exe'):
                try:
                    result = subprocess.run([path, "--version"], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        import re
                        version_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)
                        if version_match:
                            version = version_match.group(1)
                            log(f"Version: {version}", "INFO")
                except:
                    log(f"Could not get version from {path}", "WARNING")
    
    if found_paths:
        log(f"Found {len(found_paths)} Chrome installations", "SUCCESS")
        return True, found_paths
    else:
        log("No Chrome installations found", "ERROR")
        return False, []

def check_chrome_in_path():
    """Check if Chrome is in system PATH"""
    log("Checking Chrome in system PATH...", "HEADER")
    
    try:
        result = subprocess.run(["chrome", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log("Chrome found in PATH", "SUCCESS")
            log(f"Output: {result.stdout.strip()}", "INFO")
            return True
    except:
        pass
    
    try:
        result = subprocess.run(["google-chrome", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log("Chrome found in PATH (google-chrome)", "SUCCESS")
            log(f"Output: {result.stdout.strip()}", "INFO")
            return True
    except:
        pass
    
    log("Chrome not found in PATH", "WARNING")
    return False

def add_chrome_to_path():
    """Add Chrome to system PATH"""
    log("Attempting to add Chrome to PATH...", "HEADER")
    
    # Find Chrome executable
    found, paths = find_chrome_executable()
    
    if not found:
        log("Cannot add Chrome to PATH - Chrome not found", "ERROR")
        return False
    
    # Get the first executable path
    chrome_exe = None
    for path in paths:
        if path.endswith('.exe') and os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        log("No Chrome executable found", "ERROR")
        return False
    
    # Get Chrome directory
    chrome_dir = os.path.dirname(chrome_exe)
    
    try:
        # Get current PATH
        current_path = os.environ.get('PATH', '')
        
        # Check if Chrome directory is already in PATH
        if chrome_dir.lower() in current_path.lower():
            log("Chrome directory already in PATH", "INFO")
            return True
        
        # Add Chrome directory to PATH
        new_path = f"{current_path};{chrome_dir}"
        
        # Set PATH for current session
        os.environ['PATH'] = new_path
        
        # Try to set permanent PATH (requires admin rights)
        try:
            subprocess.run([
                "setx", "PATH", new_path
            ], check=True, capture_output=True)
            log(f"Chrome directory added to PATH: {chrome_dir}", "SUCCESS")
            log("PATH updated permanently", "SUCCESS")
        except:
            log(f"Chrome directory added to PATH for current session: {chrome_dir}", "SUCCESS")
            log("Could not update PATH permanently (requires admin rights)", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"Failed to add Chrome to PATH: {e}", "ERROR")
        return False

def create_chrome_symlink():
    """Create chrome.exe symlink in project directory"""
    log("Creating Chrome symlink in project directory...", "HEADER")
    
    # Find Chrome executable
    found, paths = find_chrome_executable()
    
    if not found:
        log("Cannot create symlink - Chrome not found", "ERROR")
        return False
    
    # Get the first executable path
    chrome_exe = None
    for path in paths:
        if path.endswith('.exe') and os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        log("No Chrome executable found", "ERROR")
        return False
    
    try:
        # Create symlink in current directory
        symlink_path = "chrome.exe"
        
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        
        # Try to create symlink (requires admin rights on Windows)
        try:
            os.symlink(chrome_exe, symlink_path)
            log(f"Chrome symlink created: {symlink_path}", "SUCCESS")
        except OSError:
            # Fallback: copy the executable
            import shutil
            shutil.copy2(chrome_exe, symlink_path)
            log(f"Chrome executable copied: {symlink_path}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"Failed to create Chrome symlink: {e}", "ERROR")
        return False

def update_driver_manager():
    """Update driver manager dengan Chrome path yang ditemukan"""
    log("Updating driver manager with Chrome path...", "HEADER")
    
    # Find Chrome executable
    found, paths = find_chrome_executable()
    
    if not found:
        log("Cannot update driver manager - Chrome not found", "ERROR")
        return False
    
    # Get the first executable path
    chrome_exe = None
    for path in paths:
        if path.endswith('.exe') and os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        log("No Chrome executable found", "ERROR")
        return False
    
    try:
        # Create a config file with Chrome path
        config = {
            "chrome_path": chrome_exe,
            "chrome_dir": os.path.dirname(chrome_exe)
        }
        
        import json
        with open("chrome_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        log(f"Chrome config saved: chrome_config.json", "SUCCESS")
        log(f"Chrome path: {chrome_exe}", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Failed to update driver manager: {e}", "ERROR")
        return False

def test_chrome_detection():
    """Test Chrome detection after fixes"""
    log("Testing Chrome detection...", "HEADER")
    
    # Test 1: Registry check
    reg_found, reg_version = check_chrome_registry()
    
    # Test 2: File system check
    file_found, file_paths = find_chrome_executable()
    
    # Test 3: PATH check
    path_found = check_chrome_in_path()
    
    # Test 4: Try to run Chrome
    chrome_working = False
    try:
        # Try different Chrome commands
        commands = ["chrome", "google-chrome"]
        
        # Add Chrome from found paths
        if file_found:
            for path in file_paths:
                if path.endswith('.exe'):
                    commands.append(path)
        
        for cmd in commands:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    log(f"Chrome working with command: {cmd}", "SUCCESS")
                    log(f"Version: {result.stdout.strip()}", "INFO")
                    chrome_working = True
                    break
            except:
                continue
    except:
        pass
    
    # Summary
    print(f"\n{Fore.LIGHTBLUE_EX}📊 CHROME DETECTION SUMMARY:")
    print("=" * 40)
    print(f"Registry: {'✅' if reg_found else '❌'}")
    print(f"File System: {'✅' if file_found else '❌'}")
    print(f"PATH: {'✅' if path_found else '❌'}")
    print(f"Working: {'✅' if chrome_working else '❌'}")
    
    if chrome_working:
        log("Chrome detection successful!", "SUCCESS")
        return True
    else:
        log("Chrome detection still failing", "ERROR")
        return False

def main():
    """Main function"""
    print(f"\n{Fore.LIGHTBLUE_EX}🔧 Quick Fix untuk Chrome Detection")
    print("=" * 50)
    
    log("Diagnosing Chrome detection issue...", "INFO")
    
    # Step 1: Initial detection test
    if test_chrome_detection():
        log("Chrome is already working! No fix needed.", "SUCCESS")
        return True
    
    print(f"\n{Fore.YELLOW}Applying fixes...")
    
    # Step 2: Try to add Chrome to PATH
    log("Fix 1: Adding Chrome to PATH...", "INFO")
    add_chrome_to_path()
    
    # Step 3: Create symlink
    log("Fix 2: Creating Chrome symlink...", "INFO")
    create_chrome_symlink()
    
    # Step 4: Update driver manager
    log("Fix 3: Updating driver manager...", "INFO")
    update_driver_manager()
    
    # Step 5: Test again
    print(f"\n{Fore.CYAN}Testing fixes...")
    if test_chrome_detection():
        log("Chrome detection fixed successfully!", "SUCCESS")
        
        print(f"\n{Fore.GREEN}🎉 Chrome detection berhasil diperbaiki!")
        print(f"\n{Fore.YELLOW}Next steps:")
        print("1. python social_media_uploader.py")
        print("2. python fix_all_drivers.py")
        
        return True
    else:
        log("Chrome detection still not working", "ERROR")
        
        print(f"\n{Fore.RED}❌ Chrome detection masih bermasalah")
        print(f"\n{Fore.YELLOW}Manual solutions:")
        print("1. Install Chrome: python install_chrome_windows.py")
        print("2. Download from: https://www.google.com/chrome/")
        print("3. Restart terminal after installation")
        
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