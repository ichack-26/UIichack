# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Attr_Mapper
#
# Purpose
#    Allow access to attributes of an object with different names
#
# Revision Dates
#     5-Mar-2010 (CT) Creation
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL               import TFL
from   _TFL.predicate     import callable

import _TFL._Meta.Object

class Attr_Mapper (TFL.Meta.Object) :
    """Allow access to attributes of an object with different names"""

    def __init__ (self, ** kw) :
        self._map = kw
    # end def __init__

    def __call__ (self, obj, name) :
        mapped = self._map.get (name, name)
        if mapped is not None :
            if callable (mapped) :
                return mapped (obj)
            else :
                return getattr (obj, mapped)
        raise AttributeError (name)
    # end def __call__

# end class Attr_Mapper

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Attr_Mapper
