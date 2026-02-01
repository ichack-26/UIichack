# -*- coding: utf-8 -*-
# Copyright (C) 2002-2009 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Module
#
# Purpose
#    Convenience functions for accessing features of python modules
#
# Revision Dates
#    12-Mar-2002 (CT) Creation
#    11-Sep-2009 (CT) `names_of` converted to generator
#    ««revision-date»»···
#--

from _TFL import TFL

def module_of (object) :
    """Returns the name of the module defining `object`, if possible.

       `module_of` works for classes, functions, and class proxies.
    """
    try :
        object = object.__dict__ ["Essence"]
    except (AttributeError, KeyError, TypeError) :
        pass
    result = getattr (object, "__module__", None)
    if not result :
        globals = getattr (object, "func_globals", None)
        if globals :
            result = globals.get ("__name__")
    return result
# end def module_of

def defined_by (object, module) :
    """Returns true, if `object` is defined by `module`, false otherwise.

       Unfortunately, this currently only works for `object`s for which
       `module_of` returns a non-None result.
    """
    return module_of (object) == module.__name__
# end def defined_by

def names_of (module) :
    """Returns the names of all functions and classes defined by `module`
       itself.

       Unfortunately, this currently only returns objects for which
       `module_of` returns a non-None result.
    """
    for n, f in module.__dict__.items () :
        if defined_by (f, module) :
            yield n
# end def names_of

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.Module
