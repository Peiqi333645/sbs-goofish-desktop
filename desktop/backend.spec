# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all

repo_root = os.path.abspath(os.path.join(SPECPATH, ".."))
entry_point = os.path.join(SPECPATH, "backend_entry.py")
playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all("playwright")

analysis = Analysis(
    [entry_point],
    pathex=[repo_root],
    binaries=playwright_binaries,
    datas=playwright_datas + [
        (os.path.join(repo_root, "dist"), "dist"),
        (os.path.join(repo_root, "static"), "static"),
        (os.path.join(repo_root, "prompts"), "prompts"),
        (os.path.join(repo_root, ".env.example"), "."),
    ],
    hiddenimports=playwright_hiddenimports + [
        "uvicorn.logging",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan.on",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "coverage"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="sbs-goofish-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="sbs-goofish-backend",
)
