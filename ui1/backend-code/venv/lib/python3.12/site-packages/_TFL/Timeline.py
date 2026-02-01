# -*- coding: utf-8 -*-
# Copyright (C) 2003-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Timeline
#
# Purpose
#    Timeline for scheduling
#
# Revision Dates
#    21-Aug-2003 (CT)  Creation
#    29-Aug-2003 (CT)  `Timeline.length` added
#    29-Aug-2003 (CT)  `orig` added
#    23-Sep-2003 (CT)  `snip` added
#    26-Sep-2003 (CED) `reset` added
#     2-Oct-2003 (CED) `epsilon` introduced and used to avoid rounding errors
#    23-Oct-2003 (CT)  Small changes to allow cutting of zero-length spans
#     5-Apr-2004 (CED) `__str__` added
#    29-Jun-2005 (CT)  Test scaffolding dumped
#    30-Jun-2005 (CT)  Style improvements
#    22-Jul-2006 (CED) `is_free` added
#    16-Feb-2007 (CT)  Factored to `TFL`
#    16-Feb-2007 (CT)  `is_free` removed
#    16-Feb-2007 (CT)  `bisect`-use and `break` added to `intersection`
#    16-Feb-2007 (CT)  `Timeline_Cut` simplified, `prepare_cut` added
#    16-Feb-2007 (CT)  `snip` simplified
#    16-Feb-2007 (CT)  `_sid` introduced
#    16-Feb-2007 (CT)  `intersection_p` added (and `cut` changed to deal with
#                      the resulting pieces)
#    17-Feb-2007 (CT)  `min_size` added to `intersection` (and
#                      `intersection_p`)
#    18-Feb-2007 (CT)  `Timeline_Cut` made compatible with
#                      `TFL.Numeric_Interval`
#    18-Feb-2007 (CT)  `Timeline_Cut.intersection` redefined (and
#                      `_update_result` added)
#    20-Feb-2007 (CT)  `Timeline_Cut_P` added
#    21-Feb-2007 (CT)  `Timeline_Cut.modulo` and
#                      `Timeline_Cut.prepare_cut_around` added
#    21-Feb-2007 (CT)  `Timeline.cut_p` added
#    22-Feb-2007 (CT)  `Timeline_Cut_P.minmax` added
#    11-Mar-2007 (CT)  `Timeline_Cut` and `Timeline_Cut_P` changed to take
#                      `timeline` attribute (again)
#    14-Mar-2007 (CT)  s/Timeline_Cut_P/Timeline_Cut_Periodic/
#    14-Mar-2007 (CT)  `intersection_p` changed to use `orig.upper` instead
#                      of `free [-1].upper` as upper bound
#    15-Mar-2007 (CT)  s/Timeline_Cut/TL_Section/
#    15-Mar-2007 (CT)  Major overhaul of `TL_Section`
#                      - `new` instead of `__init__`
#                      - `TL_Section_Mod_P` instead of `TL_Section.modulo`
#    16-Mar-2007 (CT)  `TLS_Periodic.minmax` changed to cache
#    16-Mar-2007 (CT)  `Timeline.intersection` changed to break
#                      `if l == min_size == 0`
#    17-Mar-2007 (CT)  `multi_intersection` and `_periodic_span_iter`
#                      factored from `intersection_p`
#     5-Apr-2007 (CT)  Assertion in `_periodic_span_iter` corrected
#     6-Apr-2007 (CT)  `TLS_Periodic.__init__` and `intersection_p` guarded
#                      by assertions
#    10-Apr-2007 (CT)  Increment `self._sid` instead of `self.__class__._sid`
#    11-Apr-2007 (CT)  s/imp/tsmp/
#    17-Apr-2007 (CT)  `TL_Section_Mod_P.new` changed to use `%` operator of
#                      `Numeric_Interval` instead of home-grown (and incorrect)
#                      code
#    17-Apr-2007 (CT)  `TLS_Periodic.prepare_cut_somewhere` added
#    14-Jun-2007 (CT)  `reset` changed to increment `_sid`
#    30-Nov-2007 (CT)  `prepare_cut_somewhere` changed to explicitly check
#                      for empty `generations` (improve traceback information)
#    13-Jun-2008 (CT)  `intersection` changed to never return an empty
#                      `sections` if `min_size == 0`
#    17-Jan-2013 (CT) Raise `Timeline_Error`, not `AssertionError`
#    ««revision-date»»···
#--

