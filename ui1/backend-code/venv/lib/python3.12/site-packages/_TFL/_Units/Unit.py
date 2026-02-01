# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Unit
#
# Purpose
#    Model a unit
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    17-Feb-2017 (CT) Add `from_base`, `__call__`, `__hash__`, `__rmul__`
#    17-Feb-2017 (CT) Add `Bound_Unit`
#    17-Feb-2017 (CT) Add `offset`
#    17-Feb-2017 (CT) Add `aliases`
#    ««revision-date»»···
#--

from   _TFL import TFL
from   _TFL.pyk import pyk

from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL._Units

@totally_ordered
class Unit (TFL.Meta.Object) :
    """Model a unit kind"""

    class Bound_Unit (TFL.Meta.Object) :

        def __init__ (self, unit_kind_cls, unit) :
            self.unit_kind_cls = unit_kind_cls
            self.unit = unit
        # end def __init__

        def __call__ (self, value) :
            return self.unit_kind_cls (value, self.unit)
        # end def __call__

        def __mul__ (self, rhs) :
            return self.unit * getattr (rhs, "unit", rhs)
        # end def __mul__

        __rmul__ = __mul__

        def __pow__ (self, rhs) :
            return self.unit ** rhs
        # end def __pow__

        def __truediv__ (self, rhs) :
            return self.unit / getattr (rhs, "unit", rhs)
        # end def __truediv__

    # end class Bound_Unit

    def __init__ \
          (self, name, factor = 1.0, abbr = None, offset = 0.0, aliases = ()) :
        self.name    = name
        self.factor  = float (factor)
        self.abbr    = abbr
        self.offset  = offset
        self.aliases = aliases
    # end def __init__

    def from_base (self, value) :
        """Convert `value` of `base_unit` into unit `self`."""
        return value / self.factor - self.offset
    # end def __call__

    def __call__ (self, value) :
        """Convert `value` of `base_unit` into unit `self`."""
        return value * self
    # end def __call__

    def __eq__ (self, rhs) :
        try :
            rhs = rhs.name
        except AttributeError :
            pass
        return self.name == rhs
    # end def __eq__

    def __float__ (self) :
        return self.factor
    # end def __float__

    def __hash__ (self) :
        return hash (self.name)
    # end def __hash__

    def __lt__ (self, rhs) :
        try :
            rhs = rhs.factor
        except AttributeError :
            pass
        return self.factor > rhs
    # end def __lt__

    def __mul__ (self, rhs) :
        try :
            rhs = rhs.factor
        except AttributeError :
            pass
        return (rhs + self.offset) * self.factor
    # end def __mul__

    __rmul__ = __mul__

    def __pow__ (self, rhs) :
        return self.factor ** rhs
    # end def __pow__

    def __repr__ (self) :
        if self.offset :
            return "%s = %+g x %s" % (self.name, self.offset, self.factor)
        else :
            return "%s = %s" % (self.name, self.factor)
    # end def __repr__

    def __truediv__ (self, rhs) :
        try :
            rhs = rhs.factor
        except AttributeError :
            pass
        return self.factor / rhs
    # end def __truediv__

# end class Unit

if __name__ != "__main__" :
    TFL.Units._Export ("Unit")
### __END__ TFL.Units.Unit
