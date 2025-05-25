# -*- mode: python ; coding: utf-8 -*-

import os

build_dir = os.path.join('_build', 'build')
dist_dir = os.path.join('_build', 'dist')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')],
    hiddenimports=[],
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
    name='main',
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

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles if hasattr(a, 'zipfiles') else [],
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
    distpath=dist_dir,
    workpath=build_dir,
)
