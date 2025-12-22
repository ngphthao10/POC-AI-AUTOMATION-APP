#!/bin/bash
################################################################################
# CSP Automation Application - Build Script
# Description: Builds standalone executable with PyInstaller and Playwright
# Version: 2.0.0
# Updated: 2025-12-22
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="csp_automation"
SPEC_FILE="csp_automation.spec"
PYTHON_VERSION="3.10"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  🚀 CSP Automation Application - Build Script          ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

################################################################################
# Preflight Checks
################################################################################

check_python() {
    print_step "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed. Please install Python 3.10+."
        exit 1
    fi

    PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VER found"
}

check_required_files() {
    print_step "Checking required files..."

    required_files=(
        "console_app.py"
        "requirements.txt"
        ".env"
        "input.json"
    )

    missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -ne 0 ]; then
        print_error "Missing required files:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi

    print_success "All required files present"
}

generate_spec() {
    if [ ! -f "$SPEC_FILE" ]; then
        print_step "Generating spec file..."

        pyi-makespec console_app.py \
            --name="$APP_NAME" \
            --onefile \
            --windowed \
            --add-data="input.json:." \
            --add-data=".env:." \
            --hidden-import="nova_act" \
            --hidden-import="playwright" \
            --hidden-import="playwright.sync_api" \
            --collect-all="playwright" \
            --collect-all="nova_act"

        print_success "Spec file generated"
    else
        print_step "Using existing spec file"
    fi
}

################################################################################
# Virtual Environment Setup
################################################################################

setup_venv() {
    print_step "Setting up virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists, using it..."
        source venv/bin/activate
    else
        print_step "Creating new virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        print_success "Virtual environment created"
    fi
}

install_dependencies() {
    print_step "Installing Python dependencies..."

    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet

    print_success "Dependencies installed"
}

install_playwright() {
    print_step "Installing Playwright browsers..."

    playwright install chromium

    if [ $? -eq 0 ]; then
        print_success "Playwright browsers installed"
    else
        print_error "Failed to install Playwright browsers"
        exit 1
    fi
}

verify_playwright() {
    print_step "Verifying Playwright installation..."

    python3 -c "
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
        print('✓ Playwright verification passed')
except Exception as e:
    print(f'✗ Playwright verification failed: {e}')
    exit(1)
" || exit 1
}

################################################################################
# Build Process
################################################################################

clean_build() {
    print_step "Cleaning previous builds..."

    rm -rf build dist
    rm -f *.pyc
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

    print_success "Build artifacts cleaned"
}

run_pyinstaller() {
    print_step "Running PyInstaller..."
    echo ""
    echo "This may take a few minutes..."
    echo ""

    pyinstaller "$SPEC_FILE" --clean --noconfirm

    if [ $? -eq 0 ]; then
        print_success "PyInstaller build completed"
    else
        print_error "PyInstaller build failed"
        exit 1
    fi
}

copy_assets() {
    print_step "Copying assets to dist folder..."

    # Copy input.json if not already copied by spec
    if [ -f "input.json" ] && [ ! -f "dist/input.json" ]; then
        cp input.json dist/
    fi

    # Copy .env if exists
    if [ -f ".env" ] && [ ! -f "dist/.env" ]; then
        cp .env dist/
    fi

    # Create necessary directories
    mkdir -p dist/logs
    mkdir -p dist/screenshots

    print_success "Assets copied"
}

create_launcher() {
    print_step "Creating launcher script..."

    cat > "dist/launch.sh" << 'EOF'
#!/bin/bash
# CSP Automation Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting CSP Automation..."

# Check for first run
if [ ! -f ".playwright_installed" ]; then
    echo "📦 First run detected - setting up Playwright browsers..."
    playwright install chromium 2>/dev/null || echo "⚠️  Playwright will auto-install on first use"
    touch ".playwright_installed"
fi

# Run the application
./csp_automation "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Application exited with error code: $EXIT_CODE"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - Check input.json is properly configured"
    echo "   - Ensure .env file has correct credentials"
    echo "   - Check logs/ folder for detailed errors"
    echo ""
fi

exit $EXIT_CODE
EOF

    chmod +x dist/launch.sh
    print_success "Launcher script created"
}

create_readme() {
    print_step "Creating README for distribution..."

    cat > "dist/README.txt" << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║  CSP AUTOMATION APPLICATION - DISTRIBUTION PACKAGE           ║
╚══════════════════════════════════════════════════════════════╝

📦 PACKAGE CONTENTS:
  • csp_automation       - Main executable
  • launch.sh            - Launcher script (recommended)
  • input.json           - Configuration file (EDIT THIS)
  • .env                 - Environment variables (credentials)
  • logs/                - Log output directory
  • screenshots/         - Screenshot output directory
  • README.txt           - This file

🚀 QUICK START:

1. Edit input.json with your configuration:
   - admin_credentials (username, password, csp_admin_url)
   - users list (target_user, new_role, branch_hierarchy)

2. Edit .env with your credentials (if needed)

3. Run the application:
   macOS/Linux: ./launch.sh
   or directly:  ./csp_automation

4. Follow the on-screen menu

📋 REQUIREMENTS:
  • macOS 10.13+ or Linux
  • Internet connection (for Playwright browsers on first run)
  • Sufficient disk space (~500MB for browser binaries)

🔧 TROUBLESHOOTING:

Issue: "Permission denied"
Fix:   chmod +x csp_automation launch.sh

Issue: Playwright browsers not found
Fix:   Run: playwright install chromium

Issue: Application crashes
Fix:   Check logs/ folder for error details
       Ensure input.json is valid JSON
       Verify .env credentials are correct

📞 SUPPORT:
  Check the logs/ folder for detailed error messages
  Screenshots are saved in screenshots/ folder on errors

📝 NOTES:
  • First run may take longer (downloading browser binaries)
  • Logs are saved with timestamps in logs/ folder
  • DO NOT delete browser cache directories

Version: 1.0.0
Built: $(date)
EOF

    print_success "README created"
}

################################################################################
# Post-Build
################################################################################

verify_build() {
    print_step "Verifying build..."

    if [ ! -f "dist/$APP_NAME" ]; then
        print_error "Executable not found in dist/"
        exit 1
    fi

    chmod +x "dist/$APP_NAME"

    # Get file size
    SIZE=$(du -h "dist/$APP_NAME" | cut -f1)
    print_success "Build verified (Size: $SIZE)"
}

print_summary() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ✅ BUILD COMPLETED SUCCESSFULLY                            ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📁 Build location: ./dist/"
    echo "📦 Executable:     ./dist/$APP_NAME"
    echo "🚀 Launcher:       ./dist/launch.sh"
    echo ""
    echo "📋 Next steps:"
    echo "  1. cd dist"
    echo "  2. Edit input.json with your configuration"
    echo "  3. ./launch.sh (or ./$APP_NAME)"
    echo ""
    echo "💡 For distribution:"
    echo "  - Zip the entire dist/ folder"
    echo "  - Share with end users"
    echo "  - Users only need to run launch.sh"
    echo ""
}

################################################################################
# Main
################################################################################

main() {
    print_header

    # Preflight checks
    check_python
    check_required_files

    # Setup
    setup_venv
    install_dependencies
    install_playwright
    verify_playwright

    # Build
    clean_build
    generate_spec
    run_pyinstaller

    # Post-build
    copy_assets
    create_launcher
    create_readme
    verify_build

    # Summary
    print_summary
}

# Run main
main
