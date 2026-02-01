# -*- coding: utf-8 -*-
# Copyright (C) 2014-2019 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.formatted_repr
#
# Purpose
#    A portable `repr` that's nicely formatted
#
# Revision Dates
#    15-Oct-2014 (CT) Creation
#    17-Oct-2014 (CT) Add `compact`
#     1-Apr-2015 (CT) Apply `pyk.decoded` to `line.head`, `line.body`, and
#                     `line.tail` in `formatted_repr` to avoid
#                     `UnicodeDecodeError` for 8-bit strings
#    19-Aug-2019 (CT) Use `print_prepr`
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL._Meta.Single_Dispatch import Single_Dispatch
from   _TFL.Decorator             import Attributed, Decorator, dict_from_class
from   _TFL.Generators            import Look_Ahead_Gen
from   _TFL.portable_repr         import portable_repr, print_prepr
from   _TFL.pyk                   import pyk
from   _TFL.Record                import Record
from   _TFL.Sorted_By             import Sorted_By

import collections
import sys

FRIT = collections.namedtuple \
    ("FR_Iter_Tuple", "level, vanguard, head, body, tail")
SK   = Sorted_By ("+")

@dict_from_class
class _formatted_repr_properties (object) :
    """Dictionary of properties for `formatted_repr`"""

    FR_Iter_Tuple = FRIT
    SK            = SK
    Type_Name_Map = portable_repr.Type_Name_Map

    @Single_Dispatch
    def generic_formatted_repr_iter (obj, level, compact, seen) :
        yield FRIT (level, True, "", portable_repr.call (obj, seen), "")
    # end def generic_formatted_repr_iter

    @Decorator
    def recurses (f) :
        def _ (obj, level, compact, seen) :
            oid = id (obj)
            if oid in seen :
                yield FRIT \
                    (level, True, "", portable_repr.recursion_repr (obj), "")
            else :
                seen = set (seen)
                seen.add   (oid)
                compact_frit = formatted_repr._compact_frit \
                    (obj, level, compact, seen)
                if compact_frit is not None :
                    yield compact_frit
                else :
                    yield from f (obj, level, compact, seen) 
        return _
    # end def recurses

    @generic_formatted_repr_iter.add_type (dict)
    @recurses
    def dict (obj, level, compact, seen) :
        if obj :
            it = formatted_repr._items_iter (obj, level + 1, compact, seen)
            yield from formatted_repr._structure_iter \
                    (it, level, "{ ", ", ", " }") 
        else :
            yield FRIT (level, True, "", "{}", "")
    # end def dict

    @generic_formatted_repr_iter.add_type (list)
    @recurses
    def list (obj, level, compact, seen) :
        if obj :
            it = formatted_repr._values_iter (obj, level + 1, compact, seen)
            yield from formatted_repr._structure_iter \
                    (it, level, "[ ", ", ", " ]") 
        else :
            yield FRIT (level, True, "", "[]", "")
    # end def list

    @generic_formatted_repr_iter.add_type (Record)
    @recurses
    def record (obj, level, compact, seen) :
        def _iter (obj, level, compact, seen) :
            it = formatted_repr._record_iter (obj, level, compact, seen)
            yield from formatted_repr._structure_iter \
                    (it, level, "( ", ", ", " )") 
        it = _iter (obj, level + 1, compact, seen)
        yield from formatted_repr._structure_iter \
                (it, level, "Record ", "", "", nl_after_open = True) 
    # end def record

    @generic_formatted_repr_iter.add_type (set)
    def set (obj, level, compact, seen) :
        if obj :
            it = formatted_repr._values_iter \
                (sorted (obj, key = SK), level, compact, seen)
            yield from formatted_repr._structure_iter \
                    (it, level, "{ ", ", ", " }") 
        else :
            yield FRIT (level, True, "", "set()", "")
    # end def set

    @generic_formatted_repr_iter.add_type (tuple)
    @recurses
    def tuple (obj, level, compact, seen) :
        if obj :
            it = formatted_repr._values_iter (obj, level + 1, compact, seen)
            clos = (",", " )") if len (obj) == 1 else " )"
            yield from formatted_repr._structure_iter \
                    (it, level, "( ", ", ", clos) 
        else :
            yield FRIT (level, True, "", "()", "")
    # end def tuple

    def _compact_frit (obj, level, compact, seen) :
        if compact :
            body = portable_repr (obj)
            if len (body) < (80 if compact == True else compact) :
                return FRIT (level, True, "", body, "")
    # end def _compact_frit

    def _items_iter (obj, level, compact, seen) :
        for k, v in sorted (pyk.iteritems (obj), key = SK) :
            rk = portable_repr (k)
            it = formatted_repr.iter (v, level + 1, compact, seen)
            for x in formatted_repr._structure_iter \
                    (it, level, rk + " : ", "", "", nl_after_open = True) :
                yield x
    # end def _items_iter

    def _record_iter (obj, level, compact, seen) :
        for k, v in sorted (pyk.iteritems (obj._kw), key = SK) :
            rk = str (k)
            it = formatted_repr.iter (v, level + 1, compact, seen)
            yield from formatted_repr._structure_iter \
                    (it, level, rk + " = ", "", "", nl_after_open = True) 
    # end def _record_iter

    def _structure_iter (it, level, open, sep, clos, nl_after_open = False) :
        la_it      = Look_Ahead_Gen (it)
        la_it_iter = iter (la_it)
        e1         = next (la_it_iter)
        if isinstance (clos, pyk.string_types) :
            clos   = (clos, )
        if la_it.is_finished :
            hi = "".join ((open.rstrip (" "), e1.head))
            ti = "".join ((e1.tail, " ".join (clos).lstrip (" ")))
            yield FRIT (level, True, hi, e1.body, ti)
        else :
            if nl_after_open :
                yield FRIT (level,    True,  open,    "",      "")
                yield FRIT (e1.level, False, e1.head, e1.body, e1.tail)
            else :
                yield FRIT \
                    (level, True, "".join ((open, e1.head)), e1.body, e1.tail)
            for en in la_it_iter :
                hc = ""
                lc = en.level
                if en.vanguard :
                    hc = sep
                    lc = level
                yield FRIT \
                    (lc, False, "".join ((hc, en.head)), en.body, en.tail)
            for c in clos :
                c = c.lstrip (" ")
                if c :
                    yield FRIT (level, False, c, "", "")
    # end def _structure_iter

    def _values_iter (obj, level, compact, seen) :
        for v in obj :
            yield from formatted_repr.iter (v, level, compact, seen) 
    # end def _values_iter

