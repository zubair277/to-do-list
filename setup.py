"""
Setup script for creating a standalone macOS app from the to-do list application.
Run: python3 setup.py py2app
"""

from setuptools import setup

APP = ['todolist.py']
DATA_FILES = [
    ('', ['background.jpg']),  # Include background image if it exists
    ('', ['pixel_todo_tasks.json']),  # Include existing tasks file
]

OPTIONS = {
    'argv_emulation': True,
    'iconfile': None,  # You can add an icon file here
    'plist': {
        'CFBundleName': 'Nighttime To-Do',
        'CFBundleDisplayName': 'Nighttime To-Do List',
        'CFBundleIdentifier': 'com.mountainapps.nighttime-todo',
        'CFBundleVersion': '3.0.0',
        'CFBundleShortVersionString': '3.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,  # Set to True if you want it to not show in dock
    },
    'packages': ['PyQt6'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui'],
    'excludes': ['tkinter', 'matplotlib', 'numpy', 'scipy'],
    'optimize': 2,
    'compressed': True,
    'dist_dir': 'dist',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
