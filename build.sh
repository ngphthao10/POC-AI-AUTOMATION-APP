#!/bin/bash

# Build script for Simple Python Application
# This script will create executable files using PyInstaller

echo "🚀 Building Simple Python Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 PyInstaller not found. Installing..."
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
echo "🔨 Building executable..."
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
    
    echo "📁 Executable file location:"
    ls -la dist/
    echo ""
    echo "🎉 You can now run your application:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   ./dist/ai_automation_app"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "   dist\\ai_automation_app.exe"
    else
        echo "   ./dist/ai_automation_app"
    fi
    
    echo ""
    echo "📦 File size: $(du -h dist/ai_automation_app | cut -f1)"
    echo "💡 Tip: You can copy this file and input.json to any computer and run it without Python installed!"
else
    echo "❌ Build failed!"
    exit 1
fi
