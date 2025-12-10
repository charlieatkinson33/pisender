# pisender.spec

# Analysis of the script
a = Analysis(
    ['pisender.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter'],  # Ensure Tkinter is included
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
)

# Create the PYZ archive with the pure Python modules
pyz = PYZ(a.pure)

# Create the executable (one-file mode, no console)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='pisender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
