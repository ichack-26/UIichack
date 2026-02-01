# -*- coding: utf-8 -*-
# Copyright (C) 2000-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.object_globals
#
# Purpose
#    Return the globals of an object or class
#
# Revision Dates
#     6-Mar-2000 (CT) Creation
#     6-Nov-2002 (CT) `assert` removed from `class_globals`
#    14-Feb-2006 (CT) Moved into package `TFL`
#    ««revision-date»»···
#--

from   _TFL import TFL

import sys

def object_globals (o) :
    """Return the globals associated to object `o`."""
    return object_module (o).__dict__
# end def object_globals

def class_globals (c) :
    """Return the globals associated to class `c`."""
    return class_module (c).__dict__
# end def class_globals

def class_module (c) :
    """Return the module defining the class `c`."""
    return sys.modules [c.__module__]
# end def class_module

object_module = class_module

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.object_globals
