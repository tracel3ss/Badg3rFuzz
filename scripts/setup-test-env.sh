# scripts/setup-test-env.sh - Script para configurar entorno de testing
#!/bin/bash
set -e

echo "🔧 Setting up test environment..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    OS="unknown"
fi

log "Detected OS: $OS"

# Instalar dependencias del sistema
install_system_deps() {
    log "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y \
            firefox \
            chromium-browser \
            xvfb \
            openssl \
            ca-certificates \
            wget \
            unzip
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install firefox
            brew install --cask google-chrome
        else
            warn "Homebrew not found. Please install Firefox and Chrome manually."
        fi
    else
        warn "Unsupported OS for automatic dependency installation"
    fi
}

# Descargar WebDrivers
download_webdrivers() {
    log "Downloading WebDrivers..."
    
    mkdir -p drivers
    cd drivers
    
    # GeckoDriver para Firefox
    log "Downloading GeckoDriver..."
    if [[ "$OS" == "linux" ]]; then
        wget -O geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-linux64.tar.gz"
        tar -xzf geckodriver.tar.gz
        chmod +x geckodriver
    elif [[ "$OS" == "macos" ]]; then
        wget -O geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-macos.tar.gz"
        tar -xzf geckodriver.tar.gz
        chmod +x geckodriver
    elif [[ "$OS" == "windows" ]]; then
        wget -O geckodriver.zip "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-v0.33.0-win64.zip"
        unzip geckodriver.zip
    fi
    
    # ChromeDriver
    log "Downloading ChromeDriver..."
    if [[ "$OS" == "linux" ]]; then
        wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
        unzip chromedriver.zip
        chmod +x chromedriver
    elif [[ "$OS" == "macos" ]]; then
        wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_mac64.zip"
        unzip chromedriver.zip
        chmod +x chromedriver
    elif [[ "$OS" == "windows" ]]; then
        wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip"
        unzip chromedriver.zip
    fi
    
    cd ..
    log "WebDrivers downloaded successfully"
}

# Configurar display virtual para Linux
setup_virtual_display() {
    if [[ "$OS" == "linux" ]]; then
        log "Setting up virtual display..."
        export DISPLAY=:99
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
        sleep 3
        log "Virtual display configured"
    fi
}

# Crear archivos de test mock
create_test_files() {
    log "Creating test files..."
    
    mkdir -p test_data
    
    # Wordlist de usuarios
    cat > test_data/users.txt << EOF
admin
administrator
test
user
demo
guest
root
EOF
    
    # Wordlist de contraseñas
    cat > test_data/passwords.txt << EOF
password
123456
admin
test
password123
qwerty
letmein
welcome
EOF
    
    # User agents de prueba
    cat > test_data/user_agents.txt << EOF
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0
EOF
    
    # Proxies de prueba (no funcionales, solo para testing)
    cat > test_data/proxies.txt << EOF
http://proxy1.test.com:8080
http://proxy2.test.com:3128
socks5://proxy3.test.com:1080
EOF
    
    log "Test files created successfully"
}

# Función principal
main() {
    log "Starting test environment setup for Badg3rFuzz..."
    
    install_system_deps
    download_webdrivers
    setup_virtual_display
    create_test_files
    
    log "✅ Test environment setup completed successfully!"
    log "You can now run tests with: pytest tests/"
}

# Ejecutar solo si es llamado directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi