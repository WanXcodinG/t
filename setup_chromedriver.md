# Setup ChromeDriver untuk Social Media Uploader

## 🚗 Masalah ChromeDriver Error

Jika Anda mengalami error **[WinError 193] %1 is not a valid Win32 application**, ini biasanya disebabkan oleh masalah dengan ChromeDriver. Berikut cara mengatasinya:

## 🔧 Solusi 1: Install ChromeDriver Manual

### Windows:

1. **Download ChromeDriver**
   - Kunjungi: https://chromedriver.chromium.org/downloads
   - Pilih versi yang sesuai dengan Chrome browser Anda
   - Download file ZIP

2. **Extract dan Install**
   ```cmd
   # Extract ke folder yang mudah diakses
   C:\chromedriver\chromedriver.exe
   
   # Atau extract ke project folder
   your-project\chromedriver.exe
   ```

3. **Add to PATH (Recommended)**
   ```cmd
   # Buka Command Prompt sebagai Administrator
   setx /M PATH "%PATH%;C:\chromedriver"
   ```

4. **Test Installation**
   ```cmd
   chromedriver --version
   ```

### Linux:
```bash
# Download ChromeDriver
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
LATEST=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip

# Extract dan install
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Test
chromedriver --version
```

### macOS:
```bash
# Menggunakan Homebrew
brew install chromedriver

# Atau manual download
curl -O https://chromedriver.storage.googleapis.com/LATEST_RELEASE
LATEST=$(cat LATEST_RELEASE)
curl -O https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
sudo mv chromedriver /usr/local/bin/
```

## 🔧 Solusi 2: WebDriver Manager (Automatic)

WebDriver Manager akan otomatis download ChromeDriver yang sesuai:

```bash
# Install WebDriver Manager
pip install webdriver-manager

# Script akan otomatis download ChromeDriver saat pertama kali dijalankan
python social_media_uploader.py
```

## 🔧 Solusi 3: Check Chrome Browser Version

Pastikan Chrome browser terinstall dan versi ChromeDriver sesuai:

1. **Check Chrome Version**
   - Buka Chrome browser
   - Klik menu (3 titik) → Help → About Google Chrome
   - Catat versi Chrome (contoh: 120.0.6099.109)

2. **Download ChromeDriver yang Sesuai**
   - Kunjungi: https://chromedriver.chromium.org/downloads
   - Pilih versi yang sesuai dengan Chrome browser
   - Download dan extract

## 🔧 Solusi 4: Alternative Browser

Jika masih bermasalah, gunakan Firefox dengan GeckoDriver:

```bash
# Install GeckoDriver
pip install webdriver-manager

# Modify script untuk menggunakan Firefox
# (Akan ditambahkan support Firefox di update selanjutnya)
```

## 🔧 Troubleshooting

### Error: "chromedriver.exe is not a valid Win32 application"

**Penyebab:**
- ChromeDriver corrupt atau tidak compatible
- Versi ChromeDriver tidak sesuai dengan Chrome browser
- File ChromeDriver rusak

**Solusi:**
1. Delete ChromeDriver yang ada
2. Download ulang dari situs resmi
3. Pastikan versi sesuai dengan Chrome browser
4. Extract ulang dengan benar

### Error: "ChromeDriver not found in PATH"

**Solusi:**
```cmd
# Windows - Add to PATH
setx PATH "%PATH%;C:\path\to\chromedriver"

# Atau copy ke System32
copy chromedriver.exe C:\Windows\System32\

# Atau letakkan di project folder
copy chromedriver.exe your-project-folder\
```

### Error: "This version of ChromeDriver only supports Chrome version X"

**Solusi:**
1. Update Chrome browser ke versi terbaru
2. Download ChromeDriver yang sesuai dengan versi Chrome
3. Atau downgrade Chrome ke versi yang didukung ChromeDriver

### Error: "WebDriver Manager failed"

**Solusi:**
```bash
# Clear WebDriver Manager cache
rm -rf ~/.wdm

# Reinstall WebDriver Manager
pip uninstall webdriver-manager
pip install webdriver-manager

# Manual download jika internet bermasalah
# Download ChromeDriver manual dan letakkan di PATH
```

## 🎯 Verification

Setelah setup, test dengan script ini:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Test ChromeDriver
try:
    options = Options()
    options.add_argument('--headless')
    
    # Method 1: System ChromeDriver
    driver = webdriver.Chrome(options=options)
    print("✅ ChromeDriver working!")
    driver.quit()
    
except Exception as e:
    print(f"❌ ChromeDriver error: {e}")
    
    # Method 2: WebDriver Manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ WebDriver Manager working!")
        driver.quit()
    except Exception as e2:
        print(f"❌ WebDriver Manager error: {e2}")
```

## 📋 Quick Fix Commands

```bash
# Windows Quick Fix
# 1. Download ChromeDriver
curl -O https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# 2. Extract to project folder
# 3. Run script

# Linux Quick Fix
sudo apt update
sudo apt install chromium-chromedriver
ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver

# macOS Quick Fix
brew install chromedriver
```

## 🚀 Recommended Setup

Untuk hasil terbaik, gunakan kombinasi:

1. **Install Chrome browser** (versi terbaru)
2. **Install WebDriver Manager** (`pip install webdriver-manager`)
3. **Backup manual ChromeDriver** di project folder
4. **Script akan otomatis pilih** method yang tersedia

Dengan setup ini, script akan:
1. Coba ChromeDriver di PATH
2. Coba ChromeDriver di project folder
3. Coba WebDriver Manager (auto-download)
4. Tampilkan error yang jelas jika semua gagal

Script sudah diperbaiki untuk handle semua skenario ini! 🎉