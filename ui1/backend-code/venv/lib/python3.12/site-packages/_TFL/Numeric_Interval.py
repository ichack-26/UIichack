# -*- coding: utf-8 -*-
# Copyright (C) 2003-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Numeric_Interval
#
# Purpose
#    Model a numeric interval
#
# Revision Dates
#    18-Nov-2003 (CT) Creation
#    27-Nov-2003 (CT) `shifted` added
#    20-Feb-2004 (CT) `doctest` added
#    23-Feb-2004 (CT) `union`   added
#     4-Mar-2004 (CED) `difference` fixed
#     8-Mar-2004 (CED) Doctest fixed according to last change
#     9-Mar-2004 (CT)  `_doc_test` changed to not use `import`
#     1-Mar-2007 (CT)  Adapted to signature change of `DL_List`
#    29-Mar-2007 (CED) `converted` added
#    11-Apr-2007 (CT)  `__iter__` added and used (in `converted`)
#    11-Apr-2007 (CT)  Doctest for `converted` added (Bad, Chris, bad)
#    17-Apr-2007 (CT)  `__mod__` added
#    11-May-2007 (CT)  `set` added
#    20-Mar-2009 (CT)  Use `practically_infinite` instead of sys.maxint
#    ««revision-date»»···
#--

from   _TFL                 import TFL
from   _TFL.pyk             import pyk

from   _TFL.Environment           import practically_infinite as infinite
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL.DL_List
import _TFL.predicate
import _TFL._Meta.Object

@totally_ordered
class Numeric_Interval (TFL.Meta.Object) :
    """Class for modelling a numeric interval.

       >>> i = Numeric_Interval (0, 100)
       >>> j = Numeric_Interval (100, 200)
       >>> k = Numeric_Interval (20, 50)
       >>> l = Numeric_Interval (210, 250)
       >>> m = Numeric_Interval (240, 260)
       >>> n = Numeric_Interval (280, 300)
       >>> i, j, k
       ((0, 100), (100, 200), (20, 50))
       >>> i.after (i), i.after (j), j.after (j), j.after (i)
       (False, False, False, True)
       >>> i.before (i), i.before (j), j.before (j), j.before (i)
       (False, True, False, False)
       >>> i.contains (i), i.contains (j), i.contains (k), j.contains (k)
       (True, False, True, False)
       >>> i.contains_point (100), i.contains_point (20), j.contains_point (20)
       (True, True, False)
       >>> i.difference (i), i.difference (j), i.difference (k)
       ([], [(0, 100)], [(0, 20), (50, 100)])
       >>> i.intersection (i), i.intersection (j), i.intersection (k)
       ((0, 100), (100, 100), (20, 50))
       >>> i.overlaps (i), i.overlaps (j), i.overlaps (k), j.overlaps (k)
       (True, False, True, False)
       >>> i.shifted (20)
       (20, 120)
       >>> i [0], i [1]
       (0, 100)
       >>> Numeric_Interval.union ()
       []
       >>> Numeric_Interval.union (m)
       [(240, 260)]
       >>> Numeric_Interval.union (i, k)
       [(0, 100)]
       >>> i, j, k, l, m, n
       ((0, 100), (100, 200), (20, 50), (210, 250), (240, 260), (280, 300))
       >>> Numeric_Interval.union (i, j, k, l, m, n)
       [(0, 200), (210, 260), (280, 300)]
       >>> j.converted (lambda v : v // 3), l.converted (lambda v : v // 2)
       ((33, 66), (105, 125))

       >>> j % 50, k % 10, l % 50, m % 50, n % 250
       ((0, 50), (0, 10), (10, 50), (40, 10), (30, 50))
    """

    format = "(%s, %s)"

    def __init__ (self, lower = infinite, upper = - infinite) :
        self.lower = lower
        self.upper = upper
    # end def __init__

    length = property (lambda s : s.upper - s.lower)

    def after (self, other) :
        return self.lower >= other.upper
    # end def after

    def before (self, other) :
        return self.upper <= other.lower
    # end def before

    def contains (self, other) :
        return self.lower <= other.lower <= other.upper <= self.upper
    # end def contains

    def contains_point (self, point) :
        return self.lower <= point <= self.upper
    # end def contains_point

    def converted (self, conversion_fct) :
        return self.__class__ (* (conversion_fct (i) for i in self))
    # end def converted

    def copy (self) :
        return self.__class__ (self.lower, self.upper)
    # end def copy

    def difference (self, other) :
        result = []
        isect  = self.intersection (other)
        if isect :
            r = self.__class__ (self.lower, isect.lower)
            if r :
                result.append (r)
            r = self.__class__ (isect.upper, self.upper)
            if r :
                result.append (r)
        else :
            result = [self]
        return result
    # end def difference

    def intersection (self, other) :
        return self.__class__ \
            (max (self.lower, other.lower), min (self.upper, other.upper))
    # end def intersection

    def intersect (self, other) :
        self.lower = max (self.lower, other.lower)
        self.upper = min (self.upper, other.upper)
    # end def intersect

    def is_empty (self) :
        return self.lower == self.upper
    # end def is_empty

    def is_valid (self) :
        return self.lower <= self.upper
    # end def is_valid

    def overlaps (self, other) :
        return not (self.upper <= other.lower or self.lower >= other.upper)
    # end def overlaps

    def set (self, lower, upper) :
        self.lower = lower
        self.upper = upper
    # end def set

    def shift (self, delta) :
        self.lower += delta
        self.upper += delta
    # end def shift

    def shifted (self, delta) :
        return self.__class__ (self.lower + delta, self.upper + delta)
    # end def shifted

    def __bool__ (self) :
        return self.length > 0
    # end def __bool__

    def __eq__ (self, other) :
        try :
            return (self.lower, self.upper) == (other.lower, other.upper)
        except AttributeError :
            return (self.lower, self.upper) == other
    # end def __eq__

    def __getitem__ (self, key) :
        return (self.lower, self.upper) [key]
    # end def __getitem__

    def __iter__ (self) :
        return iter ((self.lower, self.upper))
    # end def __iter__

    def __lt__ (self, other) :
        try :
            return (self.lower, self.upper) < (other.lower, other.upper)
        except AttributeError :
            return (self.lower, self.upper) < other
    # end def __lt__

    def __mod__ (self, rhs) :
        return self.__class__ (self.lower % rhs, (self.upper % rhs) or rhs)
    # end def __mod__

    def __repr__ (self) :
        return self.format % (self.lower, self.upper)
    # end def __repr__

    def __setitem__ (self, key, value) :
        setattr (self, ("lower", "upper") [key], value)
    # end def __setitem__

    @classmethod
    def union (cls, * args) :
        """Returns a list of intervals with the union of `args`"""
        result = []
        p = TFL.DL_List (TFL.dusort (args, lambda i : (i.lower, i.upper))).head
        while p :
            pv = p.value
            q  = p.next
            while q and pv.upper >= q.value.lower :
                if pv.upper < q.value.upper :
                    pv = cls (pv.lower, q.value.upper)
                q = q.next
            result.append (pv)
            p = q
        return result
    # end def union

# end class Numeric_Interval

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Numeric_Interval
