# -*- coding: utf-8 -*-
# Copyright (C) 2008-2020 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Filter
#
# Purpose
#    Classes for filtering
#
# Revision Dates
#    26-Jan-2008 (CT) Creation (started out as TOM.Entity_Dump_Filter)
#    27-Jan-2008 (CT) Creation continued
#    28-Jan-2008 (CT) Moved to TFL.Filter
#    28-Jan-2008 (CT) Creation continued..
#    13-Feb-2008 (CT) `filter_iter` added
#     6-May-2008 (CT) Use `all_true` and `any_true` instead of `all` and
#                     `any` to avoid errors from Python 2.4
#    17-Oct-2008 (CT) `* args, ** kw` added to filter functions
#     1-Dec-2009 (CT) `Attr_Query` and `Attr_Filter` added
#     1-Dec-2009 (MG) `Attr_Query.__mod__` added
#     2-Dec-2009 (CT) `_Filter_Q_.__init__` changed to not extract
#                     `predicate` of `Attr_Filter` instances
#     4-Dec-2009 (CT) `Attr_Query` based on `TFL.Q_Exp.Base` instead of
#                     home-grown code; `Attr_Filter` removed
#    19-Jan-2010 (CT) `Attr_Query.And` and `Attr_Query.Or` added
#    16-Jul-2011 (CT) `__repr__` added
#    22-Jul-2011 (CT) `Attr_Query.Func` added
#    12-Sep-2011 (CT) `Attr_Query.And` changed to `Attr_Query.AND`, ditto 4 `Or`
#    13-Sep-2011 (CT) All Q_Exp internal classes renamed to `_<<name>>_`
#    19-Dec-2011 (CT) Add shortcut `Attr_Query.NOT`
#    10-Aug-2012 (CT) Add `_rank` to allow defined order
#    22-Feb-2013 (CT) Define `Ignore_Exception` as `tuple`
#     8-Jul-2013 (CT) Add `op_name` to `Filter_Not`, `Filter_And`, `Filter_Or`
#    30-Aug-2013 (CT) Fix `Filter_Not.__repr__`
#    19-Sep-2013 (CT) Remove `Ignore_Exception` from `Attr_Query`
#    25-Sep-2013 (CT) Remove `LOWER`, `_Func_`
#    10-Oct-2013 (CT) Factor `_Filter_S_._add_derived_classes`
#     4-Apr-2014 (CT) Remove `Attr_Query` to `Q_Exp`
#     5-Feb-2015 (CT) Add Property `instance`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
This module provides some classes for filtering iterables::

    >>> def pprint (x) :
    ...     import textwrap
    ...     text = str (x)
    ...     sep  = chr (10) + "    "
    ...     print (sep.join (textwrap.wrap (text, 70)))
    ...
    >>> def is_even  (x) : return (x % 2) == 0
    ...
    >>> def div_7    (x) : return (x % 7) == 0
    ...
    >>> def is_prime (x) : return x in primes
    ...

    >>> primes                = [2, 3, 5, 7, 11, 13, 17, 19]
    >>> some_teens            = list (range (10, 20, 2))
    >>> fourties              = list (range (40, 50))
    >>> numbers               = primes + some_teens + fourties

    >>> Div_7                 = Filter     (div_7)
    >>> Is_Prime              = Filter     (is_prime)
    >>> Is_Even               = Filter     (is_even)
    >>> Is_Odd                = Filter_Not (Is_Even)
    >>> Is_Not_Odd            = Filter_Not (Is_Odd)
    >>> Div_7_and_Prime       = Filter_And (Div_7, Is_Prime)
    >>> Div_7_or_Prime        = Filter_Or  (Div_7, Is_Prime)
    >>> Div_7_not_Prime       = Filter_And (Div_7, ~ Is_Prime)
    >>> Div_7_not_Prime_Even  = Filter_And (Div_7_not_Prime, Is_Even)
    >>> Div_7_not_Prime_Odd   = Filter_And (Div_7_not_Prime, Is_Odd)
    >>> Is_Even_and_Prime     = Filter_And (Is_Even,  Is_Prime)

    >>> Div_7.filter (numbers)
    [7, 14, 42, 49]
    >>> Is_Prime.filter (numbers)
    [2, 3, 5, 7, 11, 13, 17, 19]
    >>> Is_Even.filter (numbers)
    [2, 10, 12, 14, 16, 18, 40, 42, 44, 46, 48]
    >>> Is_Odd.filter (numbers)
    [3, 5, 7, 11, 13, 17, 19, 41, 43, 45, 47, 49]
    >>> Is_Not_Odd.filter (numbers)
    [2, 10, 12, 14, 16, 18, 40, 42, 44, 46, 48]
    >>>
    >>> Div_7_and_Prime.filter (numbers)
    [7]
    >>> Div_7_or_Prime.filter (numbers)
    [2, 3, 5, 7, 11, 13, 17, 19, 14, 42, 49]
    >>> Div_7_not_Prime.filter (numbers)
    [14, 42, 49]
    >>> Div_7_not_Prime_Even.filter (numbers)
    [14, 42]
    >>> Div_7_not_Prime_Odd.filter (numbers)
    [49]
    >>> Is_Even_and_Prime.filter (numbers)
    [2]
    >>>
    >>> (~ Div_7).filter (numbers)
    [2, 3, 5, 11, 13, 17, 19, 10, 12, 16, 18, 40, 41, 43, 44, 45, 46, 47, 48]
    >>> (~ Is_Prime).filter (numbers)
    [10, 12, 14, 16, 18, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
    >>> (~ Is_Even).filter (numbers)
    [3, 5, 7, 11, 13, 17, 19, 41, 43, 45, 47, 49]
    >>> (~ Is_Odd).filter (numbers)
    [2, 10, 12, 14, 16, 18, 40, 42, 44, 46, 48]
    >>> (~ Is_Not_Odd).filter (numbers)
    [3, 5, 7, 11, 13, 17, 19, 41, 43, 45, 47, 49]
    >>>
    >>> pprint ((~ Div_7_and_Prime).filter (numbers))
    [2, 3, 5, 11, 13, 17, 19, 10, 12, 14, 16, 18, 40, 41, 42, 43, 44, 45,
        46, 47, 48, 49]
    >>> pprint ((~ Div_7_or_Prime).filter (numbers))
    [10, 12, 16, 18, 40, 41, 43, 44, 45, 46, 47, 48]
    >>> pprint ((~ Div_7_not_Prime).filter (numbers))
    [2, 3, 5, 7, 11, 13, 17, 19, 10, 12, 16, 18, 40, 41, 43, 44, 45, 46,
        47, 48]
    >>> pprint ((~ Div_7_not_Prime_Even).filter (numbers))
    [2, 3, 5, 7, 11, 13, 17, 19, 10, 12, 16, 18, 40, 41, 43, 44, 45, 46,
        47, 48, 49]
    >>> pprint ((~ Div_7_not_Prime_Odd).filter (numbers))
    [2, 3, 5, 7, 11, 13, 17, 19, 10, 12, 14, 16, 18, 40, 41, 42, 43, 44,
        45, 46, 47, 48]
    >>> pprint ((~ Is_Even_and_Prime).filter (numbers))
    [3, 5, 7, 11, 13, 17, 19, 10, 12, 14, 16, 18, 40, 41, 42, 43, 44, 45,
        46, 47, 48, 49]
    >>>
    >>> Is_Even.filter (numbers) == (~~Is_Even).filter (numbers)
    True

The filter operators `&` (logical and), `|` (logical or), and `~` (logical
not) are optimized to avoid intermediate level filter objects. The binary
operators short-circuit::

    >>> Is_Not_Odd is Is_Even
    True
    >>> Is_Even.predicate.__name__
    'is_even'
    >>> (~~Is_Even).predicate.__name__
    'is_even'
    >>> len ((Div_7_and_Prime & Div_7_and_Prime).predicates)
    4
    >>> len ((Div_7_or_Prime  | Div_7_or_Prime).predicates)
    4
    >>> len ((Div_7_and_Prime & Div_7_or_Prime).predicates)
    3
    >>> len ((Div_7_or_Prime  | Div_7_and_Prime).predicates)
    3
    >>> len ((Div_7_and_Prime | Div_7_and_Prime).predicates)
    2
    >>> len ((Div_7_or_Prime  & Div_7_or_Prime).predicates)
    2

    >>> for f in Div_7_and_Prime, Div_7_or_Prime :
    ...     for g in f, ~f, ~~f :
    ...         print (g.__class__.__name__, end = " ")
    ...     print ()
    ...
    Filter_And Filter_Or Filter_And
    Filter_Or Filter_And Filter_Or

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

from   _TFL                     import TFL

from   _TFL._Meta.Property      import Property
from   _TFL.predicate           import first, all_true, any_true

import _TFL._Meta.Object

import operator

class _Filter_ (TFL.Meta.Object) :
    """Base class for filters."""

    attrs = {}
    _rank = 0

    @Property
    def instance (self) :
        return self
    # end def instance

    def filter (self, iterable, * args, ** kw) :
        return list (self.filter_iter (iterable, * args, ** kw))
    # end def filter

    def filter_iter (self, iterable, * args, ** kw) :
        return (item for item in iterable if self (item, * args, ** kw))
    # end def filter_iter

    def __call__ (self, item, * args, ** kw) :
        return self.predicate (item, * args, ** kw)
    # end def __call__

    def __and__ (self, rhs) :
        return Filter_And (self, rhs)
    # end def __add__

    def __getattr__ (self, name) :
        try :
            return self.attrs [name]
        except KeyError :
            raise AttributeError (name)
    # end def __getattr__

    def __invert__ (self) :
        return Filter_Not (self.predicate, ** self.attrs)
    # end def __invert__

    def __or__ (self, rhs) :
        return Filter_Or (self, rhs)
    # end def __or__

# end class _Filter_

class _Filter_S_ (_Filter_) :
    """Base class for simple predicate filters."""

# end class _Filter_S_

class Filter (_Filter_S_) :
    """Return all items from an iterable which satisfy the predicate."""

    def __new__ (cls, predicate, ** kw) :
        if isinstance (predicate, Filter) :
            return predicate
        else :
            return cls.__c_super.__new__ (cls, predicate, ** kw)
    # end def __new__

    def __init__ (self, predicate, ** kw) :
        if self is not predicate :
            self.predicate = predicate
            self.attrs     = kw
    # end def __init__

    def __repr__ (self) :
        return "<%s %s>" % (self.__class__.__name__, self.predicate)
    # end def __repr__

# end class Filter

class Filter_Not (_Filter_S_) :
    """Return all items from an iterable which don't satisfy the predicate."""

    op_name = "not"

    def __new__ (cls, predicate, ** kw) :
        if isinstance (predicate, Filter_Not) :
            return ~ predicate
        else :
            return cls.__c_super.__new__ (cls, predicate, ** kw)
    # end def __new__

    def __init__ (self, predicate, ** kw) :
        self._not_predicate = predicate
        self.attrs          = kw
    # end def __init__

    def predicate (self, item, * args, ** kw) :
        return not self._not_predicate (item, * args, ** kw)
    # end def predicate

    def __invert__ (self) :
        return Filter (self._not_predicate, ** self.attrs)
    # end def __invert__

    def __repr__ (self) :
        return "<%s NOT %s>" % (self.__class__.__name__, self._not_predicate)
    # end def __repr__

# end class Filter_Not

class _Filter_Q_ (_Filter_) :
    """Base class for quantifying filters."""

    def __init__ (self, * pred_or_filters) :
        assert pred_or_filters
        self.predicates = preds = []
        add = preds.append
        ext = preds.extend
        for pof in pred_or_filters :
            if isinstance (pof, self.__class__) :
                ext (pof.predicates)
            elif getattr (pof, "predicate_precious_p", False) :
                add (pof)
            else :
                add (getattr (pof, "predicate", pof))
    # end def __init__

    def predicate (self, item, * args, ** kw) :
        return self.quant (p (item, * args, ** kw) for p in self.predicates)
    # end def predicate

    def _inverted_predicate (self) :
        return (Filter_Not (p) for p in self.predicates)
    # end def _inverted_predicate

    def __repr__ (self) :
        return "<%s %s>" % (self.__class__.__name__, self.predicates)
    # end def __repr__

# end class _Filter_Q_

class Filter_And (_Filter_Q_) :
    """Return all items from an iterable which satisfy all predicates."""

    op_name = "and"
    quant   = staticmethod (all_true)

    def __invert__ (self) :
        return Filter_Or (* self._inverted_predicate ())
    # end def __invert__

# end class Filter_And

class Filter_Or (_Filter_Q_) :
    """Return all items from an iterable which satisfy any of the predicates."""

    op_name = "or"
    quant   = staticmethod (any_true)

    def __invert__ (self) :
        return Filter_And (* self._inverted_predicate ())
    # end def __invert__

# end class Filter_Or

if __name__ != "__main__" :
    TFL._Export ("*", "_Filter_", "_Filter_Q_")
### __END__ TFL.Filter
