import os

# noinspection PyBroadException
try:
    import PyInstaller.__main__ as pyinstaller
except:
    os.system("python -m pip install pyinstaller")
    import PyInstaller.__main__ as pyinstaller

# noinspection PyBroadException
try:
    import pyinstaller_versionfile
except:
    os.system("python -m pip install pyinstaller-versionfile")
    import pyinstaller_versionfile

from main import __version__, __product_name__, __author__

__product_file_name__ = "Zotero-WSL-ProxyServer"
__entry__ = "main.py"

if __name__ == '__main__':
    release_name = f"{__product_file_name__}_{__version__}"
    build_path = os.path.join("build", release_name)
    version_file_path = os.path.join(build_path, "file_version_info.txt")
    if not os.path.exists(build_path):
        os.makedirs(build_path)

    pyinstaller_versionfile.create_versionfile(
        output_file=version_file_path,
        version=__version__,
        company_name=__author__,
        file_description=__product_name__,
        internal_name=__product_name__,
        legal_copyright=f"© {__author__}. All rights reserved.",
        original_filename=f"{__product_file_name__}.exe",
        product_name=__product_name__,
        translations=[0, 1200]
    )

    pyinstaller.run([
        __entry__,
        '-F',
        '--icon=assets/app_icon.ico',
        f"--version-file={version_file_path}",
        f"--name={release_name}",
    ])
