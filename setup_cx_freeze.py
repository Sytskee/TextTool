import inspect
import os
import sys
import scipy


from cx_Freeze import setup, Executable

_32_BIT = '32bit'
_64_BIT = '64bit'

#   target_platform = _32_BIT
target_platform = _64_BIT

include_files = []

if target_platform == _32_BIT:
    # File list copied from C:\Users\Sytske\Anaconda3_32\conda-meta\mkl-11.3.3-1.json
    include_files = [r'C:\Users\Sytske\Anaconda3_32\DLLs\tcl86t.dll',
                     r'C:\Users\Sytske\Anaconda3_32\DLLs\tk86t.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\cilkrts20.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\ifdlg100.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libchkp.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libicaf.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libifcoremd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libifcoremdd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libifcorert.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libifcorertd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libifportmd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libimalloc.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libiomp5md.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libiompstubs5md.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libmmd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libmmdd.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\libmpx.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_avx.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_avx2.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_avx512.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_core.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_intel_thread.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_msg.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_p4.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_p4m.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_p4m3.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_rt.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_sequential.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_tbb_thread.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_avx.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_avx2.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_avx512.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_cmpt.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_ia.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_p4.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_p4m.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_p4m2.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\mkl_vml_p4m3.dll',
                     r'C:\Users\Sytske\Anaconda3_32\Library\bin\svml_dispmd.dll']

if target_platform == _64_BIT:
    # File list copied from C:\Users\Sytske\Anaconda3\conda-meta\mkl-11.3.1-0.json
    include_files = [r'C:\Users\Sytske\Anaconda3\DLLs\tcl86t.dll',
                     r'C:\Users\Sytske\Anaconda3\DLLs\tk86t.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\cilkrts20.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\ifdlg100.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libchkp.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libicaf.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libifcoremd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libifcoremdd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libifcorert.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libifcorertd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libifportmd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libimalloc.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libiomp5md.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libiompstubs5md.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libmmd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libmmdd.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\libmpx.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\liboffload.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_avx.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_avx2.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_avx512.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_core.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_def.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_intel_thread.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_mc.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_mc3.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_msg.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_rt.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_sequential.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_tbb_thread.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_avx.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_avx2.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_avx512.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_cmpt.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_def.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_mc.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_mc2.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\mkl_vml_mc3.dll',
                     r'C:\Users\Sytske\Anaconda3\Library\bin\svml_dispmd.dll']


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = dict(
    packages=['os', 'nltk', 'csv', 'numpy', 'matplotlib'],
    includes=['tkinter', 'numpy.core._methods', 'numpy.lib.format', 'numpy.core.multiarray'],
    include_files=[os.path.dirname(scipy.__file__),
                   r'.\nltk_data\\']
                   + include_files
)

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

#if sys.platform == "win32":
#    base = "Win32GUI"

if target_platform == _32_BIT:
    os.environ['TCL_LIBRARY'] = r'C:\Users\Sytske\Anaconda3_32\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'C:\Users\Sytske\Anaconda3_32\tcl\tk8.6'

if target_platform == _64_BIT:
    os.environ['TCL_LIBRARY'] = r'C:\Users\Sytske\Anaconda3\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'C:\Users\Sytske\Anaconda3\tcl\tk8.6'

# Usage
# Either use:         python setup.py build
# or with installer:  python setup.py bdist_msi
#
# We have copied 'C:\Users\Sytske\Anaconda3\Lib\site-packages\cx_Freeze\initscripts\Console.py' to 'ConsoleWithFreezeSupport.py'
# and added multiprocessing.freeze_support()
#

init_script_full_path = os.path.join(os.path.dirname(os.path.realpath(inspect.stack()[0][1])), 'ConsoleWithFreezeSupport.py')

setup(name = "TextTool",
      version = "0.2",
      description = "TextTool",
      options = {"build_exe": build_exe_options},
      executables = [Executable("TextToolGui.py", base=base, initScript=init_script_full_path)]
)