# end class _formatted_repr_properties

_gfri = _formatted_repr_properties ["generic_formatted_repr_iter"]
_formatted_repr_properties.update \
    ( (  (k, getattr (_gfri, k))
      for k in ("add_type", "dispatch", "top_func")
      )
    , iter = _gfri
    )

@Attributed (** _formatted_repr_properties)
def formatted_repr (obj, level = 0, compact = False, indent = "  ") :
    """Return a formatted canonical string representation of `obj`."""
    return  "\n".join \
        ( ( "".join
              ( ( indent * line.level
                , pyk.decoded (line.head, pyk.user_config.output_encoding, "ascii")
                , pyk.decoded (line.body, pyk.user_config.output_encoding, "ascii")
                , pyk.decoded (line.tail, pyk.user_config.output_encoding, "ascii")

                )
              )
          ).replace (" ", " ").rstrip (" ")
        for line in formatted_repr.iter (obj, level, compact, seen = set ())
        )
# end def formatted_repr

@Attributed (** _formatted_repr_properties)
def formatted_repr_compact (obj, level = 0, compact = 80, indent = "  ") :
    """Return a compact formatted canonical string representation of `obj`."""
    return formatted_repr (obj, level, compact, indent)
# end def formatted_repr_compact

def test_formatted_repr (obj, level = 0, compact = False, indent = "  ") :
    """Return a formatted canonical string representation of `obj`.
    """
    return  "\n".join \
        ( portable_repr (line)
        for line in formatted_repr.iter (obj, level, compact, seen = set ())
        )
# end def test_formatted_repr

