# -*- coding: utf-8 -*-
# Copyright (C) 2004-2020 Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# All rights reserved
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Interval_Set
#
# Purpose
#    Model a sorted set of intervals
#
# Revision Dates
#     9-Dec-2005 (RSC) Creation
#    12-Dec-2005 (RSC) Changed License to LGPL
#                      Added several new doctests for boundary cases
#                      Reordered doctests for easier viewing
#                      _element_class replaced with a lambda
#                      Introduced _intersection_iter and recode
#                      intersection and contains with it
#                      Factored _bisection and use it in next_point
#    13-Dec-2005 (CT)  Small improvements (`_intersection_iter`, ...)
#    22-Jul-2006 (CED) `contains_interval` added
#    24-Nov-2006 (CED) `difference` added
#    19-Feb-2007 (CT)  `intersection_iter` added
#    19-Feb-2007 (CT)  `difference` done right
#    20-Feb-2007 (CT)  `contains_interval` changed to use `any_true`
#    21-Feb-2007 (CT)  `_difference_iter` factored
#    12-Mar-2007 (CT)  `k_of_n_intersection_iter` added
#    13-Mar-2007 (CT)  `k_of_n_intersection_iter` added (cont.)
#    13-Mar-2007 (CT)  `intersection_iter` changed to use `_IVS_Iter_`
#    28-Mar-2007 (CED) `copy`, `shifted` added
#    30-Mar-2007 (CED) Additional doctest added
#    30-Mar-2007 (CT)  `_difference_iter` fixed
#    31-Mar-2007 (CT)  `_difference_iter` fixed again
#     2-Apr-2007 (CT)  Another doctest for `difference` added
#     6-Apr-2007 (CT)  Use `key` argument of `min` instead of
#                      tuple/generator-expression obfuscation
#    11-Apr-2007 (CT)  `_new` added and used
#    11-Apr-2007 (CT)  `union` simplified by using `itertools.chain`
#    11-Apr-2007 (CT)  `_difference_iter` changed to skip empty intervals of
#                      `other`
#     2-Aug-2007 (CED) Property `length` added
#    11-Jul-2018 (CT) Add guards for `StopIteration`, `RuntimeError`
#                     + Python 3.7 breakage due to PEP 479
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _TFL.predicate        import any_true, dusort
from   bisect                import bisect

import _TFL._Meta.Object

import itertools

