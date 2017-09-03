import os
import sys
import scipy

from distutils.core import setup
import py2exe

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = dict(
    optimize = 2,
    includes = ["mf3"], # List of all the modules you want to import
    packages = ['nltk', 'csv'],
)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

#if sys.platform == "win32":
#    base = "Win32GUI"

os.environ['TCL_LIBRARY'] = r'C:\Users\Sytske\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Sytske\Anaconda3\tcl\tk8.6'

# Usage
# Either use:         python setup.py build
# or with installer:  python setup.py bdist_msi
#

setup(name = "TextTool",
      version = "0.2",
      description = "TextTool",
      options = {"py2exe": build_exe_options},
      console = ["TextToolGui.py"])