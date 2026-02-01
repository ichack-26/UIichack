# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Sorted_By
#
# Purpose
#    Implement composite sort-key for list of sort criteria
#
# Revision Dates
#    18-Sep-2009 (CT) Creation
#    19-Sep-2009 (MG) `_desc_key` factored to avoind binding problems of the
#                     `get` function
#    21-Sep-2009 (CT) `Descending.__lt__` fixed
#    21-Sep-2009 (CT) `Desc_Getter` added to improve introspection and to
#                     replace `_desc_key`
#    21-Sep-2009 (CT) `Descending.__eq__` added and doctests fixed
#    22-Sep-2009 (CT) `Descending` made `totally_ordered`
#                     `Descending.__eq__` removed again
#    14-Oct-2009 (CT) Signature of `Sorted_By` changed from `criteria`
#                     to `* criteria`
#     3-Dec-2009 (CT) `__iter__` added
#     3-Dec-2009 (CT) `keys` changed to allow `-` following `.`, too
#     4-Dec-2009 (CT) `Sorted_By.__call__` changed to tolerate `LookupError`
#                     and `AttributeError` exceptions raised by `key`
#     4-Dec-2009 (CT) `Sorted_By_Strict` added
#     4-Dec-2009 (CT) `Sorted_By.__call__` and `Desc_Getter.__call__` changed
#                     to allow comparison of unequal types in Python 3.x
#    16-Jul-2015 (CT) Use `expect_except` in doc-tests
#    25-Jul-2016 (CT) Change `type_name` to allow binary `byte-string` values
#    ««revision-date»»···
#--

from   _TFL                       import TFL

import _TFL._Meta.Object
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.totally_ordered import totally_ordered
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk

import _TFL.Accessor

class Desc_Getter (TFL.Meta.Object) :

    @totally_ordered
    class Descending (TFL.Meta.Object) :

        def __init__ (self, key) :
            self.key = key
        # end def __init__

        def __lt__ (self, rhs) :
            return self.key > rhs.key
        # end def __lt__

    # end class Descending

    def __init__ (self, getter) :
        self.getter = getter
    # end def __init__

    def __call__ (self, x) :
        v = self.getter (x)
        return self.Descending (Sorted_By.typed_key (v))
    # end def __call__

    def __repr__ (self) :
       return "%s-%s" % (self.Descending.__name__, portable_repr (self.getter))
    # end def __repr__

# end class Desc_Getter

