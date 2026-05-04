# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('assets/icon.ico', 'assets')],  # config.jsonとアイコンを同梱
    hiddenimports=[
        'win32timezone',
        'win32clipboard',
        'win32con',
        'win32api',
        'win32event',
        'pywintypes',
        'winotify',
        'keyboard',
        'pystray',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClipboardTransformer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # コンソールウィンドウを非表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    uac_admin=True,  # 管理者権限を要求
    uac_uiaccess=False,  # UIアクセス権限は不要
)
