# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Meta.Once_Property
#
# Purpose
#    Define a property which value is computed once per instance
#
# Revision Dates
#     9-Nov-2007 (CT) Creation
#     4-Feb-2009 (CT) Documentation improved
#    24-Sep-2009 (CT) `_del` added to `Once_Property`
#     7-Oct-2009 (CT) `Once_Property` implemented as wrapper around
#                     `Lazy_Property`
#    26-Jun-2013 (CT) Add `Class_and_Instance_Once_Property`
#    16-Oct-2015 (CT) Add `__future__` imports
#     1-Jun-2016 (CT) Add `Once_Property_NI`
#    25-Jul-2016 (CT) Add `Class_and_Instance_Once_Property_NI`
#    ««revision-date»»···
#--

from   _TFL             import TFL
import _TFL._Meta.Property

def Once_Property (f) :
    """Decorator returning a `Lazy_Property`."""
    return TFL.Meta.Lazy_Property (f.__name__, f, f.__doc__)
# end def Once_Property

def Once_Property_NI (f) :
    """Decorator returning a `Lazy_Property_NI`."""
    return TFL.Meta.Lazy_Property_NI (f.__name__, f, f.__doc__)
# end def Once_Property_NI

def Class_and_Instance_Once_Property (f) :
    """Decorator returning a `Class_and_Instance_Lazy_Property`."""
    return TFL.Meta.Class_and_Instance_Lazy_Property (f.__name__, f, f.__doc__)
# end def Class_and_Instance_Once_Property

def Class_and_Instance_Once_Property_NI (f) :
    """Decorator returning a `Class_and_Instance_Lazy_Property`."""
    return TFL.Meta.Class_and_Instance_Lazy_Property_NI \
        (f.__name__, f, f.__doc__)
# end def Class_and_Instance_Once_Property_NI

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.Once_Property