class Interval_Set (TFL.Meta.Object) :
    """Class for modelling a sorted set of intervals.

       >>> from   _TFL   import TFL
       >>> import _TFL.Numeric_Interval
       >>> N = TFL.Numeric_Interval
       >>> class IS (Interval_Set) : pass
       ...
       >>> i = IS (N (  0, 100))
       >>> j = IS (N (100, 200))
       >>> k = IS (N ( 20,  50))
       >>> l = i.union (j)
       >>> l
       IS ((0, 200))
       >>> i.union (i)
       IS ((0, 100))
       >>> i.copy ()
       IS ((0, 100))
       >>> [l.intersection (x) for x in (i, j, l)]
       [IS ((0, 100)), IS ((100, 200)), IS ((0, 200))]
       >>> [l.overlaps (x) for x in (i, j, l)]
       [True, True, True]
       >>> [l.contains_point (x) for x in (0, 50, 100, 200, 4711)]
       [True, True, True, True, False]
       >>> m = IS (N (1, 2), N (5, 6), N (7, 9))
       >>> m
       IS ((1, 2), (5, 6), (7, 9))
       >>> m.shifted (10)
       IS ((11, 12), (15, 16), (17, 19))
       >>> n = IS (N (1, 5), N (6, 6), N (9, 11), N (20, 30))
       >>> n.intersection (m)
       IS ((1, 2), (5, 5), (6, 6), (9, 9))
       >>> [m.next_point_up (x) for x in (0, 1, 3, 9, 10)]
       [1, 1, 5, 9, None]
       >>> m.intersection (l)
       IS ((1, 2), (5, 6), (7, 9))
       >>> o = IS (N (1, 1))
       >>> o, bool (o), o.is_empty ()
       (IS ((1, 1)), True, False)
       >>> p = IS ()
       >>> p, bool (p), p.is_empty ()
       (IS (), False, True)
       >>> o = IS (N (0, 5), N (10, 15), N (20, 25))
       >>> p = IS (N (3, 6), N (12, 13), N (20, 25))
       >>> o.difference (p)
       IS ((0, 3), (10, 12), (13, 15))

       >>> a = IS (N (0, 5), N (10, 20), N (40, 60), N (65, 70))
       >>> b = IS (N (7, 8), N (10, 12), N (18, 20), N (33, 37), N (45, 48))
       >>> c = a.difference (b)
       >>> c
       IS ((0, 5), (12, 18), (40, 45), (48, 60), (65, 70))
       >>> d = IS (N (10, 20), N (60,75))
       >>> c.difference (d)
       IS ((0, 5), (40, 45), (48, 60))
       >>> d.difference (IS ())
       IS ((10, 20), (60, 75))
       >>> d.difference (IS (N (30, 40)))
       IS ((10, 20), (60, 75))
       >>> d.difference (IS (N (80, 90)))
       IS ((10, 20), (60, 75))
       >>> d.difference (IS (N (0, 10)))
       IS ((10, 20), (60, 75))
       >>> d.difference (IS (N (0, 11)))
       IS ((11, 20), (60, 75))
       >>> c.union (d)
       IS ((0, 5), (10, 20), (40, 45), (48, 75))
       >>> a = IS (N (0, 390), N (585, 5000))
       >>> b = IS (N (0, 600))
       >>> a.difference (b)
       IS ((600, 5000))
       >>> a = IS (N (0, 390), N (585, 5000), N (6000, 6200), N (7000, 7500))
       >>> b = IS (N (0, 600), N (5900, 6100), N (6250, 7100))
       >>> a.difference (b)
       IS ((600, 5000), (6100, 6200), (7100, 7500))
       >>> t = IS (N (0, 1000))
       >>> u = IS (N (10, 20), N (25, 25), N (42, 400), N (900, 990))
       >>> t.difference (u)
       IS ((0, 10), (20, 42), (400, 900), (990, 1000))

       >>> list (IS.intersection_iter ((N (3, 6), N (12, 13)), min_size = 1))
       [(3, 6), (12, 13)]
       >>> list (IS.intersection_iter ((N (3, 6), N (12, 13)), min_size = 2))
       [(3, 6)]
       >>> list (IS.intersection_iter (o, p))
       [(3, 5), (12, 13), (20, 25)]
       >>> list (IS.intersection_iter (o, p, min_size = 2))
       [(3, 5), (20, 25)]
       >>> list (IS.intersection_iter (o, p, (N (4, 6), N (12, 12))))
       [(4, 5), (12, 12)]

       >>> ivs1 = (N (10, 20), N (25, 40), N (100, 150))
       >>> ivs2 = (N (20, 50), N (120, 140))
       >>> ivs3 = (N (0, 50), N (110, 140))
       >>> ivs4 = (N (5, 20), N (22, 38), N (125, 150))
       >>> list (IS.k_of_n_intersection_iter (1, 15, (ivs1, ivs2, ivs3, ivs4)))
       [(0, 50), (5, 20), (20, 50), (22, 38), (25, 40), (100, 150), (110, 140), (120, 140), (125, 150)]
       >>> list (IS.k_of_n_intersection_iter (2, 15, (ivs1, ivs2, ivs3, ivs4)))
       [(5, 20), (25, 40), (20, 50), (22, 38), (125, 150), (110, 140), (125, 140), (120, 140)]
       >>> list (IS.k_of_n_intersection_iter (3, 15, (ivs1, ivs2, ivs3, ivs4)))
       [(25, 40), (22, 38), (125, 140), (120, 140)]
       >>> list (IS.k_of_n_intersection_iter (4, 15, (ivs1, ivs2, ivs3, ivs4)))
       [(125, 140)]
       >>> list (IS.k_of_n_intersection_iter (5, 15, (ivs1, ivs2, ivs3, ivs4)))
       []
    """

    element_class = property (lambda self : self.intervals [0].__class__)

    @property
    def length (self) :
        return sum (i.length for i in self.intervals)
    # end def length

    def __init__ (self, * args) :
        if args :
            self.intervals = args [0].__class__.union (* args)
        else :
            self.intervals = []
    # end def __init__

    @classmethod
    def _new (cls, intervals) :
        ### Beware: this assumes that `intervals` is properly normalized
        ### (i.e., sorted and merged as done by `Numeric_Interval.union`)
        result = cls ()
        result.intervals = list (intervals)
        return result
    # end def _new

    def contains_interval (self, ival) :
        return bool (any_true (iv.contains (ival) for iv in self.intervals))
    # end def contains_interval

    def contains_point (self, point) :
        return self.next_point_up (point) == point
    # end def contains_point

    def copy (self) :
        return self._new (i.copy () for i in self.intervals)
    # end def copy

    def difference (self, other) :
        return self._new (self._difference_iter (other))
    # end def difference

    def intersection (self, other) :
        return self._new (self._intersection_iter (other))
    # end def intersection

    def shifted (self, delta) :
        return self._new (i.shifted (delta) for i in self.intervals)
    # end def shifted

    @classmethod
    def intersection_iter (cls, * iv_sets, ** kw) :
        """Generates all intersections larger than `min_size` between the
           intervals of `iv_sets` (the default for `min_size` is 0).
        """
        min_size = kw.pop ("min_size", 0)
        assert not kw, "Undefined arguments passed: %s" % (sorted (kw), )
        try :
            iv_iters = [cls._IVS_Iter_ (ivs, min_size) for ivs in iv_sets]
        except RuntimeError :
            pass
        else :
            while True :
                r = iv_iters [0].value
                for ivi in iv_iters [1:] :
                    r = r.intersection (ivi.value)
                    if r.length < min_size :
                        break
                else :
                    yield r
                try :
                    small = min \
                        ( iv_iters
                        , key = lambda v : (v.value.upper, - v.value.lower)
                        )
                    small.advance ()
                except (RuntimeError, StopIteration) :
                    break
    # end def intersection_iter

    @classmethod
    def k_of_n_intersection_iter (cls, k, min_size, iv_sets) :
        """Generates all intersections larger than `min_size` between at least
           `k` of the intervals of `iv_sets`.
        """
        if k == 1 :
            ivs = dusort (itertools.chain (* iv_sets), lambda iv : iv.lower)
            for iv in ivs :
                if iv.length >= min_size :
                    yield iv
        else :
            seen     = set ()
            sort_key = lambda i : (i.value.upper, i.value.lower)
            try :
                iv_iters = dusort \
                    ( (   x
                      for x in (cls._IVS_Iter_X_ (i, min_size) for i in iv_sets)
                      if  x
                      )
                    , sort_key
                    )
            except RuntimeError :
                pass
            else :
                slack = len (iv_iters) - k
                while slack >= 0 :
                    for j in range (slack + 1) :
                        hits   = 1
                        misses = j
                        r      = iv_iters [j].value
                        for ivi in iv_iters [j+1:] :
                            s = r.intersection (ivi.value)
                            if s.length >= min_size :
                                hits += 1
                                key = (s.lower, s.upper)
                                if hits >= k and key not in seen :
                                    seen.add (key)
                                    yield s
                                r = s
                            else :
                                misses += 1
                                if misses > slack :
                                    break
                    try :
                        small = min       (iv_iters, key = sort_key)
                        small.advance     ()
                    except (RuntimeError, StopIteration) :
                        break
                    iv_iters = dusort \
                        ((ivi for ivi in iv_iters if ivi), sort_key)
                    slack    = len    (iv_iters) - k
    # end def k_of_n_intersection_iter

    def is_empty (self) :
        return not self
    # end def is_empty

    def next_point_up (self, point) :
        ivals = self.intervals
        if ivals :
            i = bisect (ivals, self.element_class (point, point))
            if ivals [i - 1].contains_point (point) :
                return point
            elif i < len (ivals) :
                return ivals [i].lower
    # end def next_point_up

    def overlaps (self, other) :
        try :
            next (self._intersection_iter (other))
        except StopIteration :
            return False
        else :
            return True
    # end def overlaps

    def union (self, * other) :
        return self.__class__ (* itertools.chain (self, * other))
    # end def union

    def _difference_iter (self, other) :
        lit = iter (self)
        try :
            l   = next (lit)
        except StopIteration :
            return
        for r in other :
            if not r :
                continue
            while l.upper <= r.lower :
                yield l
                try :
                    l = next (lit)
                except StopIteration :
                    return
            if l.lower < r.upper :
                if l.lower < r.lower :
                    yield l.__class__ (l.lower, r.lower)
                if r.upper < l.upper :
                    l = l.__class__ (r.upper, l.upper)
                else :
                    try :
                        l = next (lit)
                    except StopIteration :
                        return
                    if l.lower < r.upper < l.upper :
                        l = l.__class__ (r.upper, l.upper)
        yield l
        yield from lit 
    # end def _difference_iter

    def _intersection_iter (self, other) :
        l_iter  = iter (self)
        r_iter  = iter (other)
        try :
            l, r    = next (l_iter), next (r_iter)
        except StopIteration :
            pass
        else :
            while True :
                i   = r.intersection (l)
                if i.is_valid () :
                    yield i
                try :
                    if l.upper < r.upper :
                        l = next (l_iter)
                    else :
                        r = next (r_iter)
                except StopIteration :
                    break
    # end def _intersection_iter

    def __bool__ (self) :
        return bool (self.intervals)
    # end def __bool__

    def __iter__ (self) :
        return iter (self.intervals)
    # end def __iter__

    def __repr__ (self) :
        name = self.__class__.__name__
        return "%s (%s)" % (name, ", ".join (repr (i) for i in self))
    # end def __repr__

    class _IVS_Iter_ (TFL.Meta.Object) :

        def __init__ (self, iv_set, min_size) :
            self.ivi      = iter (iv_set)
            self.min_size = min_size
            self.advance ()
        # end def __init__

        def advance (self) :
            succ     = lambda : next (self.ivi)
            min_size = self.min_size
            v = succ ()
            while v.length < min_size :
                v = succ ()
            self.value = v
        # end def advance

    # end class _IVS_Iter_

    class _IVS_Iter_X_ (_IVS_Iter_) :

        def advance (self) :
            try :
                v = self.__super.advance ()
            except StopIteration :
                self.done  = True
                self.value = v = None
            else :
                self.done  = False
        # end def advance

        def __bool__ (self) :
            return not self.done
        # end def __bool__

    # end class _IVS_Iter_X_

# end class Interval_Set

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Interval_Set
