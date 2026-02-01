# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Christian Tanzer All rights reserved
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
#    TFL.update_combined
#
# Purpose
#    Update a dictionary/list/set with elements of another
#    dictionary/list/set, combining existing keys or values
#
# Revision Dates
#    21-Aug-2014 (CT) Creation
#    26-Jan-2015 (CT) Add `update_combined.Undef`, ".List_Filtered"
#    26-Jan-2015 (CT) Add type `Undef` to `update_combined`,
#                     `update_combined_value`
#    26-Jan-2015 (CT) DRY `update_combined`
#    26-Jan-2015 (CT) Add `update_combined_many`
#    26-Jan-2015 (CT) Add `update_combined__set` to force `rhs` to `set`
#     6-Mar-2015 (CT) Add `except` to `update_combined`, `update_combined__set`
#     5-Aug-2015 (CT) Add `Dont_Combine` to `__doc__`
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL._Meta.Single_Dispatch import Single_Dispatch, Single_Dispatch_2nd
from   _TFL.Decorator             import Attributed
from   _TFL.pyk                   import pyk

import _TFL._Meta.Object
import _TFL.Undef

_undef = TFL.Undef ("value")

class Dont_Combine (object) :
    """Mixin indicating that the value should replace an existing value,
       instead of combining with it.
    """
# end class Dont_Combine

class dict_dont_combine (Dont_Combine, dict) :
    """Dictionary that doesn't combine, but replaces, under `update_combined`"""
# end class dict_dont_combine

class list_dont_combine (Dont_Combine, list) :
    """List that doesn't combine, but replaces, under `update_combined`"""
# end class list_dont_combine

class set_dont_combine (Dont_Combine, set) :
    """Set that doesn't combine, but replaces, under `update_combined`"""
# end class set_dont_combine

class tuple_dont_combine (Dont_Combine, tuple) :
    """Tuple that doesn't combine, but replaces, under `update_combined`"""
# end class tuple_dont_combine

class list_filtered (list, metaclass = TFL.Meta.M_Class) :
    """List that filters elements from ``lhs`` when `update_combined` as
       ``rhs``.
    """

    def __init__ (self, * args, ** kw) :
        self.Filter = kw.pop  ("filter")
        assert not kw, kw
        self.__super.__init__ (args)
    # end def __init__

# end class list_filtered

_update_combined_props = dict \
    ( Dict_DC       = dict_dont_combine
    , List_DC       = list_dont_combine
    , List_Filtered = list_filtered
    , Set_DC        = set_dont_combine
    , Tuple_DC      = tuple_dont_combine
    , Undef         = _undef
    )

@Single_Dispatch
@Attributed (** _update_combined_props)
def update_combined (lhs, rhs) :
    """Generic function to update ``lhs`` with the elements of ``rhs``,
       combining existing elements/keys.
    """
    try :
        return update_combined_value (lhs, rhs)
    except Exception as exc :
        print \
            ( "*** Exception during update_combined for"
            , "\n    lhs = ", repr (lhs)
            , "\n    rhs = ", repr (rhs)
            )
        raise
# end def update_combined

@Attributed (** _update_combined_props)
def update_combined_many (lhs, * rest) :
    """Update ``lhs`` with the elements of all of ``rest``, combining existing
       keys.
    """
    result = lhs
    for rhs in rest :
        result = update_combined (result, rhs)
    return result
# end def update_combined_many

@update_combined.add_type (set)
def update_combined__set (lhs, rhs) :
    if not isinstance (rhs, (set, TFL.Undef)) :
        rhs = set (rhs)
    try :
        return update_combined_value (lhs, rhs)
    except Exception as exc :
        print \
            ( "*** Exception during update_combined__set for"
            , "\n    lhs = ", repr (lhs)
            , "\n    rhs = ", repr (rhs)
            )
        raise
# end def update_combined__set

@update_combined.add_type (TFL.Undef)
def update_combined__undef (lhs, rhs) :
    return rhs
# end def update_combined__undef

@Single_Dispatch_2nd
def update_combined_value (lhs, rhs) :
    """Generic functions for update/combining the values ``lhs`` and ``rhs``.

       Values of types like ``dict``, ``list``, ``set`` combine; values
       derived from ``Dont_Combine`` and of types like ``int``, ``float``,
       ``str`` are replaced by ``rhs``.
    """
    return rhs
# end def update_combined_value

@update_combined_value.add_type (dict)
def update_combined_value__dict (lhs, rhs) :
    result = lhs.__class__ (lhs)
    skip   = TFL.is_undefined
    for k, r in pyk.iteritems (rhs) :
        if not skip (r) :
            l = lhs.get (k, _undef)
            result [k] = r if l is _undef else update_combined_value (l, r)
    return result
# end def update_combined_value__dict

@update_combined_value.add_type (list_filtered)
def update_combined_value__list_filtered (lhs, rhs) :
    result  = lhs.__class__ (l for l in lhs if rhs.Filter (l))
    result += rhs
    return result
# end def update_combined_value__list_filtered

