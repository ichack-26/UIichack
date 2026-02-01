# -*- coding: utf-8 -*-
# Copyright (C) 2003-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    module_copy
#
# Purpose
#    Return an independent copy of a module
#
# Revision Dates
#    17-Dec-2003 (CT) Creation
#    23-Apr-2020 (CT) Use `importlib.import_module`, not `__import__`
#    ««revision-date»»···
#--

from   _TFL       import TFL

from   contextlib import contextmanager

import importlib
import sys

@contextmanager
def _save_sys_modules (name) :
    if name in sys.modules :
        original = sys.modules [name]
        del sys.modules [name]
        try :
            yield
        finally :
            sys.modules [name] = original
    else :
        yield
        del sys.modules [name]
# end def _save_sys_modules

def module_copy (name, ** kw) :
    """Return an independent copy of the module with `name` and assign all
       elements of `kw` to the result.
    """
    with _save_sys_modules (name) :
        result = importlib.import_module (name)
    for k, v in kw.items () :
        setattr (result, k, v)
    return result
# end def module_copy

def import_module_copy (name, as_name, ** kw) :
    """Put a module_copy with `name` into `sys.modules`."""
    result = sys.modules [as_name] = module_copy (name, ** kw)
    return result
# end def import_module_copy

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ module_copy
