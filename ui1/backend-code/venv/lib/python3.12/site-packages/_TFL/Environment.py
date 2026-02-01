# -*- coding: utf-8 -*-
# Copyright (C) 1998-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Environment
#
# Purpose
#    Provide access to program's environment in os-independent way
#
# Revision Dates
#    17-Apr-1998 (CT)  Creation
#    16-Feb-1999 (CT)  Added `script_name` and `script_path`
#    16-Feb-1999 (CT)  Added `path_of` and `path_contains`
#    17-Feb-1999 (CT)  `path_expanded` added
#    13-Apr-2000 (CT)  `frozen` added
#    14-Apr-2000 (CT)  `module_path` added
#    25-Apr-2000 (CT)  `system` added
#    26-Apr-2000 (CT)  `default_dir` and `home_dir` added
#    13-Sep-2001 (AGO) Workaround for default paths of frozen modules
#    13-May-2003 (CT)  `module_path` changed to look in `sys.modules` first
#                      (can't be bothered to tweak `imp.find_module` for
#                      modules in packages)
#    28-May-2003 (CT)  Use `sos.uname` to find `hostname`
#    25-Jun-2003 (AGO) Fixed preliminarily [4629]
#    11-Jul-2003 (MG)  `try... except` added around `uname` call
#    21-Apr-2004 (CT)  Try to get `home_dir` from `USERPROFILE`, too
#    21-Apr-2004 (MUZ) s/sys/sos/ in sys.environ.get ("USERPROFILE")
#     7-Mar-2005 (MG)  `curdir_pat` fixed
#                      (the old pattern replaces `../../` -> `...`)
#    24-Mar-2005 (CT)  Moved into package `TFL`
#    28-Jul-2005 (CT)  `mailname` added
#     8-Aug-2006 (MSF) fixed [5608]
#    21-Aug-2007 (CED) practically_infinite introduced
#    27-Apr-2010 (CT) `exec_python_startup` added
#    21-Jun-2010 (CT) `py_shell` added
#    28-May-2013 (CT) Use `in`, not `has_key`
#    12-Oct-2014 (CT) Change `exec_python_startup` to `open` with flags `rb`
#    10-Sep-2018 (CT) Add optional argument `depth` to `py_shell`
#    20-Apr-2020 (CT) Remove `module_path`
#    ««revision-date»»···
#--

from   _TFL      import TFL
from   _TFL      import sos

import re
import sys

default_dir = sos.getcwd       ()
home_dir    = sos.environ.get  ("HOME")
if home_dir is None :
    home_dir = sos.environ.get ("USERPROFILE")
    if home_dir is None :
        home_dir = default_dir

if   sos.name == "posix"                         :
    username = sos.environ.get ("USER",         "")
    hostname = sos.environ.get ("HOSTNAME",     "")
    system   = "posix"
elif (sos.name == "nt") or (sos.name == "win32") :
    username = sos.environ.get ("USERNAME",     "")
    hostname = sos.environ.get ("COMPUTERNAME", "")
    system   = "win32"
elif sos.name == "mac"                           :
    username = "" ### ???
    hostname = "" ### ???
    system   = "mac"

if not hostname :
    try :
        hostname = sos.uname () [1]
    except Exception :
        pass

_python_startup_loaded = False

def exec_python_startup () :
    global _python_startup_loaded
    if not _python_startup_loaded :
        ps = sos.environ.get ("PYTHONSTARTUP")
        if ps and sos.path.exists (ps) :
            with open (ps, "rb") as f :
                exec (f.read ())
        _python_startup_loaded = True
# end def exec_python_startup

def mailname () :
    """Returns the mailname of the system the script is running on."""
    try :
        f = open ("/etc/mailname")
    except (IOError, sos.error) :
        pass
    else :
        try :
            return f.read ().strip ()
        except (IOError, sos.error) :
            pass
# end def mailname

def py_shell (glob_dct = None, locl_dct = None, ps1 = None, banner = None, readfunc = None, depth = 0) :
    """Provide a shell to the running python interpreter."""
    import code
    import _TFL.Context
    import _TFL.Caller
    if glob_dct is None :
        glob_dct = TFL.Caller.globals (depth)
    if locl_dct is None :
        locl_dct = TFL.Caller.locals  (depth)
    dct = dict (glob_dct, ** locl_dct)
    exec_python_startup ()
    try :
        import readline
    except ImportError :
        pass
    else :
        import rlcompleter
        readline.set_completer (rlcompleter.Completer (dct).complete)
        readline.parse_and_bind ("tab: complete")
    ### readline checks if sys.stdout is what is used to be,
    ### otherwise it won't do tab-completion
    with TFL.Context.attr_let (sys, stdout = sys.__stdout__) :
        if ps1 is not None :
            sys.ps1 = ps1
        code.interact (banner = banner, readfunc = readfunc, local = dct)
# end def py_shell

def script_name () :
    """Returns the name of the currently running python script."""
    return sos.path.basename (sys.argv [0])
# end def script_name

curdir_pat = re.compile (r"\./\.[^\.]")

def script_path () :
    """Returns the path of the currently running python script."""
    path = sos.path.dirname (sys.argv [0])
    path = curdir_pat.sub   (".", path) ### hack around case "./."
    if not path :
        path = sos.curdir
    return path
# end def script_path

def path_expanded (filename) :
    """Returns filename expanded by `path_of (filename)`.

       If no path is found for `filename`, it is returned as is.
    """
    path = path_of (filename)
    if path :
        return sos.path.join (path, filename)
    else :
        return filename
# end def path_expanded

def path_of (filename) :
    """Returns path where `filename` resides. `path_of` looks in the
       directory of the current python-script and in the python path and
       returns the first directory containing `filename`.
    """
    sc_path = script_path ()
    if path_contains (sc_path, filename) :
        return sc_path
    for path in sys.path :
        if path_contains (path, filename) :
            return path
    return ""
# end def path_of

def path_contains (path, filename) :
    """Returns `path` if there exists a file named `filename` there."""
    if sos.path.isfile (sos.path.join (path, filename)) :
        return path
    else :
        return ""
# end def path_contains

def frozen () :
    """Returns true if application is frozen"""
    import sys
    return hasattr (sys, "frozen")
# end def frozen

practically_infinite = int ((1 << 31) - 1)

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Environment
