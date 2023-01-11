import os
import sys

try:
    import PyInstaller.__main__ as pyinstaller
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install pyinstaller")
    import PyInstaller.__main__ as pyinstaller

try:
    import pyinstaller_versionfile
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install pyinstaller-versionfile")
    import pyinstaller_versionfile

from main import __version__, __product_name__, __author__

__product_file_name__ = "Zotero-WSL-ProxyServer"
__entry__ = "main.py"
__cython_module_name__ = "main"

if __name__ == '__main__':
    # Build cython
    os.system(f"{sys.executable} setup.py build_ext --inplace")

    # Create version info
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

    # Package
    pyinstaller.run([
        __entry__,
        '-F',
        '--icon=assets/app_icon.ico',
        f'--hidden-import={__cython_module_name__}',
        f"--version-file={version_file_path}",
        f"--name={release_name}",
    ])
