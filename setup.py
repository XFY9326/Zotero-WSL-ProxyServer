import os
import sys
from setuptools import setup

try:
    from Cython.Build import cythonize
except ModuleNotFoundError:
    os.system(f"{sys.executable} -m pip install cython")
    from Cython.Build import cythonize

MODULES = [
    "main.py"
]

if __name__ == '__main__':
    setup(
        ext_modules=cythonize(
            *MODULES,
            language_level=3,
            build_dir="build"
        )
    )
