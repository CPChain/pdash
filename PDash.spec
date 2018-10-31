# -*- mode: python -*-

block_cipher = None


a = Analysis(['cpchain/wallet/main.py'],
             pathex=['/Users/liaojinlong/Workspace/CPChain/pdash'],
             binaries=[],
             datas=[],
             hiddenimports=['eth_hash.backends.pycryptodome'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='PDash',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='lib/pdash.icns')

app = BUNDLE(exe,
             name='PDash.app',
             icon='lib/pdash.icns',
             bundle_identifier=None,
             info_plist={
                'NSHighResolutionCapable': 'True'
             },
            )
