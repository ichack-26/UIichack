# -*- coding: utf-8 -*-
# Copyright (C) 2009-2013 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Int_Partition
#
# Purpose
#    Compute partition of (positive) integers
#
#    http://en.wikipedia.org/wiki/Partition_(number_theory)
#
# Revision Dates
#    29-Apr-2009 (CT) Creation started
#    30-Apr-2009 (CT) Refactored to remove redundancy and improve caching
#    30-Apr-2009 (CT) Bug fixed following advice of Daniel Albeseder
#    30-Apr-2009 (CT) Tests for values of partition function added
#    ««revision-date»»···
#--

from   _TFL import TFL
from   _TFL.pyk import pyk

import _TFL._Meta.Object

class _Int_Partition_ (TFL.Meta.Object) :
    """Compute partition of (positive) integers.

       >>> for i in range (6) :
       ...   print (i, list (Int_Partition (i)))
       ...
       0 []
       1 [(1,)]
       2 [(2,), (1, 1)]
       3 [(3,), (2, 1), (1, 1, 1)]
       4 [(4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1)]
       5 [(5,), (4, 1), (3, 2), (3, 1, 1), (2, 2, 1), (2, 1, 1, 1), (1, 1, 1, 1, 1)]

       >>> Int_Partition [2,0]
       ((2,),)
       >>> Int_Partition [2,1]
       ((1, 1),)
       >>> Int_Partition [2,2]
       ()

       >>> for n in range (9) :
       ...   for l in range (n) :
       ...     print (n, l, Int_Partition [n, l])
       ...
       1 0 ((1,),)
       2 0 ((2,),)
       2 1 ((1, 1),)
       3 0 ((3,),)
       3 1 ((2, 1),)
       3 2 ((1, 1, 1),)
       4 0 ((4,),)
       4 1 ((3, 1), (2, 2))
       4 2 ((2, 1, 1),)
       4 3 ((1, 1, 1, 1),)
       5 0 ((5,),)
       5 1 ((4, 1), (3, 2))
       5 2 ((3, 1, 1), (2, 2, 1))
       5 3 ((2, 1, 1, 1),)
       5 4 ((1, 1, 1, 1, 1),)
       6 0 ((6,),)
       6 1 ((5, 1), (4, 2), (3, 3))
       6 2 ((4, 1, 1), (3, 2, 1), (2, 2, 2))
       6 3 ((3, 1, 1, 1), (2, 2, 1, 1))
       6 4 ((2, 1, 1, 1, 1),)
       6 5 ((1, 1, 1, 1, 1, 1),)
       7 0 ((7,),)
       7 1 ((6, 1), (5, 2), (4, 3))
       7 2 ((5, 1, 1), (4, 2, 1), (3, 3, 1), (3, 2, 2))
       7 3 ((4, 1, 1, 1), (3, 2, 1, 1), (2, 2, 2, 1))
       7 4 ((3, 1, 1, 1, 1), (2, 2, 1, 1, 1))
       7 5 ((2, 1, 1, 1, 1, 1),)
       7 6 ((1, 1, 1, 1, 1, 1, 1),)
       8 0 ((8,),)
       8 1 ((7, 1), (6, 2), (5, 3), (4, 4))
       8 2 ((6, 1, 1), (5, 2, 1), (4, 3, 1), (4, 2, 2), (3, 3, 2))
       8 3 ((5, 1, 1, 1), (4, 2, 1, 1), (3, 3, 1, 1), (3, 2, 2, 1), (2, 2, 2, 2))
       8 4 ((4, 1, 1, 1, 1), (3, 2, 1, 1, 1), (2, 2, 2, 1, 1))
       8 5 ((3, 1, 1, 1, 1, 1), (2, 2, 1, 1, 1, 1))
       8 6 ((2, 1, 1, 1, 1, 1, 1),)
       8 7 ((1, 1, 1, 1, 1, 1, 1, 1),)

       >>> for i in range (11) :
       ...   print ("p(%d) = %d" % (i, len (list (Int_Partition (i)))))
       ...
       p(0) = 0
       p(1) = 1
       p(2) = 2
       p(3) = 3
       p(4) = 5
       p(5) = 7
       p(6) = 11
       p(7) = 15
       p(8) = 22
       p(9) = 30
       p(10) = 42
    """

    _Table  = {}

    def __call__ (self, n) :
        """Generate all partitions of the positive integer `n`, i.e., all
           sums of positive integers adding up to `n`.
        """
        for l in range (n) :
            yield from self [(n, l)] 
    # end def __call__

    def __getitem__ (self, key) :
        """Return all partitions of length `l` for the positive integer
           `n`, i.e., all sums of `l + 1` positive integers adding up to `n`.
        """
        (n, l) = key
        try :
            result = self._Table [(n, l)]
        except KeyError :
            result = self._Table [(n, l)] = tuple (self._generate (n, l))
        return result
    # end def __getitem__

    def _generate (self, n, l) :
        if l == 0 :
            yield (n, )
        else :
            for a in range (n - l, 0 , -1) :
                for ps in self [(n - a, l - 1)] :
                    if a >= ps [0] :
                        yield (a, ) + ps
    # end def _generate

# end class _Int_Partition_

Int_Partition = _Int_Partition_ ()

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ Int_Partition
