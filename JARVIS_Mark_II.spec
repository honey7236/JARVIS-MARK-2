# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Bundle both the custom frontend and standard package dependencies
datas = [
    ('frontend', 'frontend'),
]

hiddenimports = [
    'eel',
    'pygame',
    'gtts',
    'edge_tts',
    'requests',
    'bs4',
    'speech_recognition',
    'mtranslate',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchvision', 'tensorflow', 'scipy', 'numpy',
        'matplotlib', 'pandas', 'llvmlite', 'numba', 'sympy',
        'jedi', 'IPython', 'notebook'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Jarvis',
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
