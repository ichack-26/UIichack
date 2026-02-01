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
#    TFL.DRA.Bin_Distribution
#
# Purpose
#    Compute distribution of binned measurement data
#
# Revision Dates
#    17-Nov-2006 (CT) Creation
#    22-Nov-2006 (CT) `average` and `standard_deviation` added
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    11-May-2017 (CT) Use `pyk.iteritems` (Python-3 compatibility)
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

import _TFL.defaultdict
import _TFL._Meta.Object
import _TFL._DRA.Averager

class Bin_Distribution (TFL.Meta.Object) :
    """Compute distribution of binned measurement data"""

    average            = property \
        (lambda s : int (s.averager.average + 0.5))
    standard_deviation = property \
        (lambda s : int (s.averager.standard_deviation + 0.5))

    def __init__ (self, abscissa, * indices) :
        self.abscissa       = abscissa
        self.distribution   = TFL.defaultdict (int)
        self.measurements   = 0
        self.invalid_values = 0
        self.add (* indices)
    # end def __init__

    def add (self, * indices) :
        d = self.distribution
        for i in indices :
            if i > 0 :
                d [i] += 1
                self.measurements   += 1
            else :
                self.invalid_values += 1
        self._averager = None
    # end def add

    @property
    def averager (self) :
        result = self._averager
        if result is None :
            result = TFL.DRA.Averager ()
            for i, f in pyk.iteritems (self.distribution) :
                result.add (i for k in range (f))
        return result
    # end def averager

    def probabilities (self) :
        result = TFL.defaultdict (int)
        n      = float (self.measurements)
        for i, f in pyk.iteritems (self.distribution) :
            result [i] = f / n
        return result
    # end def probabilities

# end class Bin_Distribution

if __name__ != "__main__" :
    TFL.DRA._Export ("*")
### __END__ TFL.DRA.Bin_Distribution