class Sorted_By (TFL.Meta.Object) :
    """Composite sort key for list of sort criteria.

       ::

           >>> from _TFL.Record import Record as R
           >>> NL = chr (10)
           >>> def show (l, key) :
           ...     sl = sorted (l, key = key)
           ...     print (NL.join (str (s) for s in sl))
           ...
           >>> l = [ R (a = 1, b = 1, c = "abcd")
           ...     , R (a = 1, b = 2, c = "ABCD")
           ...     , R (a = 1, b = 2, c = "efg")
           ...     , R (a = 2, b = 1, c = "xyz")
           ...     , R (a = 2, b = 1, c = " xyzz")
           ...     , R (a = 2, b = 1, c = "  xyzzz")
           ...     ]
           >>> print (NL.join (str (s) for s in l))
           (a = 1, b = 1, c = 'abcd')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("a"))
           (a = 1, b = 1, c = 'abcd')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("a", "b"))
           (a = 1, b = 1, c = 'abcd')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("a", "-b"))
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("b", "a"))
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           >>> show (l, key = Sorted_By ("-b", "a"))
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("-b", "-a"))
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = 'xyz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           (a = 1, b = 1, c = 'abcd')
           >>> show (l, key = Sorted_By ("b", "c"))
           (a = 2, b = 1, c = '  xyzzz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = 'xyz')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           >>> show (l, key = Sorted_By ("b", "-c"))
           (a = 2, b = 1, c = 'xyz')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           (a = 1, b = 2, c = 'efg')
           (a = 1, b = 2, c = 'ABCD')
           >>> show (l, key = Sorted_By ("-b", "c"))
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = '  xyzzz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = 'xyz')
           >>> show (l, key = Sorted_By ("-b", "-c"))
           (a = 1, b = 2, c = 'efg')
           (a = 1, b = 2, c = 'ABCD')
           (a = 2, b = 1, c = 'xyz')
           (a = 1, b = 1, c = 'abcd')
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> show (l, key = Sorted_By ("c"))
           (a = 2, b = 1, c = '  xyzzz')
           (a = 2, b = 1, c = ' xyzz')
           (a = 1, b = 2, c = 'ABCD')
           (a = 1, b = 1, c = 'abcd')
           (a = 1, b = 2, c = 'efg')
           (a = 2, b = 1, c = 'xyz')
           >>> show (["1", 0, "42", 2.4], Sorted_By (int))
           0
           1
           2.4
           42
           >>> show ([3, "1", 0, "42", 2.4], Sorted_By (lambda x : x))
           0
           2.4
           3
           1
           42

           >>> import warnings; warnings.filterwarnings ( "error",  "comparing unequal types not supported in 3.x")
           >>> l = [ R (a = 1, b = 1, c = "abcd", d = "foo")
           ...     , R (a = 1, b = 2, c = "ABCD", d = "bar")
           ...     , R (a = 1, b = 2, c = "efg",  d = 42)
           ...     , R (a = 2, b = 1, c = "xyz",  d = 137)
           ...     , R (a = 2, b = 1, c = " xyzz")
           ...     , R (a = 2, b = 1, c = "  xyzzz")
           ...     ]
           >>> show (l, Sorted_By ("d"))
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           (a = 1, b = 2, c = 'efg', d = 42)
           (a = 2, b = 1, c = 'xyz', d = 137)
           (a = 1, b = 2, c = 'ABCD', d = 'bar')
           (a = 1, b = 1, c = 'abcd', d = 'foo')
           >>> show (l, Sorted_By ("-d"))
           (a = 1, b = 1, c = 'abcd', d = 'foo')
           (a = 1, b = 2, c = 'ABCD', d = 'bar')
           (a = 2, b = 1, c = 'xyz', d = 137)
           (a = 1, b = 2, c = 'efg', d = 42)
           (a = 2, b = 1, c = ' xyzz')
           (a = 2, b = 1, c = '  xyzzz')
           >>> with expect_except (AttributeError) :
           ...     show (l, Sorted_By_Strict ("d"))
           AttributeError: d
           >>> with expect_except (AttributeError) :
           ...     show (l, Sorted_By_Strict ("-d"))
           AttributeError: d

    """

    Desc             = Desc_Getter
    Ignore_Exception = (LookupError, AttributeError)

    type_name_map = dict \
        ( portable_repr.Type_Name_Map
        , bool    = "number"
        , Decimal = "number"
        , float   = "number"
        , int     = "number"
        , long    = "number"
        )

    def __init__ (self, * criteria) :
        self.criteria = criteria
    # end def __init__

    def __call__ (self, x) :
        def gen (x, keys, typed_key) :
            Ignore = self.Ignore_Exception
            for key in keys :
                try :
                    v = key (x)
                except Ignore :
                    v = None
                yield typed_key (v)
        return tuple (gen (x, self.keys, self.typed_key))
    # end def __call__

    @Once_Property
    def keys (self) :
        result = []
        for c in self.criteria :
            if hasattr (c, "__call__") :
                key = c
            elif c == "+" :
                key = self.typed_value
            elif c == "-" :
                key = Desc_Getter (self.typed_value)
            elif c.startswith ("-") or ".-" in c :
                key = Desc_Getter (getattr (TFL.Getter, c.replace ("-", "")))
            else :
                key = getattr (TFL.Getter, c)
            result.append (key)
        if not result :
            result.append (self.typed_value)
        return result
    # end def keys

    @classmethod
    def type_name (cls, v) :
        t = type (v)
        n = t.__name__
        r = cls.type_name_map.get (n, n)
        if r == "byte-string" and v.isalnum :
            r = "text-string"
            v = str (v, "latin1")
        return r, v
    # end def type_name

    @classmethod
    def typed_key (cls, v) :
        result = v
        typer  = cls.type_name
        if isinstance (v, (list, tuple)) :
            result = tuple (typer (x) for x in v)
        return typer (result)
    # end def typed_key

    @staticmethod
    def typed_value (x) :
        return x
    # end def typed_value

    def __iter__ (self) :
        return iter (self.criteria)
    # end def __iter__

    def __repr__ (self) :
       return "<%s: %s>" % \
           ( self.__class__.__name__
           , ", ".join (portable_repr (key) for key in self.keys)
           )
    # end def __repr__

# end class Sorted_By

class Sorted_By_Strict (Sorted_By) :
    """Strict `Sorted_By` that raises any exception triggered by a sort
       criterion.
    """

    class Ignore_Exception (Exception) : pass

# end class Sorted_By_Strict

__doc__ = """
Easy declaration of composite sort-keys for list of sort criteria, some of
which might be reversed.

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.Sorted_By
