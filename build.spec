# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_data_files


whisper_assets = collect_data_files('whisper', subdir='assets')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/static', 'src/static'), ('src/locales/app.qm', 'src/locales'), *whisper_assets],
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
    [],
    exclude_binaries=True,
    name='Whisper GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Whisper GUI',
)
app = BUNDLE(
    coll,
    name='Whisper GUI.app',
    icon='assets/icon/icon.icns',
    bundle_identifier=None,
)
