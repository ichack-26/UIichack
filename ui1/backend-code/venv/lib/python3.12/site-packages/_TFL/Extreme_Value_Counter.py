# -*- coding: utf-8 -*-
# Copyright (C) 2004-2013 TTTech Computertechnik AG. All rights reserved
# Schönbrunnerstraße 7, A--1040 Wien, Austria. office@tttech.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Extreme_Value_Counter
#
# Purpose
#    Classes for remembering the extreme values over a sequence of increments
#    and decrements
#
# Revision Dates
#    19-Feb-2004 (CED) Creation
#    26-Feb-2004 (CED) `set` added
#    ««revision-date»»···
#--

from   _TFL import TFL

import _TFL._Meta.Object
import _TFL.Environment

class Extreme_Counter (object) :
    """
       >>> ec = Extreme_Counter ()
       >>> ec.inc ()
       >>> ec.dec ()
       >>> ec.dec ()
       >>> ec.current_val
       -1
       >>> ec.max_val
       1
       >>> ec.min_val
       -1
       >>> ec += 10
       >>> ec.set (5)
       >>> ec.current_val
       5
       >>> ec.max_val
       9
       >>> ec.min_val
       -1
    """

    def __init__ (self, init_val = 0) :
        self.init_val    = init_val
        self.reset ()
    # end def __init__

    def __iadd__ (self, rhs) :
        self.current_val += rhs
        if self.current_val > self.max_val :
            self.max_val = self.current_val
        return self
    # end def __iadd__

    def __isub__ (self, rhs) :
        self.current_val -= rhs
        if self.current_val < self.min_val :
            self.min_val = self.current_val
        return self
    # end def __isub__

    def inc (self) :
        self += 1
    # end def inc

    def dec (self) :
        self -= 1
    # end def dec

    def reset (self) :
        self.current_val = self.init_val
        self.max_val     = self.init_val
        self.min_val     = self.init_val
    # end def reset

    def set (self, value) :
        self.current_val = value
        if self.current_val < self.min_val :
            self.min_val = self.current_val
        if self.current_val > self.max_val :
            self.max_val = self.current_val
    # end def set

# end class Extreme_Counter

class Maximum_Counter (Extreme_Counter) :

    def __init__ (self, init_val = - TFL.Environment.practically_infinite) :
        self__super.__init__ (init_val)
    # end def __init__

# end class Maximum_Counter

class Minimum_Counter (Extreme_Counter) :

    def __init__ (self, init_val = TFL.Environment.practically_infinite) :
        self__super.__init__ (init_val)
    # end def __init__

# end class Minimum_Counter

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Extreme_Value_Counter
