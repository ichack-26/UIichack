# -*- coding: utf-8 -*-
# Copyright (C) 2006-2017 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.DRA.Averager
#
# Purpose
#    Compute average and standard deviation of data series
#
# Revision Dates
#    22-Nov-2006 (CT) Creation
#     1-Sep-2008 (CT) `moving_average` added
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#     6-Apr-2017 (CT) Reduce number of divisions in `moving_average`
#     6-Apr-2017 (CT) Factor `indexed_moving_average`
#    16-May-2017 (CT) Support `n == 1` in `moving_average`
#    ««revision-date»»···
#--

from   _TFL import TFL

from   _TFL.DL_List          import DL_Ring

import _TFL._Meta.Object
import _TFL._DRA

import itertools
import math

class Averager (TFL.Meta.Object) :
    """Compute average and standard deviation of data series.

       >>> runner = Averager ()
       >>> runner.add (x*x for x in range (3))
       >>> "%8.2f +- %5.3f" % (runner.average, runner.standard_deviation)
       '    1.67 +- 2.082'
       >>> runner.add (2**x for x in range (3,10))
       >>> "%8.2f +- %5.3f" % (runner.average, runner.standard_deviation)
       '  102.10 +- 165.085'
    """

    average            = property (lambda s : s.sum_x / s.n)
    standard_deviation = property \
        ( lambda s : (s.n > 1) and math.sqrt
            ((s.sum_xx * s.n - s.sum_x ** 2) / (s.n * (s.n - 1))) or 0
        )

    def __init__ (self, s = []) :
        self.n      = 0
        self.sum_x  = 0.0
        self.sum_xx = 0.0
        if s :
            self.add (s)
    # end def __init__

    def add (self, s) :
        """Add elements of iterable `s`."""
        for x in s :
            self.n      += 1
            self.sum_x  += x
            self.sum_xx += x * x
    # end def add

# end class Averager

def indexed_moving_average (s, n, central = False) :
    """Generator for indexed moving average of `n` data points over sequence `s`.

    >>> def show (ma_s, fmt = "(%d, %.1f)") :
    ...     print ("[" + ", ".join (fmt % (i, v) for i, v in ma_s) + "]")

    >>> show (indexed_moving_average (range (10), 2))
    [(1, 0.5), (2, 1.5), (3, 2.5), (4, 3.5), (5, 4.5), (6, 5.5), (7, 6.5), (8, 7.5), (9, 8.5)]
    >>> show (indexed_moving_average (range (10), 3))
    [(2, 1.0), (3, 2.0), (4, 3.0), (5, 4.0), (6, 5.0), (7, 6.0), (8, 7.0), (9, 8.0)]
    >>> show (indexed_moving_average (range (10), 4))
    [(3, 1.5), (4, 2.5), (5, 3.5), (6, 4.5), (7, 5.5), (8, 6.5), (9, 7.5)]
    >>> show (indexed_moving_average (range (10), 5))
    [(4, 2.0), (5, 3.0), (6, 4.0), (7, 5.0), (8, 6.0), (9, 7.0)]
    >>> show (indexed_moving_average (range (10), 3, True))
    [(1, 1.0), (2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0), (8, 8.0)]
    >>> show (indexed_moving_average (range (10), 5, True))
    [(2, 2.0), (3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0), (7, 7.0)]
    >>> show (indexed_moving_average (range (10), 7, True))
    [(3, 3.0), (4, 4.0), (5, 5.0), (6, 6.0)]
    >>> show (indexed_moving_average (range (10), 9, True))
    [(4, 4.0), (5, 5.0)]
    >>> show (indexed_moving_average (range (10), 10, True))
    [(5, 4.5)]
    >>> fmt = "(%d, %.2f)"
    >>> show (indexed_moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 3, True), fmt)
    [(1, 1.29), (2, 1.29), (3, 1.29), (4, 1.30), (5, 1.29)]
    >>> show (indexed_moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 5, True), fmt)
    [(2, 1.29), (3, 1.30), (4, 1.29)]
    >>> show (indexed_moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 7, True), fmt)
    [(3, 1.29)]
    """
    if central :
        i = n // 2
    else :
        i = n - 1
    return enumerate (moving_average (s, n), start = i)
# end def indexed_moving_average

def moving_average (s, n) :
    """Generator for moving average of `n` data points over sequence `s`.

    >>> def show (ma_s, fmt = "%.1f") :
    ...     print ("[" + ", ".join (fmt % v for v in ma_s) + "]")

    >>> show (moving_average (range (10), 2))
    [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5]
    >>> show (moving_average (range (10), 3))
    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    >>> show (moving_average (range (10), 4))
    [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
    >>> show (moving_average (range (10), 5))
    [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    >>> fmt = "%.2f"
    >>> show (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 3), fmt)
    [1.29, 1.29, 1.29, 1.30, 1.29]
    >>> show (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 5), fmt)
    [1.29, 1.30, 1.29]
    >>> show (moving_average ((1.28, 1.31, 1.29, 1.28, 1.30, 1.31, 1.27), 7), fmt)
    [1.29]
    """
    if n == 1 :
        yield from s 
    else :
        m  = float   (n)
        s  = iter    (s)
        w  = DL_Ring (next (s) / m for k in range (n))
        ma = sum     (w.values ())
        yield ma
        for x in s :
            x_m  = x / m
            ma  -= w.pop_front ()
            ma  += x_m
            w.append (x_m)
            yield ma
# end def moving_average

if __name__ != "__main__" :
    TFL.DRA._Export ("*")
### __END__ TFL.DRA.Averager
