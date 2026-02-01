# -*- coding: utf-8 -*-
# Copyright (C) 2004-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Proxy
#
# Purpose
#    Generic proxy
#
# Revision Dates
#    19-Apr-2004 (CT) Creation
#    20-Apr-2004 (CT) Magic name check removed from `__getattr__` (for
#                     new-style classes, Python doesn't look at instance for
#                     magic methods)
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   _TFL              import TFL
import _TFL._Meta.Object

class Proxy (TFL.Meta.Object) :
    """Proxy for some other object. All attributes not found in proxy will
       by taken from proxied object.
    """

    def __init__ (self, proxied, ** kw) :
        self.__dict__.update (kw)
        self._proxied = proxied
    # end def __init__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self._proxied, name)
    # end def __getattr__

# end class Proxy

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ Proxy
