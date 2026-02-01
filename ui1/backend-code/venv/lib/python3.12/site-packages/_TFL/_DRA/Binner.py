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
#    TFL.DRA.Binner
#
# Purpose
#    Support for binning of measurement values
#
# Revision Dates
#    15-Nov-2006 (CT) Creation
#    22-Nov-2006 (CT) `delta` added
#    24-Nov-2006 (CT) Optional argument `center` added to `value`
#    26-Nov-2006 (CT) `index_f` factored
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    28-Feb-2017 (CT) Add `range` method
#    ««revision-date»»···
#--

from   _TFL import TFL

import _TFL._Meta.Object
import _TFL._DRA

class Binner (TFL.Meta.Object) :
    """Distribute measurement values into bins.

    The range of possible values is split into bins that are numbered from
    1 to `n` (0 is reserved for invalid values). Each measured value is
    mapped to the bin containing it.

    >>> B = Binner (0, 2)
    >>> [B.index (d) for d in (0, 1, 2, 10, 180, 359)]
    [1, 1, 2, 6, 91, 180]

    >>> [B.value (i) for i in [1, 1, 2, 6, 91, 180]]
    [1.0, 1.0, 3.0, 11.0, 181.0, 359.0]

    >>> [B.range (i) for i in [1, 2, 6, 91, 180]]
    [(0.0, 2.0), (2.0, 4.0), (10.0, 12.0), (180.0, 182.0), (358.0, 360.0)]

    """

    def __init__ (self, offset, width) :
        self.offset = float (offset)
        self.width  = float (width)
    # end def __init__

    def delta (self, d) :
        """Returns delta corresponding to binner index delta `d`"""
        return self.width * d
    # end def delta

    def index (self, r) :
        """Returns bin index for value `r`."""
        return int (self.index_f (r))
    # end def index

    def index_f (self, r) :
        """Returns bin index for value `r` as float value."""
        return ((r - self.offset) / self.width) + 1
    # end def index

    def range (self, i) :
        """Returns the range of values in bin `i`."""
        lo = self.value (i, center = False)
        hi = lo + self.width
        return (lo, hi)
    # end def range

    def value (self, i, center = True) :
        """Returns value corresponding to bin `i`."""
        width  = self.width
        result = ((i - 1) * width) + self.offset
        if center :
            result += (width / 2)
        return result
    # end def value

# end class Binner

if __name__ != "__main__" :
    TFL.DRA._Export ("*")
### __END__ TFL.DRA.Binner
