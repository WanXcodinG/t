#!/bin/bash
# Ubuntu VPS Installer untuk Social Media Uploader
# Complete setup script untuk Ubuntu VPS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "${BLUE}🔧 $1${NC}"
    echo "=================================================="
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Exiting..."
            exit 1
        fi
    fi
}

# Detect Ubuntu version
detect_ubuntu() {
    log_header "Detecting Ubuntu Version"
    
    if [[ ! -f /etc/os-release ]]; then
        log_error "Cannot detect OS. This script is for Ubuntu only."
        exit 1
    fi
    
    source /etc/os-release
    
    if [[ "$ID" != "ubuntu" ]]; then
        log_error "This script is designed for Ubuntu. Detected: $ID"
        exit 1
    fi
    
    log_success "Ubuntu $VERSION_ID detected"
    
    # Check if supported version
    case $VERSION_ID in
        "18.04"|"20.04"|"22.04"|"24.04")
            log_success "Supported Ubuntu version: $VERSION_ID"
            ;;
        *)
            log_warning "Ubuntu $VERSION_ID may not be fully tested"
            ;;
    esac
}

# Update system
update_system() {
    log_header "Updating System"
    
    log_info "Updating package lists..."
    sudo apt update
    
    log_info "Upgrading packages..."
    sudo apt upgrade -y
    
    log_success "System updated successfully"
}

# Install basic dependencies
install_dependencies() {
    log_header "Installing Dependencies"
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "wget"
        "curl"
        "gnupg"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "unzip"
        "git"
    )
    
    log_info "Installing basic packages..."
    sudo apt install -y "${packages[@]}"
    
    log_success "Basic dependencies installed"
}

# Install Chrome
install_chrome() {
    log_header "Installing Google Chrome"
    
    # Check if Chrome is already installed
    if command -v google-chrome &> /dev/null; then
        local version=$(google-chrome --version 2>/dev/null || echo "Unknown")
        log_success "Chrome already installed: $version"
        return 0
    fi
    
    log_info "Adding Google Chrome repository..."
    
    # Download and add Google signing key
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    
    # Add Chrome repository
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
    
    # Update package list
    sudo apt update
    
    # Install Chrome
    log_info "Installing Google Chrome..."
    if sudo apt install -y google-chrome-stable; then
        log_success "Chrome installed successfully"
    else
        log_warning "Chrome installation via repository failed. Trying direct download..."
        
        # Fallback: direct download
        wget -O /tmp/google-chrome-stable.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo dpkg -i /tmp/google-chrome-stable.deb
        sudo apt install -f -y  # Fix dependencies
        
        log_success "Chrome installed via direct download"
    fi
    
    # Verify installation
    if google-chrome --version &> /dev/null; then
        local version=$(google-chrome --version)
        log_success "Chrome verification successful: $version"
    else
        log_error "Chrome installation verification failed"
        return 1
    fi
}

# Install Chrome dependencies
install_chrome_dependencies() {
    log_header "Installing Chrome Dependencies"
    
    local packages=(
        "libnss3"
        "libgconf-2-4"
        "libxss1"
        "libappindicator1"
        "libindicator7"
        "gconf-service"
        "fonts-liberation"
        "libappindicator3-1"
        "libasound2"
        "libatk-bridge2.0-0"
        "libdrm2"
        "libxcomposite1"
        "libxdamage1"
        "libxrandr2"
        "libgbm1"
        "libxkbcommon0"
        "libgtk-3-0"
        "libxshmfence1"
        "xvfb"
    )
    
    log_info "Installing Chrome dependencies..."
    sudo apt install -y "${packages[@]}"
    
    log_success "Chrome dependencies installed"
}

# Setup Python environment
setup_python() {
    log_header "Setting up Python Environment"
    
    # Check Python version
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python version: $python_version"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    log_success "Python environment ready"
}

# Clone or setup project
setup_project() {
    log_header "Setting up Project"
    
    local project_dir="social-media-uploader"
    
    # If we're already in the project directory, skip cloning
    if [[ -f "social_media_uploader.py" ]]; then
        log_info "Already in project directory"
        return 0
    fi
    
    # Check if project directory exists
    if [[ -d "$project_dir" ]]; then
        log_info "Project directory exists. Updating..."
        cd "$project_dir"
        if [[ -d ".git" ]]; then
            git pull
        fi
    else
        log_info "Project directory not found. Please ensure project files are available."
        log_info "Current directory: $(pwd)"
        log_info "Files: $(ls -la)"
    fi
}

# Install Python requirements
install_python_requirements() {
    log_header "Installing Python Requirements"
    
    if [[ ! -f "requirements.txt" ]]; then
        log_warning "requirements.txt not found. Creating basic requirements..."
        cat > requirements.txt << EOF
selenium>=4.15.0
webdriver-manager>=4.0.0
colorama>=0.4.6
requests>=2.31.0
google-auth>=2.23.4
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.108.0
google-generativeai>=0.3.2
opencv-python>=4.8.1.78
pillow>=10.1.0
numpy>=1.24.3
yt-dlp>=2023.12.30
EOF
    fi
    
    log_info "Installing Python requirements..."
    python3 -m pip install -r requirements.txt
    
    log_success "Python requirements installed"
}