from   _TFL                  import TFL

from   _TFL.Generators       import enumerate_slice
from   _TFL.pyk              import pyk

import _TFL.Interval_Set
import _TFL.Numeric_Interval
import _TFL._Meta.Object

from   bisect                import bisect

class Timeline_Error (Exception) :
    """Wrong use of Timeline"""
# end class Timeline_Error

class TL_Section (TFL.Numeric_Interval) :
    """Section that may be cut from Timeline"""

    Span       = TFL.Numeric_Interval
    parents    = []
    period     = None
    _sid       = None

    @classmethod
    def new (cls, span, index, timeline) :
        result          = cls (span.lower, span.upper)
        result.index    = index
        result.timeline = timeline
        result._sid     = timeline._sid
        return result
    # end def new

    def intersection (self, other) :
        result = self.__super.intersection (other)
        self._update_result (other, result)
        return result
    # end def intersection

    def prepare_cut (self, span) :
        self.to_cut = self.__super.intersection (span)
        return self.to_cut
    # end def prepare_cut

    def prepare_cut_around_l (self, span, size) :
        jitter = size - span.length
        if jitter <= 0 :
            lower = span.lower
        else :
            lower = max (self.lower, span.lower - jitter)
        return self.prepare_cut (self.Span (lower, lower + size))
    # end def prepare_cut_around_l

    def prepare_cut_around_u (self, span, size) :
        jitter = size - span.length
        if jitter <= 0 :
            upper = span.upper
        else :
            upper = min (self.upper, span.upper + jitter)
        return self.prepare_cut (self.Span (upper - size, upper))
    # end def prepare_cut_around_u

    def prepare_cut_l (self, size) :
        lower       = self.lower
        self.to_cut = self.Span (lower, lower + size)
        return self.to_cut
    # end def prepare_cut_l

    def prepare_cut_u (self, size) :
        upper       = self.upper
        self.to_cut = self.Span (upper - size, upper)
        return self.to_cut
    # end def prepare_cut_u

    def _update_result (self, other, result) :
        parents = self.parents
        if parents :
            result.parents = parents + getattr (other, "parents", [])
    # end def _update_result

# end class TL_Section

class TL_Section_Mod_P (TL_Section) :
    """TL_Section modulo period."""

    @classmethod
    def new (cls, parent, period) :
        result         = cls (* (parent % period))
        result.parents = [parent]
        return result
    # end def new

# end class TL_Section_Mod_P

