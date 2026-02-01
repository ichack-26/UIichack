# -*- coding: utf-8 -*-
# Copyright (C) 2001-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Primes
#
# Purpose
#    Provide list of prime numbers up to a certain boundary
#
# Revision Dates
#    25-Mar-2001 (CT)  Creation
#    11-Feb-2006 (CT)  Moved into package `TFL`
#     8-Nov-2006 (PGO) Primes are immutable
#    ««revision-date»»···
#--

from   _TFL               import TFL
import _TFL.Ordered_Set

from math               import sqrt

class Primes (TFL.Immutable_Ordered_Set) :
    """List of primes up to a certain boundary"""

    Factors      = {}
    U_Factors    = {}

    def is_prime (self, p) :
        return p in self.index_dict
    # end def is_prime

    def factors (self, number, _i = 0) :
        """Returns list of all prime factors of `number`."""
        try :
            return self.Factors [number]
        except KeyError :
            last_p = int (sqrt (number))
            for p in self [_i:] :
                if p > last_p :
                    ### if we didn't find any prime factor yet, `number` must
                    ### be prime itself
                    result = [number]
                    break
                div, mod = divmod (number, p)
                if mod == 0 :
                    result = [p] + self.factors (div, _i)
                    break
                _i = _i + 1
            else :
                raise ValueError (str (number), "Needs bigger prime table")
            self.Factors [number] = result
            return result
    # end def factors

    def u_factors (self, number, _i = 0) :
        """Returns list of all unique prime factors of `number` (i.e.,
           `result` contains each factor only once).
        """
        try :
            return self.U_Factors [number]
        except KeyError :
            last_p = int (sqrt (number))
            for p in self [_i:] :
                if p > last_p :
                    ### if we didn't find any prime factor yet, `number` must
                    ### be prime itself
                    result = [number]
                    break
                div, mod = divmod (number, p)
                if mod == 0 :
                    result = self.u_factors (div, _i) [:]
                    if [p] != result [0:1] :
                        result [0:0] = [p]
                    break
                _i = _i + 1
            else :
                raise ValueError (str (number), "Needs bigger prime table")
            self.U_Factors [number] = result
            return result
    # end def u_factors

    def __contains__ (self, item) :
        return item in self.index_dict
    # end def __contains__

# end class Primes

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Primes