__doc__ = r"""
``formatted_repr`` returns a formatted canonical string
representation of `obj`.

Examples::

    >>> print (formatted_repr ([1, ("a", "b"), 2, ("c", ), 4, ()]))
    [ 1
    , ( 'a'
      , 'b'
      )
    , 2
    , ('c', )
    , 4
    , ()
    ]

    >>> print (formatted_repr (set ([1, "a", "2", 3])))
    { 1
    , 3
    , '2'
    , 'a'
    }

    >>> print (formatted_repr ([1, 2, 3, "a", u"b", "c", b"bytes"]))
    [ 1
    , 2
    , 3
    , 'a'
    , 'b'
    , 'c'
    , 'bytes'
    ]

    >>> d1 = { 1: u"a", 2: "b", "c" : 23, u"d" : 42 }
    >>> print (formatted_repr (d1))
    { 1 : 'a'
    , 2 : 'b'
    , 'c' : 23
    , 'd' : 42
    }

    >>> print (formatted_repr ([1, d1, 2, ["x", "y"], { 23: 42 }, (42, 23)]))
    [ 1
    , { 1 : 'a'
      , 2 : 'b'
      , 'c' : 23
      , 'd' : 42
      }
    , 2
    , [ 'x'
      , 'y'
      ]
    , {23 : 42}
    , ( 42
      , 23
      )
    ]

    >>> l1 = [1, 2, [], 3]
    >>> l2 = ["a", ["b"], "c"]
    >>> l1.append (l2)
    >>> l2.append (l1)
    >>> l3 = ["x", "y", l1, l2, "z"]

    >>> print (formatted_repr (l1))
    [ 1
    , 2
    , []
    , 3
    , [ 'a'
      , ['b']
      , 'c'
      , [...]
      ]
    ]

    >>> print (formatted_repr (l2))
    [ 'a'
    , ['b']
    , 'c'
    , [ 1
      , 2
      , []
      , 3
      , [...]
      ]
    ]

    >>> print_prepr (l3)
    ['x', 'y', [1, 2, [], 3, ['a', ['b'], 'c', [...]]], ['a', ['b'], 'c', [1, 2, [], 3, [...]]], 'z']

    >>> print (formatted_repr (l3))
    [ 'x'
    , 'y'
    , [ 1
      , 2
      , []
      , 3
      , [ 'a'
        , ['b']
        , 'c'
        , [...]
        ]
      ]
    , [ 'a'
      , ['b']
      , 'c'
      , [ 1
        , 2
        , []
        , 3
        , [...]
        ]
      ]
    , 'z'
    ]

    >>> print (formatted_repr_compact (l3))
    [ 'x'
    , 'y'
    , [1, 2, [], 3, ['a', ['b'], 'c', [...]]]
    , ['a', ['b'], 'c', [1, 2, [], 3, [...]]]
    , 'z'
    ]

    >>> print (formatted_repr (l3, compact = 120))
    ['x', 'y', [1, 2, [], 3, ['a', ['b'], 'c', [...]]], ['a', ['b'], 'c', [1, 2, [], 3, [...]]], 'z']

    >>> thing = ["abc", "dfg", {1: "abc", 2: "xyz", 0: (42, 137)}]

    >>> print (formatted_repr (thing))
    [ 'abc'
    , 'dfg'
    , { 0 :
          ( 42
          , 137
          )
      , 1 : 'abc'
      , 2 : 'xyz'
      }
    ]

    >>> thing [-1].update ({b"recursive" : thing, "nested" : ["u", "v"]})
    >>> print (formatted_repr (thing))
    [ 'abc'
    , 'dfg'
    , { 0 :
          ( 42
          , 137
          )
      , 1 : 'abc'
      , 2 : 'xyz'
      , 'nested' :
          [ 'u'
          , 'v'
          ]
      , 'recursive' : [...]
      }
    ]

    >>> print (formatted_repr_compact (thing))
    [ 'abc'
    , 'dfg'
    , { 0 : (42, 137)
      , 1 : 'abc'
      , 2 : 'xyz'
      , 'nested' : ['u', 'v']
      , 'recursive' : [...]
      }
    ]

    >>> print (formatted_repr (Record (qux = 23)))
    Record (qux = 23)

    >>> thinr = Record (foo = 42, bar = u"wrzl", baz = "MadamImadam")
    >>> print (formatted_repr (thinr))
    Record
      ( bar = 'wrzl'
      , baz = 'MadamImadam'
      , foo = 42
      )

    >>> thinq = ["abc", "dfg", { 1 : "yxz" }, thinr]
    >>> print (formatted_repr (thinq))
    [ 'abc'
    , 'dfg'
    , {1 : 'yxz'}
    , Record
        ( bar = 'wrzl'
        , baz = 'MadamImadam'
        , foo = 42
        )
    ]

"""

__all__ = ("formatted_repr", "formatted_repr_compact")

if __name__ != "__main__" :
    TFL._Export (* __all__)
### __END__ TFL.formatted_repr
