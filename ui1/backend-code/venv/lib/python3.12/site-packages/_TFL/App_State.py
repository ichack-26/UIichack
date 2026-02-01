# -*- coding: utf-8 -*-
# Copyright (C) 2000-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.App_State
#
# Purpose
#    Encapsulate the persistent state of an interactive application
#
# Revision Dates
#    25-Apr-2000 (CT)  Creation
#     3-May-2000 (CT)  Import from `WindowsRegistry' moved into `try' block
#    11-May-2000 (RM)  Printing of traceback removed in load
#    12-May-2000 (CT)  Printing of traceback reintroduced in load (avoid
#                      syntax error)
#    13-Jul-2000 (CT)  `win32api.error' exception handlers added
#     8-Aug-2000 (CT)  Pickle before opening file
#    16-Aug-2000 (CT)  `if state' added to win32 version of `load'
#    22-Feb-2001 (CT)  Use `raise' instead of `raise exc' for re-raise
#    14-Sep-2001 (CT)  `__setattr__` added
#     6-Nov-2001 (CT)  Import of `traceback` moved from exception handler to
#                      global scope
#     5-Dec-2001 (MG)  Import of `WindowsRegistry` moved out of functions (not
#                      allowed in future versions of python)
#    10-Mar-2003 (AGO) `__repr__` added
#    20-Mar-2003 (CT)  Derive from `TFL.Meta.Object`
#    31-Jan-2005 (CT)  Calls to `pickle.dumps` changed to avoid
#                      DeprecationWarning
#                          The 'bin' argument to Pickler() is deprecated
#    20-May-2005 (CT)  Moved to TFL
#    19-Aug-2008 (CT)  `product_name` added as optional paramter to `__init__`
#    17-Dec-2009 (CT)  Use `pickle` instead of `cPickle` (3-compatibility)
#    28-Oct-2015 (CT) Use `pyk.pickle_protocol`
#    ««revision-date»»···
#--

from   _TFL                import TFL
from   _TFL                import sos
from   _TFL.pyk            import pyk

import _TFL._Meta.Object
import _TFL.Environment

import sys
import traceback

try :
    from WindowsRegistry import *
except (ImportError, SyntaxError) :
    pass

class App_State (TFL.Meta.Object) :
    """Encapsulate the persistent state of an interactive application."""

    product_name = None ### redefine in descendents or pass into constructor
    bin          = False

    def __init__ (self, product_name = None, ** kw) :
        if product_name is not None :
            self.__dict__ ["product_name"] = product_name
        assert (self.product_name)
        self.__dict__ ["state"] = kw.copy ()
    # end def __init__

    def __getattr__ (self, name) :
        try :
            return self.state [name]
        except KeyError :
            raise AttributeError (name)
    # end def __getattr__

    def __setattr__ (self, name, value) :
        if name in self.state :
            self.state [name] = value
        else :
            raise AttributeError (name)
    # end def __setattr__

    def __repr__ (self) :
        return "App_State %s" % self.product_name
    # end def __repr__

    def add (self, ** kw) :
        state = kw.copy ()
        state.update (self.state)
        self.__dict__ ["state"] = state
    # end def add

    if TFL.Environment.system == "win32" :
        def foldername (self) :
            return r"Software\%s" % self.product_name
        # end def foldername

        def load (self) :
            """Load persistent application state from registry"""
            try :
                state = RegistryValue \
                    ( r"%s\%s" % (self.foldername (), "state")
                    , root = win32con.HKEY_CURRENT_USER
                    )
                if state.value :
                    state = pyk.pickle.loads (state.value)
                    self.state.update (state)
            except (SystemExit, KeyboardInterrupt) :
                raise
            except win32api.error :
                pass
            except :
                traceback.print_exc ()
        # end def load

        def dump (self) :
            """Dump persistent application state to registry"""
            try :
                reg_entry = RegistryFolder \
                    ( r"%s" % self.foldername ()
                    , root = win32con.HKEY_CURRENT_USER
                    )
                state     = pyk.pickle.dumps \
                    (self.state, self.bin, pyk.pickle_protocol)
                reg_entry.write ("state", state)
            except (SystemExit, KeyboardInterrupt) :
                raise
            except win32api.error as exc :
                print ("Could not write application state to Windows registry")
                print (exc)
            except :
                traceback.print_exc ()
        # end def dump
    else :
        def filename (self) :
            return sos.path.join \
                (TFL.Environment.home_dir, ".%s.state" % (self.product_name, ))
        # end def filename

        def load (self) :
            """Load persistent application state from rc file"""
            try :
                with open (self.filename (), "rb") as file :
                    state = pyk.pickle.load (file)
                    self.state.update (state)
            except (SystemExit, KeyboardInterrupt) :
                raise
            except :
                pass
        # end def load

        def dump (self) :
            """Dump persistent application state to rc file"""
            try :
                state = pyk.pickle.dumps \
                    (self.state, self.bin, pyk.pickle_protocol)
                with open (self.filename (), "wb") as file :
                    file.write (state)
            except (SystemExit, KeyboardInterrupt) :
                raise
            except :
                traceback.print_exc ()
        # end def dump
    # end if TFL.Environment.system == "win32"

# end class App_State

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.App_State
