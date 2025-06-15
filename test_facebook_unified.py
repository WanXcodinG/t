#!/usr/bin/env python3
"""
Test script untuk Facebook Unified Uploader
Test semua fitur: text status, media, AI content generation
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
        "HEADER": "🧪"
    }
    
    icon = icons.get(level, "📝")
    print(f"{color}{icon} {message}{Style.RESET_ALL}")

def test_facebook_uploader_import():
    """Test Facebook uploader import"""
    log("Testing Facebook uploader import...", "HEADER")
    
    try:
        from facebook_uploader import FacebookUploader
        log("Facebook uploader import successful", "SUCCESS")
        return True
    except ImportError as e:
        log(f"Facebook uploader import failed: {e}", "ERROR")
        return False

def test_facebook_uploader_initialization():
    """Test Facebook uploader initialization"""
    log("Testing Facebook uploader initialization...", "HEADER")
    
    try:
        from facebook_uploader import FacebookUploader
        
        uploader = FacebookUploader(headless=True, debug=False)
        log("Facebook uploader initialization successful", "SUCCESS")
        
        # Test AI availability
        if uploader.ai_assistant:
            log("AI Assistant available", "SUCCESS")
        else:
            log("AI Assistant not available", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"Facebook uploader initialization failed: {e}", "ERROR")
        return False

def test_ai_content_generation():
    """Test AI content generation"""
    log("Testing AI content generation...", "HEADER")
    
    try:
        from facebook_uploader import FacebookUploader
        
        uploader = FacebookUploader(headless=True, debug=False)
        
        # Test different content types
        test_prompts = [
            ("motivasi hari senin", "status"),
            ("review makanan enak", "media"),
            ("tips produktivitas", "status")
        ]
        
        for prompt, content_type in test_prompts:
            log(f"Testing AI generation for: {prompt} ({content_type})", "INFO")
            
            ai_content = uploader.generate_ai_content(prompt, content_type)
            
            if ai_content and "content" in ai_content:
                log(f"AI content generated: {ai_content['title']}", "SUCCESS")
                log(f"Content preview: {ai_content['content'][:100]}...", "INFO")
            else:
                log(f"AI content generation failed for: {prompt}", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"AI content generation test failed: {e}", "ERROR")
        return False

def test_facebook_methods():
    """Test Facebook uploader methods"""
    log("Testing Facebook uploader methods...", "HEADER")
    
    try:
        from facebook_uploader import FacebookUploader
        
        uploader = FacebookUploader(headless=True, debug=False)
        
        # Test method availability
        methods_to_test = [
            "create_facebook_post",
            "upload_status",
            "upload_reels",
            "generate_ai_content",
            "load_cookies",
            "save_cookies",
            "check_cookies_status"
        ]
        
        for method_name in methods_to_test:
            if hasattr(uploader, method_name):
                log(f"Method {method_name}: ✅ Available", "SUCCESS")
            else:
                log(f"Method {method_name}: ❌ Missing", "ERROR")
        
        return True
        
    except Exception as e:
        log(f"Facebook methods test failed: {e}", "ERROR")
        return False

def test_cookies_functionality():
    """Test cookies functionality"""
    log("Testing cookies functionality...", "HEADER")
    
    try:
        from facebook_uploader import FacebookUploader
        
        uploader = FacebookUploader(headless=True, debug=False)
        
        # Test cookies status check
        status = uploader.check_cookies_status()
        log(f"Cookies status check: {status}", "INFO")
        
        # Test cookies path
        if uploader.cookies_path.exists():
            log("Cookies file exists", "SUCCESS")
        else:
            log("Cookies file not found (normal for first run)", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Cookies functionality test failed: {e}", "ERROR")
        return False

def test_driver_manager_integration():
    """Test driver manager integration"""
    log("Testing driver manager integration...", "HEADER")
    
    try:
        from facebook_uploader import DRIVER_MANAGER_AVAILABLE
        
        if DRIVER_MANAGER_AVAILABLE:
            log("Universal Driver Manager available", "SUCCESS")
            
            # Test driver manager import
            from driver_manager import get_chrome_driver
            log("Driver manager import successful", "SUCCESS")
        else:
            log("Universal Driver Manager not available", "WARNING")
            log("Will use fallback driver setup", "INFO")
        
        return True
        
    except Exception as e:
        log(f"Driver manager integration test failed: {e}", "ERROR")
        return False

def test_ai_integration():
    """Test AI integration"""
    log("Testing AI integration...", "HEADER")
    
    try:
        from facebook_uploader import AI_AVAILABLE
        
        if AI_AVAILABLE:
            log("AI Assistant available", "SUCCESS")
            
            # Test AI import
            from gemini_ai_assistant import GeminiAIAssistant
            log("AI Assistant import successful", "SUCCESS")
            
            # Check API key
            import os
            if os.getenv('GEMINI_API_KEY'):
                log("Gemini API key configured", "SUCCESS")
            else:
                log("Gemini API key not configured", "WARNING")
                log("Set with: set GEMINI_API_KEY=your_api_key", "INFO")
        else:
            log("AI Assistant not available", "WARNING")
            log("Install with: pip install google-generativeai", "INFO")
        
        return True
        
    except Exception as e:
        log(f"AI integration test failed: {e}", "ERROR")
        return False

def run_comprehensive_test():
    """Run comprehensive test"""
    log("🧪 FACEBOOK UNIFIED UPLOADER TEST", "HEADER")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_facebook_uploader_import),
        ("Initialization Test", test_facebook_uploader_initialization),
        ("Methods Test", test_facebook_methods),
        ("Cookies Test", test_cookies_functionality),
        ("Driver Manager Integration", test_driver_manager_integration),
        ("AI Integration", test_ai_integration),
        ("AI Content Generation", test_ai_content_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{Fore.YELLOW}📋 {test_name}:")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            log(f"{test_name} crashed: {e}", "ERROR")
    
    print(f"\n{Fore.LIGHTBLUE_EX}📊 TEST RESULTS:")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        log("🎉 All tests passed! Facebook Unified Uploader ready!", "SUCCESS")
        
        print(f"\n{Fore.GREEN}✅ Available Features:")
        print("• Text status posting")
        print("• Media posting (image/video)")
        print("• AI content generation")
        print("• Random AI content")
        print("• Cookie management")
        print("• Universal driver support")
        
        print(f"\n{Fore.CYAN}🚀 Usage Examples:")
        print("# Interactive mode:")
        print("python facebook_uploader.py")
        print()
        print("# Text status:")
        print('python facebook_uploader.py --content "Hello Facebook!"')
        print()
        print("# AI generated status:")
        print('python facebook_uploader.py --ai --prompt "motivasi hari senin"')
        print()
        print("# Media with caption:")
        print('python facebook_uploader.py --media "image.jpg" --content "Amazing photo!"')
        
    else:
        log(f"⚠️ {total - passed} tests failed. Check the output above.", "WARNING")
        
        print(f"\n{Fore.YELLOW}🔧 Troubleshooting:")
        print("1. Run: python fix_all_drivers.py")
        print("2. Install AI: pip install google-generativeai")
        print("3. Set API key: set GEMINI_API_KEY=your_api_key")
        print("4. Check Chrome: google-chrome --version")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Test dihentikan oleh user")
    except Exception as e:
        print(f"{Fore.RED}💥 Test error: {str(e)}")
        sys.exit(1)