# -*- coding: utf-8 -*-
# Copyright (C) 2005-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Apply_All
#
# Purpose
#    Class transparently applying method calls to a set of objects
#
# Revision Dates
#    20-Feb-2005 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._Meta.Object

class Apply_All (TFL.Meta.Object) :
    """Class transparently applying method calls to a set of objects.

       >>> l1  = list (range (5))
       >>> l2  = ["f", "b", "c", "a"]
       >>> all = Apply_All (l1, l2)
       >>> all._receivers
       ([0, 1, 2, 3, 4], ['f', 'b', 'c', 'a'])
       >>> all.sort ()
       >>> all._receivers
       ([0, 1, 2, 3, 4], ['a', 'b', 'c', 'f'])
       >>> all.count ("a")
       [0, 1]
       >>> all.reverse ()
       >>> all._receivers
       ([4, 3, 2, 1, 0], ['f', 'c', 'b', 'a'])
       >>> all.pop ()
       [0, 'a']
       >>> all._receivers
       ([4, 3, 2, 1], ['f', 'c', 'b'])
    """

    def __init__ (self, * receivers) :
        self._receivers = receivers
    # end def __init__

    def _apply (self, name, * args, ** kw) :
        result = []
        for r in self._receivers :
            f = getattr (r, name)
            r = f (* args, ** kw)
            if r is not None :
                result.append (r)
        return result or None
    # end def _apply

    def __getattr__ (self, name) :
        return lambda * args, ** kw : self._apply (name, * args, ** kw)
    # end def __getattr__

# end class Apply_All

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ Apply_All
