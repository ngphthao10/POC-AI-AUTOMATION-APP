#!/usr/bin/env python3
"""
Playwright Runtime Hook for PyInstaller
This hook ensures Playwright works correctly in the bundled executable
"""

import os
import sys
from pathlib import Path

def get_hook_dirs():
    """Get directories needed for Playwright runtime"""
    return []

def get_hook_imports():
    """Get imports needed for Playwright runtime"""
    return []

# Playwright initialization for PyInstaller frozen environment
if getattr(sys, 'frozen', False):
    # We're running in a PyInstaller bundle
    application_path = sys._MEIPASS
    
    # Set Playwright environment variables for bundled app
    os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', '0')
    
    # Ensure Playwright can find its drivers in the bundled environment
    if hasattr(sys, '_MEIPASS'):
        # Look for playwright drivers in the bundle
        playwright_driver_path = os.path.join(sys._MEIPASS, 'playwright', 'driver')
        if os.path.exists(playwright_driver_path):
            os.environ['PLAYWRIGHT_DRIVER_PATH'] = playwright_driver_path
else:
    # We're running in a normal Python environment
    pass

# Additional setup for NovaAct compatibility
try:
    import nova_act
    # Ensure NovaAct can find its artifacts
    if getattr(sys, 'frozen', False):
        nova_act_artifacts_path = os.path.join(sys._MEIPASS, 'nova_act', 'artifacts')
        if os.path.exists(nova_act_artifacts_path):
            # Set environment variable for NovaAct to find its Chrome extension
            os.environ['NOVA_ACT_ARTIFACTS_PATH'] = nova_act_artifacts_path
except ImportError:
    # NovaAct not available, continue
    pass

print("🔧 Playwright runtime hook initialized")
