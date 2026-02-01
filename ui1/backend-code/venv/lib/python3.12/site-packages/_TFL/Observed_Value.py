# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Observed_Value
#
# Purpose
#    Encapsulate a value and inform observers about changes of that value
#
# Revision Dates
#     5-Jan-2006 (CT) Creation
#    21-Jan-2006 (MG) Support for `kw` added
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    31-Mar-2020 (CT) Def `__bool__`, not `__nonzero__` (Py-3)
#    ««revision-date»»···
#--

from   _TFL        import TFL

import _TFL._Meta.Object

class Observed_Value (TFL.Meta.Object) :
    """Value that informs registered observers about changes.

       >>> x = Observed_Value (0)
       >>> def obs (ov, nv) :
       ...     print ("%s changed to %s" % (ov, nv))
       ...
       >>> x.register_observer (obs)
       >>> x.value
       0
       >>> x.value = 0
       >>> x.value = 42
       0 changed to 42
       >>> x.value = 0
       42 changed to 0
       >>> x.value = 0
    """

    value = property (lambda s : s._value, lambda s, v : s._set (v))

    def __init__ (self, value = None, ** kw) :
        self._value    = value
        self.observers = []
        self.kw        = kw
    # end def __init__

    def deregister_observer (self, * o) :
        to_remove = set (o)
        self.observers = [o for o in self.observers if o not in to_remove]
    # end def deregister_observer

    def register_observer (self, * o) :
        self.observers.extend (o)
    # end def register_observer

    def _set (self, value) :
        if value != self._value :
            for o in self.observers :
                o (self, value, ** self.kw)
        self._value = value
    # end def _set

    def __getattr__ (self, name) :
        if name not in self.kw :
            return getattr (self._value, name)
        return self.kw [name]
    # end def __getattr__

    def __float__ (self) :
        return float (self._value)
    # end def __float__

    def __int__ (self) :
        return int (self._value)
    # end def __int__

    def __len__ (self) :
        return len (self._value)
    # end def __len__

    def __long__ (self) :
        return long (self._value)
    # end def __long__

    def __bool__ (self) :
        return bool (self._value)
    # end def __bool__

    def __repr__ (self) :
        return repr (self._value)
    # end def __repr__

    def __str__ (self) :
        return str (self._value)
    # end def __str__

# end class Observed_Value

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Observed_Value
