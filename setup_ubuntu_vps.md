# Setup Ubuntu VPS untuk Social Media Uploader

## 🐧 Complete Ubuntu VPS Setup Guide

Script ini sekarang **fully support** untuk Ubuntu VPS dengan deteksi otomatis dan instalasi Chrome yang seamless.

## 🚀 Quick Setup untuk Ubuntu VPS

### **Step 1: Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

### **Step 2: Install Python Dependencies**
```bash
# Install Python dan pip jika belum ada
sudo apt install -y python3 python3-pip

# Install requirements
pip3 install -r requirements.txt
```

### **Step 3: Auto-Install Chrome (Recommended)**
```bash
# Script akan otomatis install Chrome dan dependencies
python3 driver_manager.py --install-chrome
```

### **Step 4: Test Setup**
```bash
# Test driver setup
python3 driver_manager.py --test

# Test full system
python3 fix_all_drivers.py
```

### **Step 5: Run Social Media Uploader**
```bash
# Run main script
python3 social_media_uploader.py
```

## 🔧 Manual Chrome Installation (Alternative)

Jika auto-install gagal, install Chrome secara manual:

### **Method 1: Official Google Repository**
```bash
# Add Google signing key
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -

# Add Google Chrome repository
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'

# Update package list
sudo apt update

# Install Chrome
sudo apt install -y google-chrome-stable
```

### **Method 2: Direct Download**
```bash
# Download Chrome deb package
wget -O /tmp/google-chrome-stable.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install with dpkg
sudo dpkg -i /tmp/google-chrome-stable.deb

# Fix dependencies if needed
sudo apt install -f -y
```

### **Method 3: Snap Package**
```bash
sudo snap install chromium
```

## 📦 Install Chrome Dependencies

Chrome memerlukan dependencies tambahan untuk VPS headless:

```bash
# Essential packages
sudo apt install -y \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    gconf-service \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libgtk-3-0 \
    libxshmfence1

# Additional packages for stability
sudo apt install -y \
    xvfb \
    x11vnc \
    fluxbox \
    wget \
    unzip
```

## 🎯 VPS-Specific Features

### **Auto-Detection:**
- ✅ **VPS Environment Detection** - Otomatis detect VPS (OpenVZ, Xen, KVM, etc.)
- ✅ **Headless Mode** - Auto-enable headless mode untuk VPS
- ✅ **Ubuntu Distribution Detection** - Detect Ubuntu version dan variant
- ✅ **Architecture Detection** - Support x86_64 dan ARM64

### **Optimized Chrome Options untuk VPS:**
```python
# Options yang otomatis ditambahkan untuk Ubuntu VPS:
--headless=new
--no-sandbox
--disable-dev-shm-usage
--single-process          # Important untuk VPS
--no-zygote              # Important untuk VPS
--disable-setuid-sandbox
--disable-gpu
--disable-software-rasterizer
```

### **Memory Optimization:**
- ✅ **Single Process Mode** - Mengurangi memory usage
- ✅ **Disabled GPU** - Tidak perlu GPU acceleration
- ✅ **Optimized Flags** - Flags khusus untuk VPS environment

## 🔍 Diagnostics untuk Ubuntu VPS

### **Run Comprehensive Diagnostics:**
```bash
python3 driver_manager.py --diagnostics
```

**Output Example:**
```
🔍 DRIVER DIAGNOSTICS
==================================================

System Information:
OS: linux
Architecture: x86_64
Distribution: ubuntu
Is Ubuntu: True
Is VPS: True
Is Headless: True
DISPLAY: Not set

Chrome Browser:
✅ Chrome installed: 120.0.6099.109

ChromeDriver:
✅ ChromeDriver found: /home/user/drivers/chromedriver
✅ ChromeDriver working

Dependencies:
✅ Selenium: 4.16.0
✅ WebDriver Manager available
✅ Requests available

Ubuntu VPS Checks:
✅ libnss3: installed
✅ libgconf-2-4: installed
✅ libxss1: installed

Driver Test:
✅ Driver creation successful
✅ Navigation test successful
```

## 🐳 Docker Support

Untuk Docker containers, gunakan base image dengan Chrome pre-installed:

