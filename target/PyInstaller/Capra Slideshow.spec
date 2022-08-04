# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['/Users/Jordan/Developer/eds/capra/src/main/python/main.py'],
             pathex=['/Users/Jordan/Developer/eds/capra/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/usr/local/lib/python3.9/site-packages/fbs/freeze/hooks'],
             hooksconfig={},
             runtime_hooks=['/Users/Jordan/Developer/eds/capra/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='Capra Slideshow',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='/Users/Jordan/Developer/eds/capra/target/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=False,
               upx_exclude=[],
               name='Capra Slideshow')
app = BUNDLE(coll,
             name='Capra Slideshow.app',
             icon='/Users/Jordan/Developer/eds/capra/target/Icon.icns',
             bundle_identifier=None)
