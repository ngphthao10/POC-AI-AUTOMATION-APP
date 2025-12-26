# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules
import os

# Add src directory to Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath('.')), 'src')

datas = [('input.json', '.'), ('.env', '.')]
binaries = []
hiddenimports = [
    'nova_act',
    'playwright',
    'playwright.sync_api',
    # Collect all modules from src/
    'src.shared.retry_utils',
    'src.shared.logger',
    'src.shared.screenshot_utils',
    'src.shared.error_utils',
    'src.shared.action_counter',
    'src.shared.wait_utils',
    'src.shared.nova_manager',
    'src.features.csp.csp_admin_main',
    'src.features.csp.handlers',
    'src.features.csp.handlers.csp_login_handler',
    'src.features.csp.handlers.csp_user_search_handler',
    'src.features.csp.handlers.csp_role_handler',
    'src.features.csp.handlers.csp_branch_handler',
    'src.features.csp.handlers.csp_save_handler',
    'src.csp.csp_admin_change_role_and_branch',
]

# Collect all from src packages
try:
    hiddenimports += collect_submodules('src.shared')
    hiddenimports += collect_submodules('src.features')
    hiddenimports += collect_submodules('src.csp')
except:
    pass

tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('nova_act')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['console_app.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='csp_automation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name='csp_automation.app',
    icon=None,
    bundle_identifier=None,
)
