# -*- coding: utf-8 -*-
# Copyright (C) 2005-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Memoizer
#
# Purpose
#    Add memoization to functions and methods without changing the
#    source code of the memoized components
#
# Revision Dates
#     5-Jun-2005 (CT) Creation
#    22-Feb-2013 (CT) Use `TFL.Undef ()` not `object ()`
#    28-May-2013 (CT) Fix doc-test for print-function
#    ««revision-date»»···
#--

"""
Add memoization to functions and methods of modules/classing without
changing the source code of the memoized components.

Caveats:
- the functions/methods memoized must be idempotent
- all arguments passed to the function/methods must be hashable
- keyword arguments cannot be used

    >>> class Test :
    ...     def method (self, i) :
    ...         print ("    Test.method called with", i)
    ...         return i * i
    ...
    >>> Memoizer.add_method (Test, "method")
    >>> t = Test ()
    >>> for j in range (5) :
    ...     print ("First  call", j)
    ...     print ("   ", t.method (j))
    ...     print ("Second call", j)
    ...     print ("   ", t.method (j))
    ...
    First  call 0
        Test.method called with 0
        0
    Second call 0
        0
    First  call 1
        Test.method called with 1
        1
    Second call 1
        1
    First  call 2
        Test.method called with 2
        4
    Second call 2
        4
    First  call 3
        Test.method called with 3
        9
    Second call 3
        9
    First  call 4
        Test.method called with 4
        16
    Second call 4
        16

"""

from   _TFL             import TFL
from   _TFL.pyk         import pyk
import _TFL._FMW.Wrapper
import _TFL.Undef

class _Memoized_ (TFL.FMW.Wrapped_FM) :
    """Wrapper adding memoization to a single function or method"""

    __undef = TFL.Undef ()

    def __init__ (self, * args, ** kw) :
        self._cache = {}
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    def __call__ (self, * args) :
        _cache = self._cache
        _undef = self.__undef
        result = _cache.get (args, _undef)
        if result is _undef :
            result = _cache [args] = self.fct (* args)
        return result
    # end def __call__

# end class _Memoized_

class _Memoizer_ (TFL.FMW.Wrapper) :
    """Add memoization to functions and methods without changing the
       source code of the memoized components.
    """

    Wrapped_FM = _Memoized_

# end class _Memoizer_

Memoizer = _Memoizer_ ()

if __name__ != "__main__" :
    TFL.FMW._Export ("Memoizer")
### __END__ Memoizer
