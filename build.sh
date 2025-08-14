#!/bin/bash

# Build script for AI Automation Application with NovaAct and Playwright
# This script will create executable files using PyInstaller with full Playwright support

echo "🚀 Building AI Automation Application with Playwright..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check for existing virtual environments and use the appropriate one
if [ -d "nova_act_env" ]; then
    echo "� Using existing nova_act_env virtual environment..."
    source nova_act_env/bin/activate
elif [ -d "venv" ]; then
    echo "🔧 Using existing venv virtual environment..."
    source venv/bin/activate
else
    echo "� Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install or upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements first
echo "📦 Installing Python requirements..."
pip install -r requirements.txt

# Install Playwright browsers (critical for NovaAct)
echo "🌐 Installing Playwright browsers (this may take a few minutes)..."
playwright install chromium

# Verify Playwright installation
echo "✅ Verifying Playwright installation..."
python3 -c "
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
        print('✅ Playwright browsers installed successfully')
except Exception as e:
    print(f'❌ Playwright installation failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Playwright verification failed. Build cannot continue."
    exit 1
fi

# Check if PyInstaller is installed
if ! pip show pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
if [ -d "build" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "🧹 Cleaning previous dist..."
    rm -rf dist
fi

# Build the application
echo "🔨 Building executable with Playwright support..."
echo "📋 PyInstaller will include:"
echo "   - NovaAct package and artifacts"
echo "   - Playwright drivers and browsers"
echo "   - All Python dependencies"
echo "   - Configuration files"
echo ""

pyinstaller ai_automation_app.spec

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Copy input.json to dist directory
    echo "📋 Copying input.json to distribution directory..."
    if [ -f "src/csp/input.json" ]; then
        cp "src/csp/input.json" "dist/"
        echo "✅ input.json copied successfully"
    else
        echo "⚠️  input.json not found in src/csp/ - you can add it later"
    fi
    
    # Create a simple test script to verify the build
    echo "🧪 Creating build verification script..."
    cat > "dist/test_build.py" << 'EOF'
#!/usr/bin/env python3
import sys
import os

print("🧪 Testing built application dependencies...")

try:
    import nova_act
    print("✅ NovaAct import successful")
except ImportError as e:
    print(f"❌ NovaAct import failed: {e}")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright import successful")
except ImportError as e:
    print(f"❌ Playwright import failed: {e}")
    sys.exit(1)

try:
    with sync_playwright() as p:
        print("✅ Playwright context created")
        browser = p.chromium.launch(headless=True)
        print("✅ Chromium browser launched")
        browser.close()
        print("✅ Browser closed successfully")
except Exception as e:
    print(f"❌ Playwright browser test failed: {e}")
    sys.exit(1)

print("🎉 All tests passed! Built application should work correctly.")
EOF

    # Create launch script for the built application
    echo "🚀 Creating launch script..."
    cat > "dist/launch_app.sh" << 'EOF'
#!/bin/bash

# Startup script for AI Automation App
# This ensures Playwright browsers are available before running the main application

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="ai_automation_app"

echo "🚀 Starting AI Automation Application..."

# Check if this is the first run by looking for a marker file
FIRST_RUN_MARKER="$SCRIPT_DIR/.playwright_setup_complete"

if [ ! -f "$FIRST_RUN_MARKER" ]; then
    echo "🌐 First run detected - setting up Playwright browsers..."
    echo "⏳ This may take a few minutes to download browser binaries..."
    
    # Check if playwright command is available
    if command -v playwright &> /dev/null; then
        echo "📦 Installing Chromium browser..."
        playwright install chromium
        
        if [ $? -eq 0 ]; then
            echo "✅ Playwright browsers installed successfully"
            touch "$FIRST_RUN_MARKER"
        else
            echo "❌ Failed to install Playwright browsers"
            echo "💡 You may need to run this manually: playwright install chromium"
            read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
        fi
    else
        echo "⚠️  Playwright command not found in PATH"
        echo "💡 Browsers will be installed automatically on first NovaAct usage"
        touch "$FIRST_RUN_MARKER"
    fi
    
    echo ""
fi

# Run the main application
echo "🎯 Launching AI Automation Application..."
"$SCRIPT_DIR/$APP_NAME" "$@"

# Capture the exit code
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Application exited with error code: $EXIT_CODE"
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   1. Ensure Playwright browsers are installed: playwright install chromium"
    echo "   2. Check that input.json is properly configured"
    echo "   3. Verify network connectivity to the CSP portal"
    echo "   4. Try running from a terminal for more detailed error messages"
    echo ""
fi

exit $EXIT_CODE
EOF

    chmod +x dist/launch_app.sh
    
    echo "📁 Executable file location:"
    ls -la dist/
    echo ""
    echo "🎉 Build completed successfully!"
    echo ""
    echo "🧪 To test the build:"
    echo "   cd dist && python3 test_build.py"
    echo ""
    echo "🚀 To run your application:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   ./dist/ai_automation_app"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "   dist\\ai_automation_app.exe"
    else
        echo "   ./dist/ai_automation_app"
    fi
    
    echo ""
    echo "📦 File size: $(du -h dist/ai_automation_app | cut -f1)"
    echo ""
    echo "💡 Important notes:"
    echo "   - This build includes Playwright browsers"
    echo "   - The executable should work on systems without Python"
    echo "   - Make sure to copy both the executable and input.json"
    echo "   - For deployment, the entire dist/ folder may be needed"
    
else
    echo "❌ Build failed!"
    echo "💡 Common issues:"
    echo "   - Playwright browsers not installed properly"
    echo "   - Missing Python dependencies"
    echo "   - Insufficient disk space for browsers"
    echo ""
    echo "🔧 Try running: playwright install chromium"
    exit 1
fi