### **Dockerfile Example:**
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Run setup
RUN python3 fix_all_drivers.py

# Default command
CMD ["python3", "social_media_uploader.py"]
```

## 🔧 Troubleshooting Ubuntu VPS

### **Common Issues & Solutions:**

#### **1. Chrome not found**
```bash
# Check if Chrome is installed
google-chrome --version

# If not found, install:
python3 driver_manager.py --install-chrome
```

#### **2. ChromeDriver permission denied**
```bash
# Make ChromeDriver executable
chmod +x drivers/chromedriver

# Or for system-wide:
sudo chmod +x /usr/local/bin/chromedriver
```

#### **3. Display not found (DISPLAY variable)**
```bash
# This is normal for VPS - script auto-detects and uses headless mode
echo $DISPLAY  # Should be empty on VPS

# Force headless mode if needed:
export HEADLESS=true
```

#### **4. Memory issues on small VPS**
```bash
# Check memory usage
free -h

# Add swap if needed (for VPS with <2GB RAM):
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **5. Network/firewall issues**
```bash
# Check if ports are blocked
curl -I https://www.google.com

# Check DNS
nslookup google.com

# If behind firewall, may need proxy settings
```

#### **6. Dependencies missing**
```bash
# Install all Chrome dependencies
sudo apt install -y libnss3 libgconf-2-4 libxss1 libappindicator1 fonts-liberation

# Check what's missing:
ldd /usr/bin/google-chrome | grep "not found"
```

## 🎯 Performance Optimization untuk VPS

### **Memory Usage:**
- **Headless Mode**: Saves ~200MB RAM
- **Single Process**: Saves ~100MB RAM  
- **Disabled GPU**: Saves ~50MB RAM
- **Total Savings**: ~350MB RAM vs desktop mode

### **CPU Usage:**
- **Optimized Flags**: Reduced CPU usage
- **No Animations**: Faster page loads
- **Minimal Extensions**: Reduced overhead

### **Network Usage:**
- **Disabled Images**: Optional untuk save bandwidth
- **Compressed Responses**: Automatic
- **Connection Pooling**: Reuse connections

## 📊 VPS Requirements

### **Minimum Requirements:**
- **RAM**: 1GB (2GB recommended)
- **CPU**: 1 vCPU (2 vCPU recommended)
- **Storage**: 2GB free space
- **Network**: Stable internet connection
- **OS**: Ubuntu 18.04+ (20.04+ recommended)

### **Recommended VPS Specs:**
- **RAM**: 2-4GB
- **CPU**: 2 vCPU
- **Storage**: 5GB+ free space
- **Network**: 100Mbps+
- **OS**: Ubuntu 22.04 LTS

## 🚀 Quick Commands Reference

```bash
# Complete setup from scratch
curl -sSL https://raw.githubusercontent.com/your-repo/setup.sh | bash

# Or manual setup:
git clone your-repo
cd social-media-uploader
pip3 install -r requirements.txt
python3 driver_manager.py --install-chrome
python3 fix_all_drivers.py
python3 social_media_uploader.py

# Test everything
python3 driver_manager.py --test

# Run diagnostics
python3 driver_manager.py --diagnostics

# Check system status
python3 social_media_uploader.py
# Choose: System Status & Statistics
```

## 🎉 Success Indicators

Setelah setup berhasil, Anda akan melihat:

```
✅ Chrome installed: 120.0.6099.109
✅ ChromeDriver found: /home/user/drivers/chromedriver
✅ ChromeDriver working
✅ VPS environment detected
✅ Headless mode enabled
✅ Driver creation successful
✅ Navigation test successful
✅ All uploaders ready
```

## 🔒 Security Considerations

### **VPS Security:**
- ✅ **No GUI Access** - Headless mode lebih secure
- ✅ **Minimal Attack Surface** - Hanya essential packages
- ✅ **Process Isolation** - Chrome runs in sandbox
- ✅ **No Persistent Sessions** - Clean state setiap run

### **Recommended Security:**
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Setup firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

Dengan setup ini, social media uploader akan berjalan **perfectly** di Ubuntu VPS dengan **full automation** dan **optimal performance**! 🚀🐧✨