@update_combined_value.add_type (list, tuple)
def update_combined_value__list (lhs, rhs) :
    result  = lhs.__class__ (lhs)
    result += rhs
    return result
# end def update_combined_value__list

@update_combined_value.add_type (set)
def update_combined_value__set (lhs, rhs) :
    result  = lhs.__class__ (lhs)
    result |= rhs
    return result
# end def update_combined_value__set

@update_combined_value.add_type (Dont_Combine)
def update_combined_value__dont_combine (lhs, rhs) :
    return rhs
# end def update_combined_value__dont_combine

@update_combined_value.add_type (TFL.Undef)
def update_combined_value__undef (lhs, rhs) :
    return lhs
# end def update_combined_value__undef

__doc__ = """
Update a dictionary/list/set with elements of another
dictionary/list/set, combining existing keys or values, instead of
replacing like the standard ``dict`` method ``update()`` does .

One can force replacement instead of update for an element by using
an instance of :class:`dict_dont_combine`, :class:`list_dont_combine`,
:class:`set_dont_combine`, or :class:`tuple_dont_combine`.

By including an instance of :class:`list_filtered`, one can selectively remove
existing elements.

    >>> from   _TFL.portable_repr import portable_repr

    >>> l1 = dict (foo = 1, bar = { 1 : "a", 2 : "b"}, qux = [2, 3])
    >>> r1 = dict (bar = { 2 : "baz", 3 : "c" }, qux = [5, 7])
    >>> portable_repr (l1)
    "{'bar' : {1 : 'a', 2 : 'b'}, 'foo' : 1, 'qux' : [2, 3]}"
    >>> portable_repr (r1)
    "{'bar' : {2 : 'baz', 3 : 'c'}, 'qux' : [5, 7]}"
    >>> portable_repr (update_combined (l1, r1))
    "{'bar' : {1 : 'a', 2 : 'baz', 3 : 'c'}, 'foo' : 1, 'qux' : [2, 3, 5, 7]}"

    >>> l2 = dict (bar = list_dont_combine ([1, 2, 3]), qux = [1, 2, 3])
    >>> r2 = dict (bar = [4, 5], qux = list_dont_combine ([4, 5]))
    >>> portable_repr (l2)
    "{'bar' : [1, 2, 3], 'qux' : [1, 2, 3]}"
    >>> portable_repr (r2)
    "{'bar' : [4, 5], 'qux' : [4, 5]}"
    >>> portable_repr (update_combined (l2, r2))
    "{'bar' : [1, 2, 3, 4, 5], 'qux' : [4, 5]}"

    >>> l3 = dict (bar = set ([1, 2, 3]), qux = set ([1, 2, 3]))
    >>> r3 = dict (bar = set ([4, 5]), qux = set_dont_combine ([4, 5]))
    >>> portable_repr (l3)
    "{'bar' : {1, 2, 3}, 'qux' : {1, 2, 3}}"
    >>> portable_repr (r3)
    "{'bar' : {4, 5}, 'qux' : {4, 5}}"
    >>> portable_repr (update_combined (l3, r3))
    "{'bar' : {1, 2, 3, 4, 5}, 'qux' : {4, 5}}"

    >>> l4 = list (range (10))
    >>> r4 = list_filtered (20, 30, 40, filter = lambda x : bool (x % 2))
    >>> portable_repr (l4)
    '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]'
    >>> portable_repr (r4)
    '[20, 30, 40]'
    >>> portable_repr (update_combined (l4, r4))
    '[1, 3, 5, 7, 9, 20, 30, 40]'

    >>> r5 = list_filtered (20, 30, 40, filter = lambda x : not (x % 2))
    >>> portable_repr (l4)
    '[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]'
    >>> portable_repr (r5)
    '[20, 30, 40]'
    >>> portable_repr (update_combined (l4, r5))
    '[0, 2, 4, 6, 8, 20, 30, 40]'

    >>> portable_repr (update_combined_many (l1))
    "{'bar' : {1 : 'a', 2 : 'b'}, 'foo' : 1, 'qux' : [2, 3]}"
    >>> portable_repr (update_combined_many (_undef, l1))
    "{'bar' : {1 : 'a', 2 : 'b'}, 'foo' : 1, 'qux' : [2, 3]}"
    >>> portable_repr (update_combined_many (l1, _undef))
    "{'bar' : {1 : 'a', 2 : 'b'}, 'foo' : 1, 'qux' : [2, 3]}"
    >>> portable_repr (update_combined_many (_undef, l1, _undef))
    "{'bar' : {1 : 'a', 2 : 'b'}, 'foo' : 1, 'qux' : [2, 3]}"
    >>> portable_repr (update_combined_many (_undef, l1, _undef, r1))
    "{'bar' : {1 : 'a', 2 : 'baz', 3 : 'c'}, 'foo' : 1, 'qux' : [2, 3, 5, 7]}"

    >>> portable_repr (update_combined_many ([(0, ), (1, )], [(2, ), (0, )]))
    '[(0,), (1,), (2,), (0,)]'

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.update_combined
