# -*- coding: utf-8 -*-
# Copyright (C) 2000-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Script
#
# Purpose
#    Model python script to be run from an application
#
# Revision Dates
#     8-Aug-2000 (CT)  Creation (factored from Script_Menu_Mgr)
#     8-Aug-2000 (CT)  `Script.__call__' changes sys.path temporarily to
#                      include the script's path
#     8-Aug-2000 (CT)  `add_to_python_path' and `reset_python_path' added
#    14-Sep-2000 (CT)  `error' added
#    22-Feb-2001 (CT)  Use `raise' instead of `raise exc' for re-raise
#     1-Jul-2002 (CT)  `__call__` changed to hide the mdodules `__builtin__`
#                      and `sys` from scripts
#     3-Jul-2002 (CT)  Change of 1-Jul revoked
#    29-Jan-2004 (CT)  `gauge` and `echo`-calls added
#    14-Jun-2004 (GWA) `\n` added to `gauge.echo` calls
#    14-Feb-2006 (CT)  Moved into package `TFL`
#     9-Aug-2006 (CT) `Script.__hash__` changed to return
#                     `hash (self.name)` instead of `id (self)`
#    19-Apr-2020 (CT)  Use "``" for doc strings, not "`'"
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL.Filename              import *
from   _TFL.Functor               import Functor
from   _TFL.Gauge_Logger          import Gauge_Logger
from   _TFL                       import sos
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object

import sys
import traceback

@totally_ordered
class Script (TFL.Meta.Object) :

    def __init__ (self, path, glob_dict = {}, local_dict = {}, name = None, doc = "") :
        fn             = Filename (path, absolute = 1)
        self.path      = fn.name
        self.name      = name or fn.base
        self.dir       = fn.directory
        self.gd        = glob_dict
        self.ld        = local_dict
        self.gauge     = local_dict.get ("gauge")
        if not self.gauge :
            self.gauge = Gauge_Logger ()
        self.old_path  = []
        self._sys_pth  = sys.path [:]
        self.__doc__   = \
            (  doc.replace ("script-name", self.name)
            or ("Run script `%s'" % self.name)
            )
        self.error     = None
    # end def __init__

    def __call__ (self, ld = {}) :
        self.error = None
        gd = self.gd.copy ()
        gd.update         (self.ld)
        gd.update         (ld)
        gd.update \
            ({ "add_to_python_path" : self.add_to_python_path
             , "reset_python_path"  : self.reset_python_path
             }
            )
        try :
            self.old_path = sys.path [:]
            try     :
                sys.path  [0:0] = [self.dir]
                self.gauge.echo   ("Running script %s\n" % self.path)
                execfile          (self.path, gd)
                self.gauge.echo   ("Finished execution of %s\n" % self.path)
            finally :
                sys.path  = self.old_path
        except KeyboardInterrupt as exc :
            raise
        except Exception :
            print ("Error during execution of", self.path)
            traceback.print_exc ()
            self.error = sys.exc_info () [1]
    # end def __call__

    def add_to_python_path (self, path, index = -1) :
        """Add `path` to `sys.path`"""
        sys.path      [index+1 : index+1] = [path]
        self.old_path [index   : index] = [path]
    # end def add_to_python_path

    def reset_python_path (self) :
        """Reset `sys.path` to original value."""
        self.old_path = self._sys_pth [:]
        sys.path      = self._sys_pth [:]
    # end def reset_python_path

    def __eq__ (self, other) :
        return self.name == getattr (other, "name", other)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.name)
    # end def __hash__

    def __lt__ (self, other) :
        return self.name < getattr (other, "name", other)
    # end def __lt__

# end class Script

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Script
