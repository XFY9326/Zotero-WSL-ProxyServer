import os
import platform
import sys
from importlib.util import find_spec

from main import __version__, __product_name__, __author__

PRODUCT_NAME = "Zotero-WSL-ProxyServer"
BUILD_DIR = "build"
ICO_PATH = "assets/app_icon.ico"
MAIN_ENTRY = ".\\main.py"

if __name__ == "__main__":
    if find_spec("nuitka") is None:
        assert os.system(f"{sys.executable} -m pip install nuitka") == 0, "Pip nuitka install failed!"

    if platform.system().lower() != "windows":
        raise OSError("This program only support Windows!")

    # noinspection SpellCheckingInspection
    commands = [
        "nuitka",
        "--enable-console",
        "--onefile",
        "--assume-yes-for-downloads",
        f"--output-dir=\"{BUILD_DIR}\"",
        f"--output-filename=\"{PRODUCT_NAME}\"",
        f"--product-name=\"{__product_name__}\"",
        f"--file-description=\"{__product_name__}\"",
        f"--file-version=\"{__version__}\"",
        f"--product-version=\"{__version__}\"",
        f"--company-name=\"{__author__}\"",
        f"--copyright=\"© {__author__}. All rights reserved.\"",
        f"--windows-icon-from-ico=\"{ICO_PATH}\"",
        MAIN_ENTRY
    ]
    os.system(" ".join(commands))
