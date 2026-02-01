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
#    TFL.Infinity
#
# Purpose
#    Provide an instance that is larger than any number
#
# Revision Dates
#    29-Jun-2016 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _TFL.I18N                  import _

import _TFL._Meta.Object

class _Infinity_ (TFL.Meta.Object) :
    r"""Instance that is larger than any number.

    >>> import operator
    >>> map = dict \
    ...     ( eq  = "==", ne = "!=", le = "<=", lt = "<", ge = ">=", gt = ">"
    ...     , add = "+", floordiv = "//", sub = "-", mul = "*", truediv = "/"
    ...     )
    >>> fmt = "%-8s %-2s %-8s : %s"
    >>> for v in (Infinity, 1, 42.0) :
    ...     for name, sym in sorted (pyk.iteritems (map)) :
    ...         op = getattr (operator, name)
    ...         try :
    ...            r1 = fmt % (v, sym, Infinity, op (v, Infinity))
    ...         except ArithmeticError as exc :
    ...             r1 = "%-20s : %s" % (exc.__class__.__name__, exc)
    ...         print (r1)
    ...         if v is not Infinity :
    ...             try :
    ...                 r2 = fmt % (Infinity, sym, v, op (Infinity, v))
    ...             except ArithmeticError as exc :
    ...                 r2 = "%-20s : %s" % (exc.__class__.__name__, exc)
    ...             print (r2)
    ∞        +  ∞        : ∞
    ∞        == ∞        : True
    ArithmeticError      : Cannot divide ∞ by ∞
    ∞        >= ∞        : True
    ∞        >  ∞        : False
    ∞        <= ∞        : True
    ∞        <  ∞        : False
    ∞        *  ∞        : ∞
    ∞        != ∞        : False
    ∞        -  ∞        : ∞
    ArithmeticError      : Cannot divide ∞ by ∞
    1        +  ∞        : ∞
    ∞        +  1        : ∞
    1        == ∞        : False
    ∞        == 1        : False
    ArithmeticError      : Cannot divide 1 by ∞
    ∞        // 1        : ∞
    1        >= ∞        : False
    ∞        >= 1        : True
    1        >  ∞        : False
    ∞        >  1        : True
    1        <= ∞        : True
    ∞        <= 1        : False
    1        <  ∞        : True
    ∞        <  1        : False
    1        *  ∞        : ∞
    ∞        *  1        : ∞
    1        != ∞        : True
    ∞        != 1        : True
    1        -  ∞        : ∞
    ∞        -  1        : ∞
    ArithmeticError      : Cannot divide 1 by ∞
    ∞        /  1        : ∞
    42.0     +  ∞        : ∞
    ∞        +  42.0     : ∞
    42.0     == ∞        : False
    ∞        == 42.0     : False
    ArithmeticError      : Cannot divide 42.0 by ∞
    ∞        // 42.0     : ∞
    42.0     >= ∞        : False
    ∞        >= 42.0     : True
    42.0     >  ∞        : False
    ∞        >  42.0     : True
    42.0     <= ∞        : True
    ∞        <= 42.0     : False
    42.0     <  ∞        : True
    ∞        <  42.0     : False
    42.0     *  ∞        : ∞
    ∞        *  42.0     : ∞
    42.0     != ∞        : True
    ∞        != 42.0     : True
    42.0     -  ∞        : ∞
    ∞        -  42.0     : ∞
    ArithmeticError      : Cannot divide 42.0 by ∞
    ∞        /  42.0     : ∞

    """

    def __add__ (self, rhs) :
        return Infinity
    __radd__ = __add__ # end def

    def __eq__ (self, rhs) :
        return is_infinite (rhs)
    __le__ = __eq__ # end def

    def __floordiv__ (self, rhs) :
        if is_infinite (rhs) :
            raise ArithmeticError ("Cannot divide %s by %s" % (self, rhs))
        return Infinity
    __truediv__ = __floordiv__ # end def

    def __ge__ (self, rhs) :
        return True
    # end def __ge__

    def __gt__ (self, rhs) :
        return not is_infinite (rhs)
    # end def __gt__

    def __hash__ (self) :
        return id (self)
    # end def __hash__

    def __lt__ (self, rhs) :
        return False
    # end def __lt__

    def __mul__ (self, rhs) :
        return Infinity
    __rmul__ = __mul__ # end def

    def __rdiv__ (self, rhs) :
        raise ArithmeticError ("Cannot divide %s by %s" % (rhs, Infinity))
    __rfloordiv__ = __rtruediv__ = __rdiv__ # end def

    def __repr__ (self) :
        return pyk.reprify (_ ("Infinity"))
    # end def __repr__

    def __str__ (self) :
        return "∞"
    # end def __str__

    def __sub__ (self, rhs) :
        return Infinity
    __rsub__ = __sub__ # end def

# end class _Infinity_

Infinity = _Infinity_ ()
"""Instance that is larger than any number."""

def is_infinite (v) :
    """Return True if `v` is infinite."""
    return isinstance (v, _Infinity_)
# end def is_infinite

__all__ = __sphinx__members = ("Infinity", "is_infinite")

if __name__ != "__main__" :
    TFL._Export (* __all__)
### __END__ TFL.Infinity
