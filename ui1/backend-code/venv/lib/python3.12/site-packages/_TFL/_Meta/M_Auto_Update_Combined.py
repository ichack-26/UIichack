# -*- coding: utf-8 -*-
# Copyright (C) 2015-2022 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.Meta.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Meta.M_Auto_Update_Combined
#
# Purpose
#    Metaclass that automatically applies `update_combined` to a
#    class's attribute and the corresponding attribute of all its base classes
#
# Revision Dates
#    26-Jan-2015 (CT) Creation
#     6-Mar-2015 (CT) Add `except` to `_m_update_combine`
#     5-Aug-2015 (CT) Improve `__doc__`
#    19-Aug-2019 (CT) Use `print_prepr`
#    14-Oct-2022 (CT) Save uncombined value of auto-combined attribute
#    15-Oct-2022 (CT) Filter identical values before combining
#    ««revision-date»»···
#--

"""
Metaclass that automatically applies
:func:`~_TFL.update_combined.update_combined_many` to a class's attribute and
the corresponding attribute of all its base classes.

One specifies the attributes to be automatically combined by listing
their names in either :attr:`_attrs_to_update_combine` or
:attr:`_attrs_uniq_to_update_combine`.

::

    >>> from   _TFL.portable_repr import print_prepr

    >>> class A (object, metaclass = M_Auto_Update_Combined) :
    ...     _attrs_to_update_combine      = ("foo", "bar", "qux")
    ...     _attrs_uniq_to_update_combine = ("quux", )
    ...     foo                           = set ([1, 2, 3])
    ...     qux = quux                    = [(0, ), (1, )]
    ...
    >>> class B (A) :
    ...     _attrs_to_update_combine      = ("baz", )
    ...     foo                           = set ([5, 4, 3])
    ...     bar                           = set ("ab")
    ...     qux = quux                    = [(2, ), (0, )]
    ...
    >>> class C (B) :
    ...     bar                           = set ("xyz")
    ...     qux = quux                    = [(0, 1, ), (3, )]

    >>> print_prepr (A.foo, A.bar, A.qux, A.quux)
    {1, 2, 3} <Undef/value> [(0,), (1,)] [(0,), (1,)]
    >>> print_prepr (B.foo, B.bar, B.qux, B.quux, B.baz)
    {1, 2, 3, 4, 5} {'a', 'b'} [(0,), (1,), (2,), (0,)] [(0,), (1,), (2,)] <Undef/value>
    >>> print_prepr (C.foo, C.bar, C.qux, C.quux, C.baz)
    {1, 2, 3, 4, 5} {'a', 'b', 'x', 'y', 'z'} [(0,), (1,), (2,), (0,), (0, 1), (3,)] [(0,), (1,), (2,), (0, 1), (3,)] <Undef/value>

    >>> class P (object, metaclass = M_Auto_Update_Combined) :
    ...     _attrs_to_update_combine      = ("foo", "bar")
    ...     bar                           = dict (x = 1, y = 2)
    >>> class R (object) :
    ...     foo                           = dict (u = 1, v = "a")
    ...     bar                           = dict (y = 3, z = 42)
    ...     baz                           = dict (a = 0)
    >>> class PR (P, R) :
    ...     _attrs_to_update_combine      = ("baz", )
    ...     baz                           = dict (b = 42)
    >>> class RP (R, P) :
    ...     foo                           = dict (v = "b", w = "a")
    ...     bar                           = dict (x = "z", z = -42)
    ...     baz                           = dict (c = 137)

    >>> print_prepr (P.foo, P.bar)
    <Undef/value> {'x' : 1, 'y' : 2}
    >>> print_prepr (R.foo,  R.bar, R.baz)
    {'u' : 1, 'v' : 'a'} {'y' : 3, 'z' : 42} {'a' : 0}
    >>> print_prepr (PR.foo, PR.bar, PR.baz)
    {'u' : 1, 'v' : 'a'} {'x' : 1, 'y' : 2, 'z' : 42} {'a' : 0, 'b' : 42}
    >>> print_prepr (RP.foo, RP.bar, RP.baz)
    {'u' : 1, 'v' : 'b', 'w' : 'a'} {'x' : 'z', 'y' : 3, 'z' : -42} {'c' : 137}

"""

from   _TFL                           import TFL
from   _TFL.pyk                       import pyk

from   _TFL.predicate                 import uniq, uniq_p
from   _TFL.update_combined           import update_combined_many

import _TFL._Meta.M_Auto_Combine_Sets
import _TFL._Meta.M_Class

import itertools

class M_Auto_Update_Combined (TFL.Meta.M_Auto_Combine_Sets, TFL.Meta.M_Class) :

    _attrs_to_update_combine      = ()
    _attrs_uniq_to_update_combine = ()

    _sets_to_combine              = \
        ("_attrs_to_update_combine", "_attrs_uniq_to_update_combine")

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls._m_update_combine  (bases, dct)
    # end def __init__

    def _m_update_combine (cls, bases, dct) :
        undef = update_combined_many.Undef
        def _gen (cls, bases, name) :
            yield from uniq_p \
                ( (getattr (c, name, undef) for c in reversed ((cls, ) + bases))
                , lambda x : id (x)
                )
        for name in cls._attrs_to_update_combine :
            old = dct.get (name, undef)
            try :
                new = update_combined_many (* _gen (cls, bases, name))
            except Exception as exc :
                print \
                    ( "*** Exception when trying to update/combined", name
                    , "for class", cls
                    )
                raise
            setattr (cls, "_%s__uncombined__" % name, old)
            setattr (cls, name, new)
        for name in cls._attrs_uniq_to_update_combine :
            old = dct.get (name, undef)
            ucm = update_combined_many (* _gen (cls, bases, name))
            new = ucm.__class__ (uniq (ucm))
            setattr (cls, "_%s__uncombined__" % name, old)
            setattr (cls, name, new)
    # end def _m_update_combine

# end class M_Auto_Update_Combined

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Update_Combined