class TLS_Periodic (TFL.Meta.Object) :
    """Set of periodic TL_Sections from Timeline"""

    _minmax = None

    def __init__ (self, period, min_size, timeline, generations) :
        self.period      = period
        self.min_size    = min_size
        self.timeline    = timeline
        self.generations = list (generations)
        self._imp        = {}
        if not self.generations :
            raise ValueError ("`generations` must not be empty")
    # end def __init__

    def intersections_mod_p (self, min_size = None) :
        """Return the intersections of `.generations` taken modulo `.period`.
        """
        if min_size is None :
            min_size = self.min_size
        try :
            result     = self._imp [min_size]
        except KeyError :
            p          = self.period
            TSMP       = TL_Section_Mod_P
            normalized = \
                [[TSMP.new (s, p) for s in g] for g in self.generations]
            result     = self._imp [min_size] = list \
                ( TFL.Interval_Set.intersection_iter
                    (* normalized, ** dict (min_size = min_size))
                )
        return result
    # end def intersections_mod_p

    @property
    def minmax (self) :
        result = self._minmax
        if result is None :
            result = self._minmax = min \
                (max ([s.length for s in g] or [0]) for g in self.generations)
        return result
    # end def minmax

    def prepare_cut_mod_p_l (self, tsmp, size) :
        return self._prepare_cut_mod_p \
            (tsmp, size, lambda p, * a : p.prepare_cut_around_l (* a))
    # end def prepare_cut_mod_p_l

    def prepare_cut_mod_p_u (self, tsmp, size) :
        return self._prepare_cut_mod_p \
            (tsmp, size, lambda p, * a : p.prepare_cut_around_u (* a))
    # end def prepare_cut_mod_p_u

    def prepare_cut_somewhere (self, size) :
        result = self.to_cut = []
        for g in self.generations :
            if g :
                p = max (g)
                if p.parents :
                    if len (p.parents) != 1 :
                        raise RuntimeError \
                            ( "p.parents must have one element: %s"
                            % (p.parents, )
                            )
                    p = p.parents
                p.prepare_cut_around_l (p, size)
                result.append (p)
            else :
                raise ValueError \
                    ( "Elements of self.generations %s must not be empty, %s"
                    % (self.generations, size)
                    )
        return result
    # end def prepare_cut_somewhere

    def _prepare_cut_mod_p (self, tsmp, size, preparer) :
        period = self.period
        shift  = 0
        for p in tsmp.parents :
            preparer (p, tsmp.shifted (shift), size)
            shift += period
        self.to_cut = tsmp.parents
        return self.to_cut
    # end def _prepare_cut_mod_p

    def __bool__ (self) :
        return self.minmax > 0
    # end def __bool__

    def __iter__ (self) :
        return iter (self.generations)
    # end def __iter__

# end class TLS_Periodic

