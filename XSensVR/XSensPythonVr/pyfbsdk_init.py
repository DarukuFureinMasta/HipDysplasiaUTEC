
# WARNING: Minimal error checking and validation is performed!

# First, let's set a version number for this file : Should remaining of MBVersion-2000 
from __future__ import print_function

gPyfbsdkInitVersion = "11.1"
import sys

MB_CONFIG_PATH = ""
MB_USER_CONFIG_PATH = ""

def AppendIfExists(path, p):
    import os
    if os.path.exists(p):
        path.append(p)
    #else:
        #print("Path doesn't exists", p)

def GetConfigPath():
    global MB_CONFIG_PATH
    return MB_CONFIG_PATH

def GetUserConfigPath():
    global MB_USER_CONFIG_PATH
    return MB_USER_CONFIG_PATH

def GetPythonStartupPath(configpath):
    import glob
    import os.path
#    print(configpath)
    pattern = os.path.join(MB_USER_CONFIG_PATH, "*.Application.txt")
    appconfig = glob.glob(pattern)
    if not appconfig:
        print("No config file!")
        return None
    appconfig = appconfig[0]
    startuppath = os.path.join(configpath, "PythonStartup")
    try:
        # We cannot use ConfigParser to read the file because our config
        # file starts with a version attribute not assigned to a section
        configfile = open(appconfig, "r")
        for line in configfile:
            if line.startswith("PythonStartup"):
                valuepair = line.split("=")
                if len(valuepair) == 2:
                    startuppath = valuepair[1].strip()
                break
    except:
        pass
    finally:
        configfile.close()
    return startuppath
    
def StartPyfbsdk(pUserConfigPath, pExePath):
    # First we need to figure out which platform we are on. We will use
    # sys.platform for that.
    
    global MB_USER_CONFIG_PATH
    MB_USER_CONFIG_PATH = pUserConfigPath
    
    import os
    
    lDefaultSysPaths = sys.path
    
    global MB_CONFIG_PATH
    MB_CONFIG_PATH = os.path.join(pExePath, "..", "config")

    try:
        # We need to change the path to point the location of fbsdk dll we need.
        # The search algorythm used by the loading of libraries in Python does
        # not search in the folder where the executable is located.

        if sys.version_info[0] > 2:
            PyVer = "37"
        else:
            PyVer = "27"

        # On Win32 PATH has to contain the bin/x64 directory, otherwise PySide2
        # won't be able to load their required Qt libraries.
        # The pyfbsdk.pyd file also need to be part of the PATH to be able to load python libraries.
        os.environ['PATH'] = pExePath + os.pathsep + os.path.join(pExePath,"python"+PyVer,"lib" ) + os.pathsep + os.environ['PATH']

        # Some explanation about the sys.path:
        # 1- the dir where python.dll is added
        # 2- Registry are checked (localMachine + localuser) for Software\Python\PythonCore
        # 3- PYTHONPATH env var is checked

        path = []
        AppendIfExists( path, pExePath)
        
        AppendIfExists( path, os.path.join(MB_CONFIG_PATH,"Python") )
        AppendIfExists( path, os.path.join(MB_CONFIG_PATH,"PythonStartup") )
        
        # We now have to setup the search path for our python libraries.
        # By inserting our paths at the beginning of the list we take precedence over
        # any values of PYTHONPATH.
    
        AppendIfExists( path, os.path.join(pExePath,"python"+PyVer,"lib" ) )
        if os.name == 'posix': # Linux
            # on Linux, the Python files are under lib/python2.7 (or 3.7)
            PyVerDot = "3.7" if PyVer == "37" else "2.7"
            AppendIfExists( path, os.path.join(pExePath,"bin" ) )   # This is for pip
            AppendIfExists( path, os.path.join(pExePath,"lib","python"+PyVerDot,"lib-dynload" ) )
            AppendIfExists( path, os.path.join(pExePath,"lib","python"+PyVerDot,"site-packages" ) )
        else:
            AppendIfExists( path, os.path.join(pExePath,"Scripts" ) )   # This is for pip
            AppendIfExists( path, os.path.join(pExePath,"python"+PyVer,"DLLs" ) )
            AppendIfExists( path, os.path.join(pExePath,"python"+PyVer,"site-packages" ) )

        # Support ORSDK plugins which containing Python wrapper
        AppendIfExists( path, os.path.join(pExePath,"plugins") ) 
        
        AppendIfExists( path, os.path.join(MB_CONFIG_PATH,"Scripts") )
        
        startuppath = GetPythonStartupPath(MB_CONFIG_PATH)    
        if startuppath and os.path.exists(startuppath):
            AppendIfExists( path, startuppath)   
    
        for lDefaultSysPath in lDefaultSysPaths:
            AppendIfExists( path, lDefaultSysPath )
        
        sys.path = path
        
        # site is the module responsable for adding 
        # all sites-packages to sys.path. 
        import site
        site.main()

        # We need to change the path to point the location of fbsdk dll we need.
        # The search algorythm used by the loading of libraries in Python does
        # not search in the folder where the executable is located.
        
        # First we have to figure out the exact key for the PATH variable...
        # We cannot assume that the name will be all in uppercase.
        lPathKey = 'PATH'
        
        # This searches the environment for any key that looks like 'PATH'
        # and creates a list of matches... which should contain in theory 0 or 1
        # element.
        lPathKeyList = [pKey for pKey in os.environ if pKey.upper() == lPathKey]
        try:
            pKey = next(iter(lPathKeyList))
            # If we have at least one key, we use it to add the path fbsdk.dll.
            os.putenv( pKey, "%s%s%s" % ( os.environ[pKey], os.path.pathsep, pExePath ) )
        except StopIteration:
            # Otherwise, we add it.
            os.putenv( lPathKey, "%s" % pExePath )
    except:
        # notify any exception that happened during the init script
        print("Error in config script pyfbsdk_init.py")
        import traceback
        print(traceback.print_exc())