# Setup ChromeDriver
setup_chromedriver() {
    log_header "Setting up ChromeDriver"
    
    log_info "Running driver setup..."
    if python3 -c "from driver_manager import UniversalDriverManager; UniversalDriverManager().get_chromedriver_path()" &> /dev/null; then
        log_success "ChromeDriver setup successful"
    else
        log_warning "ChromeDriver setup failed. Running fix script..."
        python3 fix_all_drivers.py
    fi
}

# Run tests
run_tests() {
    log_header "Running Tests"
    
    log_info "Testing driver setup..."
    if python3 driver_manager.py --test; then
        log_success "Driver test passed"
    else
        log_error "Driver test failed"
        return 1
    fi
    
    log_info "Running comprehensive tests..."
    if python3 test_driver_fix.py; then
        log_success "All tests passed"
    else
        log_warning "Some tests failed"
    fi
}

# Setup systemd service (optional)
setup_service() {
    log_header "Setting up Systemd Service (Optional)"
    
    read -p "Do you want to create a systemd service for the uploader? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local service_file="/etc/systemd/system/social-media-uploader.service"
        local current_dir=$(pwd)
        local user=$(whoami)
        
        sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Social Media Uploader
After=network.target

[Service]
Type=simple
User=$user
WorkingDirectory=$current_dir
ExecStart=/usr/bin/python3 $current_dir/social_media_uploader.py
Restart=always
RestartSec=10
Environment=DISPLAY=:99
Environment=HEADLESS=true

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable social-media-uploader
        
        log_success "Systemd service created and enabled"
        log_info "Start with: sudo systemctl start social-media-uploader"
        log_info "Check status: sudo systemctl status social-media-uploader"
    fi
}

# Setup firewall (optional)
setup_firewall() {
    log_header "Setting up Firewall (Optional)"
    
    read -p "Do you want to configure UFW firewall? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Configuring UFW firewall..."
        
        sudo ufw --force enable
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw allow 80
        sudo ufw allow 443
        
        log_success "Firewall configured"
        log_info "SSH, HTTP, and HTTPS ports are allowed"
    fi
}

# Show final instructions
show_final_instructions() {
    log_header "Installation Complete!"
    
    echo -e "${GREEN}🎉 Social Media Uploader has been successfully installed on your Ubuntu VPS!${NC}"
    echo
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "1. Test the installation:"
    echo "   python3 social_media_uploader.py"
    echo
    echo "2. Configure your API keys:"
    echo "   export GEMINI_API_KEY='your_gemini_api_key'"
    echo "   # Add to ~/.bashrc for persistence"
    echo
    echo "3. Setup YouTube API (if needed):"
    echo "   # Place youtube_credentials.json in credentials/ folder"
    echo
    echo "4. Run diagnostics if needed:"
    echo "   python3 driver_manager.py --diagnostics"
    echo
    echo -e "${BLUE}🔧 Useful Commands:${NC}"
    echo "• Test drivers: python3 driver_manager.py --test"
    echo "• Fix issues: python3 fix_all_drivers.py"
    echo "• Check status: python3 social_media_uploader.py"
    echo
    echo -e "${GREEN}✅ Features Available:${NC}"
    echo "• Video upload to TikTok, Facebook, YouTube, Instagram"
    echo "• Text status to Facebook"
    echo "• Image/media posts to Facebook and Instagram"
    echo "• AI content generation (with Gemini API)"
    echo "• Video enhancement with FFmpeg"
    echo "• Video download with yt-dlp"
    echo "• Headless mode optimized for VPS"
    echo
    echo -e "${YELLOW}📚 Documentation:${NC}"
    echo "• Setup guide: setup_ubuntu_vps.md"
    echo "• ChromeDriver help: setup_chromedriver.md"
    echo "• Gemini API: setup_gemini_api.md"
    echo "• YouTube API: setup_youtube_api.md"
    echo
    echo -e "${BLUE}🐧 VPS-Specific Features:${NC}"
    echo "• Auto-detected VPS environment"
    echo "• Headless mode enabled automatically"
    echo "• Memory-optimized Chrome options"
    echo "• Single-process mode for stability"
    echo
    log_success "Installation completed successfully!"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀 Social Media Uploader - Ubuntu VPS Installer      ║
║                                                              ║
║  Complete setup for TikTok, Facebook, YouTube, Instagram    ║
║  uploaders with AI, FFmpeg, and video download support      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log_info "Starting Ubuntu VPS installation..."
    echo
    
    # Run installation steps
    check_root
    detect_ubuntu
    update_system
    install_dependencies
    install_chrome
    install_chrome_dependencies
    setup_python
    setup_project
    install_python_requirements
    setup_chromedriver
    run_tests
    setup_service
    setup_firewall
    show_final_instructions
}

# Run main function
main "$@"