# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['pythumb/__main__.py'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pythumb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'python36.dll',
        'python37.dll',
        'python38.dll',
        'python39.dll',
        'ucrtbase.dll',
        'vcruntime140.dll'
    ],
    runtime_tmpdir=None,
    console=True,
    icon='assets/icon.ico'
)
