# -*- coding: utf-8 -*-
# Copyright (C) 2007-2019 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.DRA.Interpolator
#
# Purpose
#    Interpolate for equidistantly spaced data
#
# Revision Dates
#    11-Nov-2007 (CT) Creation
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    19-Aug-2019 (CT) Use `print_prepr`
#    ««revision-date»»···
#--

from   _TFL                   import TFL

from   _TFL.portable_repr     import print_prepr

import _TFL._Meta.Object
import _TFL._DRA

import _TFL.Accessor

class Interpolator_3 (TFL.Meta.Object) :
    """Interpolate from three data values.

       >>> calcer = Interpolator_3 ((7, 0.884226), (8, 0.877366), (9, 0.870531))
       >>> print_prepr (calcer (8.18125))
       0.87612530127
    """

    ### see J. Meeus, ISBN 0-943396-61-1, pp. 23-24
    ### XXX generalize to any (odd) number of data points

    x_getter = TFL.Getter [0]
    y_getter = TFL.Getter [1]

    def __init__ (self, p1, p2, p3, x_getter = None, y_getter = None) :
        if x_getter is not None :
            self.x_getter = x_getter
        if y_getter is not None :
            self.y_getter = y_getter
        Y = self.y_getter
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.a  = a = Y (p2) - Y (p1)
        self.b  = b = Y (p3) - Y (p2)
        self.c  = b - a
    # end def __init__

    def __call__ (self, x) :
        """Interpolated value at `x`."""
        X = self.x_getter
        Y = self.y_getter
        n = x - X (self.p2)
        return Y (self.p2) + (n / 2.0) * (self.a + self.b + n * self.c)
    # end def __call__

# end class Interpolator_3

if __name__ != "__main__" :
    TFL.DRA._Export ("*")
### __END__ Interpolator
