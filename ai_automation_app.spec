# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import nova_act
from pathlib import Path

# Get the NovaAct package path
nova_act_path = os.path.dirname(nova_act.__file__)

a = Analysis(
    ['console_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/csp/input.json', '.'),
        ('src/config/nova_act_config.py', 'src/config/'),
        # Include NovaAct artifacts (Chrome extension files)
        (os.path.join(nova_act_path, 'artifacts'), 'nova_act/artifacts'),
        # Include our runtime hook
        ('playwright_runtime_hook.py', '.'),
    ],
    hiddenimports=[
        'playwright',
        'playwright._impl',
        'playwright._impl._driver',
        'playwright._impl._browser_type',
        'playwright._impl._page',
        'playwright.sync_api',
        'nova_act',
        'nova_act.impl',
        'nova_act.impl.playwright',
        'greenlet',
        'pyee',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['playwright_runtime_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ai_automation_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
