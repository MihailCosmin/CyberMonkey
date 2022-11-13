from cx_Freeze import setup, Executable
from sys import platform

base = None
if (platform == "win32"):
    base = "Win32GUI"

with open("requirements.txt", "r", encoding="utf-8") as _:
    requirements = _.read().splitlines()

executables = [
    Executable(
        script="src/CyberMonkey.py",
        base=base,
        icon="src/img/ico/monkey.ico"
    )
]

include_files = ["src/img/ico/monkey.ico"]
packages = ["ctypes", "imp", "PySide6", "yt_dlp", "cx_Freeze", "PyInstaller", "pyperclip", "regex", "adblockparser"]
excludes = [
    "PyQt5", "PyQt4", "reportlab", "matplotlib", "numba", "scipy", "sqlalchemy", "sqlite3", "soupsieve",
    "llvmlite", "black", "bs4", "jupyter", "tornado", "pygments"
]
options = {
    'build_exe': {
        'packages': requirements,  # Was packages
        'excludes': excludes,
        'include_files': include_files,
    },
}

package_data = {
    'img': ['*', 'ico/*', 'png/*', 'svg/*'],
    'qss': ['*'],
    'utils': ['*'],
    'widgets': ['*'],
}

setup(
    name="CyberMonkey",
    install_requires=requirements,
    packages=['utils', 'widgets', 'img', 'qss'],
    package_dir={'': 'src'},
    package_data=package_data,
    options=options,
    version="0.0.1",
    description='GUI for AutoMonkey that allows you to easily create automations',
    executables=executables
)
