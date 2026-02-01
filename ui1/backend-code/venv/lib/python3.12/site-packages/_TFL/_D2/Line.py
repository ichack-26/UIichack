# -*- coding: utf-8 -*-
# Copyright (C) 2002-2019 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.D2.Line
#
# Purpose
#    Classes modeling lines in 2D space
#
# Revision Dates
#    24-Jun-2002 (CT)  Creation (factored from Two_Dim)
#    24-Mar-2003 (CT)  Converted to new-style class
#    11-Jun-2003 (CT)  s/!= None/is not None/
#    11-Jun-2004 (GKH) Deprecation warning removed [10140]
#    28-Sep-2004 (CT)  Use `isinstance` instead of type comparison
#     5-Apr-2005 (CT)  Breakage in unit-test introduced by GKH removed
#    20-Aug-2012 (CT) Add `transformed`
#    20-Aug-2012 (CT) Sort methods alphabetically
#    21-Aug-2012 (CT) Add `__iter__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    24-Nov-2019 (CT) Fix typo in `Normal_Form.__repr__` (Py 3.8 warning)
#                     + `%` operator was missing between format string and tuple
#    ««revision-date»»···
#--

from   _TFL           import TFL
from   _TFL._D2       import D2
import _TFL._D2.Point
import _TFL._Meta.Object
import math

class Normal_Form (TFL.Meta.Object) :
    """Normal form of straight line: `a*x + b*y + c = 0`"""

    def __init__ (self, line) :
        self.line = line
        self.a    = line.head.y - line.tail.y
        self.b    = line.tail.x - line.head.x
        self.c    = line.head.x * line.tail.y - line.tail.x * line.head.y
    # end def __init__

    def intersection (self, other) :
        """Returns intersection between the two lines in normal forms
           (None, if parallel).
        """
        try :
            x       = float (self.b * other.c - self.c * other.b)
            y       = float (self.c * other.a - self.a * other.c)
            divisor = float (self.a * other.b - self.b * other.a)
            return D2.Point (x / divisor, y / divisor)
        except ArithmeticError :
            return None
    # end def intersection

    def __repr__ (self) :
        return "%s %r" % (self.__class__.__name__, self.line)
    # end def __repr__

    def __str__ (self) :
        return "(%s, %s, %s)" % (self.a, self.b, self.c)
    # end def __str__

# end class Normal_Form

class Line (TFL.Meta.Object) :
    """Model a finite straight line in 2-dimensional space.

       >>> l = Line (D2.Point (0.0, 0.0), D2.Point (5.0, 5.0))
       >>> m = Line (D2.Point (0.0, 5.0), D2.Point (5.0, 0.0))
       >>> n = Line (D2.Point (0.0, 0.0), D2.Point (5.0, 0.0))
       >>> m.contains (l.point (0.5))
       1
       >>> l.distance (D2.Point (2.5, 2.5))
       0.0
       >>> n.distance (D2.Point (2.5, 2.5))
       2.5
       >>>
       >>> l.intersection (m)
       Point (2.5, 2.5)
       >>> l.length () == m.length ()
       1
       >>> print ("%5.2f" % l.length ())
        7.07
       >>> l.distance (D2.Point (5.0, 0.0)) - (l.length () / 2) < 1.e-12
       1
       >>> l.point (0.5)
       Point (2.5, 2.5)
       >>> l.tail * 0.5
       Point (2.5, 2.5)
       >>> l.tail + l.tail
       Point (10.0, 10.0)
    """

    def __init__ (self, head = (0.0, 0.0), tail = (1.0, 1.0)) :
        if isinstance (head, (list, tuple)) :
            head = D2.Point (* head)
        if isinstance (tail, (list, tuple)) :
            tail = D2.Point (* tail)
        self.head = head
        self.tail = tail
    # end def __init__

    def contains (self, p) :
        return (not self.distance (p)) and self._contains (p)
    # end def contains

    def distance (self, p) :
        """Returns the distance between point `p` and the line `self`.
           Attention: This method calculates only the distance to the
           INFINITE line. That means, if the distance to
           the point lies on a line normal that is outside [head, tail] of
           the line than this not mathematically correct, because the nearest
           point of the line is head or tail in this case and this distance
           is longer than the distance to the infinite line!
        """
        nf = Normal_Form (self)
        return ( abs       (float (nf.a * p.x  + nf.b * p.y  + nf.c))
               / math.sqrt (float (nf.a * nf.a + nf.b * nf.b))
               )
    # end def distance

    def intersection (self, other) :
        p = Normal_Form (self).intersection (Normal_Form (other))
        if p is not None :
            if self._contains (p) and other._contains (p) : return p
        return None
    # end def intersection

    def length (self) :
        return (self.tail - self.head).norm
    # end def length

    def point (self, shift) :
        """Returns the point at the linear position `shift` between the head
           and the tail of the line.
        """
        return (self.head * (1. - shift)) + (self.tail * shift)
    # end def point

    def shift (self, right) :
        """Shifts the complete line by vector `right`."""
        self.head.shift (right)
        self.tail.shift (right)
        return self
    # end def shift

    def transformed (self, affine) :
        """Return another point whose coordinateare derived via `affine`
           transform from `self`.
        """
        return self.__class__ \
            (self.head.transformed (affine), self.tail.transformed (affine))
    # end def transformed

    def _contains (self, p) :
        v = p         - self.tail
        u = self.head - self.tail
        r = 1
        for i in (0, 1) :
            if u [i] != 0 : r = r and (0.0 <= v [i] / u [i] <= 1.0)
            else          : r = r and (v [i] == 0)
        return r
    # end def _contains

    def __iter__ (self) :
        yield self.head
        yield self.tail
    # end def __iter__

    def __repr__ (self) :
        return "%s %s" % (self.__class__.__name__, str (self))
    # end def __repr__

    def __str__ (self) :
        return "(%s, %s)" % (self.head, self.tail)
    # end def __str__

# end class Line

if __name__ != "__main__" :
    D2._Export ("*")
### __END__ Line
