# -*- coding: utf-8 -*-
# Copyright (C) 2006-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.defaultdict
#
# Purpose
#    dict with default value for missing entries
#
# Revision Dates
#    13-Mar-2006 (CT) Creation (for Python 2.4)
#    20-Jun-2007 (CT) Adapted to Python 2.5
#    20-Jun-2007 (CT) `defaultdict_kd` added
#    29-Aug-2008 (CT) s/super(...)/__super/
#    30-May-2012 (CT) Add `defaultdict_nested`
#    20-Mar-2013 (CT) Remove pre-2.5 support
#    20-Mar-2013 (CT) Add `defaultdict_cb` and `defaultdict_int`
#    23-May-2013 (CT) Use `TFL.Meta.BaM` for Python-3 compatibility
#    ««revision-date»»···
#--

"""
Python 2.5 provides `collections.defaultdict`.

Originally, this module allowed the use of `defaultdict` in earlier versions
of Python.

In addition, this module provides

* :class:`defaultdict_cb`: defaultdict with class-based `default_factory`

* :class:`defaultdict_int`: defaultdict using `int` as `default_factory`

* :class:`defaultdict_kd`: defaultdict that passes the missing `key` to the
  `default_factory`

::

    >>> zd = defaultdict (int)
    >>> zd [1] = 42
    >>> zd [2] = 137
    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137)]

    >>> zd [3]
    0
    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137), (3, 0)]

    >>> zd [4] += 1
    >>> zd [4]
    1

    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137), (3, 0), (4, 1)]

    >>> zd = defaultdict_int ()
    >>> zd [1] = 42
    >>> zd [2] = 137
    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137)]

    >>> zd [3]
    0
    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137), (3, 0)]

    >>> zd [4] += 1
    >>> zd [4]
    1

    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137), (3, 0), (4, 1)]

    >>> ze = defaultdict_int (zd)
    >>> ze [100] = sum (ze)

    >>> sorted (pyk.iteritems (zd))
    [(1, 42), (2, 137), (3, 0), (4, 1)]
    >>> sorted (pyk.iteritems (ze))
    [(1, 42), (2, 137), (3, 0), (4, 1), (100, 10)]

"""

from   _TFL import TFL
from   _TFL.pyk import pyk

import _TFL._Meta.M_Class

from   collections import defaultdict

class _defaultdict_ (defaultdict, metaclass = TFL.Meta.M_Class) :

    pass

# end class _defaultdict_

class defaultdict_cb (_defaultdict_) :
    """defaultdict([mapping|iterable], ** kw) --> dict with class based default factory"""

    default_factory = None

    def __init__ (self, * args, ** kw) :
        self.__super.__init__ (self.default_factory, * args, ** kw)
    # end def __init__

# end class defaultdict_cb

defaultdict_int = defaultdict_cb.New \
    (__name__ = "defaultdict_int", default_factory = int)

class defaultdict_kd (_defaultdict_) :
    """defaultdict_kd(_default_factory) --> dict with default factory

       The default factory is called with the `key` argument to produce
       a new value when a key is not present, in __getitem__ only.
       A defaultdict compares equal to a dict with the same items.

       >>> sort_key = lambda x : (type (x [0]).__name__, x [0])
       >>> dd = defaultdict_kd (lambda k : k * 2)
       >>> sorted (pyk.iteritems (dd), key = sort_key)
       []
       >>> dd [1] = 42
       >>> dd [2]
       4
       >>> dd ["a"]
       'aa'
       >>> sorted (pyk.iteritems (dd), key = sort_key)
       [(1, 42), (2, 4), ('a', 'aa')]
    """

    def __missing__ (self, key) :
        if self.default_factory is None :
            raise KeyError (key)
        result = self [key] = self.default_factory (key)
        return result
    # end def __missing__

# end class defaultdict_kd

def defaultdict_nested (depth = 1, leaf = dict) :
    """Return a `defaultdict` nested to `depth` with leaves of type `leaf`.

    >>> from _TFL.formatted_repr import formatted_repr as formatted
    >>> ddn_1 = defaultdict_nested (1, int)
    >>> ddn_1 # doctest:+ELLIPSIS
    defaultdict(<... 'int'>, {})
    >>> ddn_2 = defaultdict_nested (2, int)
    >>> ddn_1 ["foo"] += 1
    >>> ddn_1 ["foo"] += 1
    >>> ddn_1 # doctest:+ELLIPSIS
    defaultdict(<... 'int'>, {'foo': 2})
    >>> ddn_2 ["foo"] ["bar"] += 42
    >>> print (formatted (ddn_1))
    {'foo' : 2}
    >>> print (formatted (ddn_2))
    {'foo' : {'bar' : 42}}
    >>> ddn_7 = defaultdict_nested (7, int)
    >>> ddn_7 [1] [2] [3] [4] [5] [6] [7] = "foo"
    >>> print (formatted (ddn_7))
    {1 : {2 : {3 : {4 : {5 : {6 : {7 : 'foo'}}}}}}}

    >>> ddn_7 [0] [1] [2] [3] [4] [5] [6] [7] = "bar"
    Traceback (most recent call last):
      ...
    TypeError: 'int' object does not support item assignment
    """
    result = defaultdict (leaf)
    for i in range (depth - 1) :
        result = defaultdict (lambda r = result : r)
    return result
# end def defaultdict_nested

if __name__ != "__main__" :
    TFL._Export \
        ( "defaultdict", "defaultdict_cb", "defaultdict_int", "defaultdict_kd"
        , "defaultdict_nested", "_defaultdict_"
        )
### __END__ TFL.defaultdict