class Timeline (TFL.Meta.Object) :
    """Timeline for scheduling.

       >>> S  = Timeline.Span
       >>> tl = Timeline (0, 1000)
       >>> tl.free
       [(0, 1000)]
       >>> c = tl.intersection (S (100, 100)) [0] [0]
       >>> c.prepare_cut_l (0)
       (100, 100)
       >>> tl.cut (c)
       >>> tl.free
       [(0, 1000)]
       >>> c = tl.intersection (S (100, 300)) [0] [0]
       >>> c.prepare_cut_l (50)
       (100, 150)
       >>> tl.cut (c)
       >>> tl.free
       [(0, 100), (150, 1000)]
       >>> tl.intersection (S (80, 120))
       ([(80, 100)], 20)
       >>> c = tl.intersection (S (70, 100)) [0] [0]
       >>> c.prepare_cut_u (15)
       (85, 100)
       >>> tl.cut (c)
       >>> tl.free
       [(0, 85), (150, 1000)]
       >>> c = tl.intersection (S (150, 200)) [0] [0]
       >>> c.prepare_cut_l (50)
       (150, 200)
       >>> tl.cut (c)
       >>> tl.free
       [(0, 85), (200, 1000)]
       >>> c = tl.intersection (S (500, 600)) [0] [0]
       >>> c.prepare_cut_l (50)
       (500, 550)
       >>> tl.cut (c)
       >>> tl.free
       [(0, 85), (200, 500), (550, 1000)]
       >>> c1, c2 = tl.intersection (S (50, 300)) [0]
       >>> c1, c2
       ((50, 85), (200, 300))
       >>> c1.prepare_cut_u (15)
       (70, 85)
       >>> c2.prepare_cut_l (15)
       (200, 215)
       >>> tl.cut (c1, c2)
       >>> tl.free
       [(0, 70), (215, 500), (550, 1000)]
       >>> with expect_except (Timeline_Error) :
       ...      tl.cut (c1, c2)
       Timeline_Error: Wrong use of Timeline (intersection vs. cut)
           [(0, 70), (215, 500), (550, 1000)] <--> (200, 215)

       >>> tl = Timeline (0, 1000)
       >>> tl.snip (S (10, 20), S (25, 25), S (42, 400), S (900, 990))
       >>> tl.free
       [(0, 10), (20, 42), (400, 900), (990, 1000)]
       >>> tl.snip (S (995,1000), S (5, 7), S (400, 410), S (23, 37))
       >>> tl.free
       [(0, 5), (7, 10), (20, 23), (37, 42), (410, 900), (990, 995)]
       >>> tl.intersection (S (0, 50), min_size = 6)
       ([], 0)
       >>> tl.intersection (S (0, 50), min_size = 4)
       ([(0, 5), (37, 42)], 10)
       >>> tl.intersection (S (0, 50), min_size = 3)
       ([(0, 5), (7, 10), (20, 23), (37, 42)], 16)

       >>> tl = Timeline (0, 1000)
       >>> pieces = []
       >>> for (f, ) in tl.intersection_p (S (50, 100), 400) :
       ...     x = f.prepare_cut_l (50)
       ...     pieces.append (f)
       ...
       >>> [(p.to_cut, p.index) for p in pieces]
       [((50, 100), 0), ((450, 500), 0), ((850, 900), 0)]
       >>> tl.cut (* pieces)
       >>> tl.free
       [(0, 50), (100, 450), (500, 850), (900, 1000)]

       >>> tl = Timeline (0, 1000)
       >>> with expect_except (Timeline_Error) :
       ...      tl.intersection_p (S (50, 100), 40)
       Timeline_Error: Length of span must be shorter than period: ((50, 100), 40)

       >>> tl = Timeline (0, 1000)
       >>> tl.snip (S (100, 120), S (300, 330), S (360, 370), S (550, 590))
       >>> tl.free
       [(0, 100), (120, 300), (330, 360), (370, 550), (590, 1000)]
       >>> tcp = tl.intersection_p (S (50, 150), 250)
       >>> tcp.minmax
       30
       >>> tcp.generations
       [[(50, 100), (120, 150)], [(330, 360), (370, 400)], [(590, 650)], [(800, 900)]]
       >>> tsmps = tcp.intersections_mod_p ()
       >>> tsmps
       [(90, 100), (120, 150)]
       >>> tcp.prepare_cut_mod_p_l (tsmps [0], 30)
       [(50, 100), (330, 360), (590, 650), (800, 900)]
       >>> tl.cut_p (tcp)
       >>> tl.free
       [(0, 70), (120, 300), (370, 550), (620, 820), (850, 1000)]

       >>> tl = Timeline (0, 1000)
       >>> tl.snip (S (100, 120), S (300, 330), S (360, 370), S (550, 590))
       >>> tcp = tl.intersection_p (S (50, 150), 250)
       >>> tsmps = tcp.intersections_mod_p ()
       >>> tcp.prepare_cut_mod_p_u (tsmps [0], 25)
       [(50, 100), (330, 360), (590, 650), (800, 900)]
       >>> tl.cut_p (tcp)
       >>> tl.free
       [(0, 75), (120, 300), (330, 335), (370, 550), (615, 840), (865, 1000)]

       >>> tl = Timeline (0, 1000)
       >>> tl.snip (S (100, 120), S (300, 330), S (360, 370), S (550, 590))
       >>> tcp = tl.intersection_p (S (50, 150), 250)
       >>> tsmps = tcp.intersections_mod_p ()
       >>> tcp.prepare_cut_mod_p_l (tsmps [1], 30)
       [(120, 150), (370, 400), (590, 650), (800, 900)]
       >>> tl.cut_p (tcp)
       >>> tl.free
       [(0, 100), (150, 300), (330, 360), (400, 550), (590, 620), (650, 870), (900, 1000)]

       >>> tl = Timeline (0, 1000)
       >>> tl.snip (S (100, 120), S (300, 330), S (360, 370), S (550, 590))
       >>> tl.snip (S (70, 100), S (120, 130))
       >>> tl.free
       [(0, 70), (130, 300), (330, 360), (370, 550), (590, 1000)]
       >>> tcp = tl.intersection_p (S (50, 150), 250)
       >>> tcp.minmax
       20
       >>> tcp.generations
       [[(50, 70), (130, 150)], [(330, 360), (370, 400)], [(590, 650)], [(800, 900)]]

    """

    epsilon    = 0.001
    length     = property (lambda s : sum ((f.length for f in s.free), 0))
    _sid       = 0

    Section    = TL_Section
    Span       = TFL.Numeric_Interval

    def __init__ (self, lower, upper) :
        self.orig = self.Span (lower, upper)
        self.reset ()
    # end def __init__

    def cut (self, * pieces) :
        """Cut `pieces` from `self.free`. Each element of `pieces` must be a
           `TL_Section` as returned from `intersection` to which
           `prepare_cut_l` or `prepare_cut_u` was applied. Beware: don't
           interleave calls to `intersection` with multiple calls to `cut`.
        """
        try :
            pieces = sorted \
                (pieces, key = lambda p : (p.index, p.to_cut), reverse = True)
            for p in pieces :
                if p._sid != self._sid:
                    raise Timeline_Error \
                        ( "%s\n    %s <--> %s"
                        % ( "Wrong use of Timeline (intersection vs. cut)"
                          , self.free, p.to_cut
                          )
                        )
                if p.to_cut :
                    f = self.free [p.index]
                    if abs (f.lower - p.to_cut.lower) < self.epsilon :
                        f.lower = p.to_cut.upper
                    elif abs (f.upper - p.to_cut.upper) < self.epsilon :
                        f.upper = p.to_cut.lower
                    else :
                        head = self.Span (f.lower, p.to_cut.lower)
                        tail = self.Span (p.to_cut.upper, f.upper)
                        if not (head and tail) :
                            raise RuntimeError \
                                ( "Both head and tail must be non-empty: "
                                  "head = %s, tail = %s"
                                % (head, tail)
                                )
                        self.free [p.index : p.index + 1] = [head, tail]
                    if not f :
                        del self.free [p.index]
        finally :
            self._sid += 1
    # end def cut

    def cut_p (self, tcp) :
        self.cut (* tcp.to_cut)
    # end def cut_p

    def intersection (self, span, min_size = 1) :
        sections, total  = [], 0
        Section          = self.Section
        if span.length > 0 :
            free         = self.free
            lower, upper = span
            h            = bisect (free, self.Span (lower, lower))
            if h and free [h - 1].contains_point (lower) :
                h -= 1
            for i, f in enumerate_slice (free, h) :
                if f.lower > upper :
                    break
                s = f.intersection (span)
                l = s.length
                if l >= min_size :
                    sections.append (Section.new (s, i, self))
                    total += l
                    if l == min_size == 0 :
                        break
        else :
            min_size = 0
        if (not sections) and min_size == 0 :
            sections.append \
                (Section.new (self.Span (span.upper, span.upper), 0, self))
            total += 1
        return sections, total
    # end def intersection

    def intersection_p (self, span, period, min_size = 1) :
        spans = list (self._periodic_span_iter (span, period))
        if not spans :
            raise ValueError \
                ( "Expansion of span `%s` to period `%s` must not be empty"
                % (span, period)
                )
        return self.multi_intersection (spans, period, min_size)
    # end def intersection_p

    def multi_intersection (self, spans, period, min_size) :
        """`spans` should be periodic with `period` but may have some
           jitter.
        """
        return TLS_Periodic \
            ( period, min_size, self
            , (self.intersection (span, min_size) [0] for span in spans)
            )
    # end def multi_intersection

    def reset (self) :
        self._sid += 1
        self.free  = [self.orig.copy ()]
    # end def reset

    def snip (self, * spans) :
        for s in spans :
            l = s.length
            if l > 0 :
                (free, ), size = self.intersection (s)
                if abs (size - l) > self.epsilon :
                    raise ValueError ((self.free, s, spans, free))
                free.prepare_cut_l (size)
                self.cut           (free)
    # end def snip

    def _periodic_span_iter (self, span, period) :
        if span.length > period :
            raise Timeline_Error \
                ( "Length of span must be shorter than period: %s"
                % ((span, period), )
                )
        upper = self.orig.upper
        while span.lower < upper :
            yield span
            span = span.shifted (period)
    # end def _periodic_span_iter

    def __str__ (self) :
        return "Timeline free: " + str (self.free)
    # end def __str__

# end class Timeline

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Timeline
