# -*- coding: utf-8 -*-
# Copyright (C) 2016 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.FO
#
# Purpose
#    Formatter for objects and their attributes
#
# Revision Dates
#     9-Sep-2016 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL        import TFL
from   _TFL.pyk    import pyk

import _TFL._Meta.Object
import _TFL.Accessor

class FO (TFL.Meta.Object) :
    """Formatter for objects and their attributes."""

    def __init__ (self, obj) :
        self._obj_ = obj
    # end def __init__

    def _attr_as_str (self, obj, name, value) :
        return "%s" % (value, )
    # end def _attr_as_str

    def __call__ (self, name) :
        getter   = getattr (TFL.Getter, name)
        obj      = self._obj_
        value    = getter (obj)
        return self._attr_as_str (obj, name, value)
    # end def __call__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws
            ### `ValueError`
            return getattr (self.__super, name)
        result = self (name)
        if "." not in name :
            setattr (self, name, result)
        return result
    # end def __getattr__

    def __getitem__ (self, key) :
        try :
            return self.__getattr__ (key)
        except AttributeError :
            raise KeyError (key)
    # end def __getitem__

    def __str__ (self) :
        return "%s" % (self._obj_, )
    # end def __str__

# end class FO

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.FO
