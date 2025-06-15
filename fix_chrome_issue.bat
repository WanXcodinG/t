@echo off
echo 🔧 Quick Fix untuk Chrome Detection Issue
echo ================================================

echo.
echo ℹ️ Checking Chrome installation...

REM Check if Chrome is installed in common locations
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome found: C:\Program Files\Google\Chrome\Application\chrome.exe
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
    goto :found_chrome
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome found: C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    goto :found_chrome
)

if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome found: %LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
    set CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
    goto :found_chrome
)

echo ❌ Chrome not found in common locations
echo.
echo 📥 Would you like to download and install Chrome?
echo 1. Yes - Download and install Chrome automatically
echo 2. No - I'll install Chrome manually
echo.
set /p choice="Choose (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo 📥 Downloading Chrome installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://dl.google.com/chrome/install/latest/chrome_installer.exe' -OutFile 'chrome_installer.exe'"
    
    if exist "chrome_installer.exe" (
        echo ✅ Chrome installer downloaded
        echo.
        echo 🔧 Installing Chrome...
        chrome_installer.exe /silent /install
        
        echo ⏳ Waiting for installation to complete...
        timeout /t 30 /nobreak >nul
        
        echo 🧹 Cleaning up installer...
        del chrome_installer.exe
        
        echo.
        echo ✅ Chrome installation completed!
        echo Please restart this script to continue.
        pause
        exit /b 0
    ) else (
        echo ❌ Failed to download Chrome installer
        goto :manual_install
    )
) else (
    goto :manual_install
)

:manual_install
echo.
echo 📋 Manual installation steps:
echo 1. Visit: https://www.google.com/chrome/
echo 2. Download and install Chrome
echo 3. Restart this script
echo.
pause
exit /b 1

:found_chrome
echo.
echo 🔧 Adding Chrome to PATH...

REM Get Chrome directory
for %%i in ("%CHROME_PATH%") do set CHROME_DIR=%%~dpi

REM Check if Chrome directory is already in PATH
echo %PATH% | find /i "%CHROME_DIR%" >nul
if %errorlevel%==0 (
    echo ✅ Chrome directory already in PATH
) else (
    echo ℹ️ Adding Chrome directory to PATH: %CHROME_DIR%
    setx PATH "%PATH%;%CHROME_DIR%" >nul
    set PATH=%PATH%;%CHROME_DIR%
    echo ✅ Chrome directory added to PATH
)

echo.
echo 🔗 Creating Chrome symlink in project directory...
if exist "chrome.exe" del "chrome.exe"
copy "%CHROME_PATH%" "chrome.exe" >nul
if exist "chrome.exe" (
    echo ✅ Chrome executable copied to project directory
) else (
    echo ⚠️ Could not copy Chrome executable
)

echo.
echo 🧪 Testing Chrome detection...
"%CHROME_PATH%" --version >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Chrome is working!
    "%CHROME_PATH%" --version
) else (
    echo ❌ Chrome test failed
)

echo.
echo 🚀 Running Python fix script...
python quick_fix_chrome.py

echo.
echo 🎉 Chrome detection fix completed!
echo.
echo 📋 Next steps:
echo 1. python social_media_uploader.py
echo 2. python fix_all_drivers.py
echo.
pause