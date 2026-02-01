# -*- coding: utf-8 -*-
# Copyright (C) 2009-2020 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Q_Result
#
# Purpose
#    Provide filtering and ordering functions over query result
#
# Revision Dates
#     1-Dec-2009 (CT) Creation
#     2-Dec-2009 (CT) Creation continued
#     3-Dec-2009 (CT) Creation continued..
#     7-Dec-2009 (CT) Usage of `TFL.Attr_Filter` replaced by `TFL.Attr_Query`
#    19-Feb-2010 (MG) `first` fixed
#     1-Sep-2010 (CT) `attr`, `attrs`, and `set` added
#     2-Sep-2010 (CT) `set` changed to use `SET` of `Q.Get`
#     7-Sep-2010 (MG) `attr` and `attrs` return a `Q_Result` instance instead
#                     of being an iterator
#    26-Jul-2011 (CT) Handling of `distinct` changed so that it is passed on
#                     to derived queries
#    13-Sep-2011 (MG) `group_by` and `_Q_Result_Group_By_` added
#    16-Sep-2011 (MG) `_Attr_` and `_Attrs_Tuple_` added and used
#    16-Sep-2011 (MG) `_Attr_` missing  compare functions added
#    16-Sep-2011 (CT) `_Attr_.__eq__` and `.__lt__` robustified
#    16-Sep-2011 (MG) `_Q_Result_Group_By_._fill_cache` support for `SUM`
#                     added
#    15-Nov-2011 (CT) Change `_Attrs_Tuple_.__init__` to not pass `* args` to
#                     `__super` to avoid: `DeprecationWarning:
#                         object.__init__() takes no parameters`
#    30-Jan-2012 (CT) Add `_Attr_.__nonzero__`, `__int__`, `.__float__`;
#                     define all `_Attr_` comparison operators explicitly
#    12-Jun-2012 (MG) `Q_Result_Composite._fill_cache`: check for
#                     `self._order_by` fixed
#     8-Aug-2012 (CT) Fix typo (`.__class__.__name__`, not `.__class__.__name`)
#    14-Dec-2012 (CT) Move `order_by` before method in `super_ordered_delegate`
#    14-Dec-2012 (CT) Redefine `Q_Result_Composite.first` to delegate `first`
#    14-Dec-2012 (CT) Add guard for `._cache` to `_fill_cache`
#    21-Jan-2013 (MG) `Q_Result_Composite.first`: filter `None` result
#    27-Mar-2013 (CT) Factor `@_comparison_operator` from `_Attr_`;
#                     to allow mixed numeric comparisons, try normal
#                     comparison first
#     2-May-2013 (CT) Change `Q_Result_Composite.limit` to `@super_ordered`,
#                     not `@super_ordered_delegate` (gave wrong order sometimes)
#    30-Jul-2013 (CT) Remove `set`
#    25-Aug-2013 (CT) Allow strings as `criterion` for `order_by`
#    17-Sep-2013 (CT) Add `fixed_order_by` to support different `criteria`
#    17-Sep-2013 (CT) Change signature of `order_by` to allow multiple arguments
#     3-Oct-2013 (CT) Add `allow_duplicates` to `attr`, `attrs` (default False)
#     9-Oct-2013 (CT) Use `adapt__bool__` (3-compatibility)
#     4-Apr-2014 (CT) Use `TFL.Q`, not `TFL.Attr_Query ()`
#    16-Jul-2015 (CT) Use `expect_except` in doc-tests
#     7-Aug-2015 (CT) Add class and method docstrings to `_Q_Result_`,
#                     `Q_Result`, and `Q_Result_Composite`
#    15-Aug-2015 (CT) Add `_portable_repr_Attr_`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

"""
Provide filtering and ordering functions over query result::

    >>> qr = Q_Result ([x for x in range (10)])
    >>> qr.count ()
    10
    >>> qr [5]
    5
    >>> qr [5:9].all ()
    [5, 6, 7, 8]
    >>> qr.slice (3).all ()
    [3, 4, 5, 6, 7, 8, 9]
    >>> qr.slice (3, 5).all ()
    [3, 4]
    >>> qr.slice (3, 8).all ()
    [3, 4, 5, 6, 7]
    >>> qq = qr.order_by (lambda x : x % 2)
    >>> qq [4]
    8
    >>> qq.all ()
    [0, 2, 4, 6, 8, 1, 3, 5, 7, 9]
    >>> qq.filter (lambda x : x % 2).all ()
    [1, 3, 5, 7, 9]
    >>> qq.distinct (lambda x : x % 2).all ()
    [0, 1]
    >>> qq.all ()
    [0, 2, 4, 6, 8, 1, 3, 5, 7, 9]
    >>> qq.distinct (lambda x : x % 3 == 0).all ()
    [0, 2]
    >>> qs = qr.filter (lambda x : x % 2 == 0)
    >>> qs.count ()
    5
    >>> qs.all ()
    [0, 2, 4, 6, 8]
    >>> qt = qs.filter (lambda x : x % 3 == 0)
    >>> qt.count ()
    2
    >>> qt.all ()
    [0, 6]
    >>> qt.first ()
    0
    >>> with expect_except (IndexError) :
    ...     qt.one ()
    IndexError: Query result contains 2 entries
    >>> qu = qt.limit (1)
    >>> qu.all ()
    [0]
    >>> qu.one ()
    0
    >>> qv = qt.offset (1)
    >>> qv.all ()
    [6]
    >>> qv.one ()
    6

    >>> qr = Q_Result (list (range (1, 100, 10)))
    >>> qs = Q_Result (list (range (10, 200, 20)))
    >>> qt = Q_Result (list (x*x for x in range (10)))
    >>> qc = Q_Result_Composite ((qr, qs, qt))
    >>> qr.count ()
    10
    >>> qs.count ()
    10
    >>> qt.count ()
    10
    >>> qc.count ()
    30
    >>> qc.all ()
    [1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 10, 30, 50, 70, 90, 110, 130, 150, 170, 190, 0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> qc.distinct ().count ()
    28
    >>> qc.distinct ().all ()
    [1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 10, 30, 50, 70, 90, 110, 130, 150, 170, 190, 0, 4, 9, 16, 25, 36, 49, 64]
    >>> qc.distinct ().order_by (lambda x : x % 10).all ()
    [10, 30, 50, 70, 90, 110, 130, 150, 170, 190, 0, 1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 4, 64, 25, 16, 36, 9, 49]
    >>> qc.distinct (lambda x : x % 10).all ()
    [1, 10, 4, 9, 16, 25]
    >>> qc.distinct (lambda x : x % 10).count ()
    6
    >>> qc [5:15].all ()
    [51, 61, 71, 81, 91, 10, 30, 50, 70, 90]
    >>> qc.limit (5).all ()
    [1, 11, 21, 31, 41]
    >>> qc.distinct (lambda x : x % 10).limit (3).all ()
    [1, 10, 4]
    >>> qc.limit (15).distinct (lambda x : x % 10).all ()
    [1, 10]

    >>> qg = Q_Result ((1, 2, 3, 4, 2, 3, 4, 4,5))
    >>> qg.all        ()
    [1, 2, 3, 4, 2, 3, 4, 4, 5]
    >>> qg.group_by (lambda x : x).all ()
    [1, 2, 3, 4, 5]

.. autoclass:: _Q_Result_
 :members:

"""

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

import _TFL._Meta.Object
import _TFL.Decorator
import _TFL.Q_Exp
import _TFL.Sorted_By

from   _TFL._Meta.Single_Dispatch import Single_Dispatch
from   _TFL.portable_repr         import portable_repr
from   _TFL.predicate             import first, uniq, uniq_p

import itertools
import operator

def _comparison_operator (op) :
    name    = op.__name__
    op      = getattr (operator, name)
    def _ (self, rhs) :
        if isinstance (rhs, _Attr_) :
            rhs = rhs._VALUE
        lhs = self._VALUE
        try :
            return op (lhs, rhs)
        except TypeError :
            ### Some combinations, like `lhs == None` or
            ### `type (rhs) == datetime.date`, raise a TypeError
            ### Compare `(x.__class__.__name__, x)` in this case
            return op \
                ((lhs.__class__.__name__, lhs), (rhs.__class__.__name__, rhs))
    _.__doc__    = op.__doc__
    _.__name__   = name
    _.__module__ = op.__module__
    return _
# end def _comparison_operator

class _Attr_ (object) :
    """Wrapper for result of `.attr` method."""

    def __init__ (self, getter, value) :
        self._VALUE  = value
        p            = getter._name.split (".", 1)
        self._NAME   = p.pop              (0)
        self._REST   = p and p.pop        (0)
        self._IS_SUM = getter if isinstance (getter, TFL.Q._Sum_) else None
    # end def __init__

    @_comparison_operator
    def __eq__ (self, rhs) : pass

    def __float__ (self) :
        return float (self._VALUE)
    # end def __float__

    def __getattr__ (self, name) :
        if name == self._NAME :
            if not self._REST :
                return self._VALUE
            return _Attr_ (getattr (Q_Result.Q, self._REST), self._VALUE)
        raise AttributeError (name)
    # end def __getattr__

    @_comparison_operator
    def __ge__ (self, rhs) : pass

    @_comparison_operator
    def __gt__ (self, rhs) : pass

    def __hash__ (self) :
        lhs = self._VALUE
        return hash ((lhs.__class__.__name__, lhs))
    # end def __hash__

    def __int__ (self) :
        return int (self._VALUE)
    # end def __int__

    @_comparison_operator
    def __le__ (self, rhs) : pass

    @_comparison_operator
    def __lt__ (self, rhs) : pass

    @_comparison_operator
    def __ne__ (self, rhs) : pass

    def __bool__ (self) :
        return bool (self._VALUE)
    # end def __bool__

    def __repr__ (self) :
        return repr (self._VALUE)
    # end def __repr__

    def __str__ (self) :
        return str (self._VALUE)
    # end def __str__

# end class _Attr_

@portable_repr.add_type (_Attr_)
def _portable_repr_Attr_ (obj, seen) :
    return portable_repr (obj._VALUE)
# end def _portable_repr_Attr_

class _Attrs_Tuple_ (tuple) :
    """Wrapper for result of `.attrs` method."""

    _IS_SUM = None

    def __new__ (cls, getters, * args) :
        return super (_Attrs_Tuple_, cls).__new__ (cls, * args)
    # end def __new__

    def __init__ (self, getters, * args) :
        super (_Attrs_Tuple_, self).__init__ ()
        self._NAMES          = {}
        for i, g in enumerate (getters) :
            p                = g._name.split (".", 1)
            k                = p.pop         (0)
            self._NAMES [k]  = i, p and p.pop (0)
            if isinstance (g, TFL.Q._Sum_) :
                self._IS_SUM = g
                self._SUM_CO = i
    # end def __init__

    def __getattr__ (self, name) :
        idx, rest = self._NAMES.get (name, (-1, None))
        if rest is not None :
            result = self [idx]
            if rest :
                result = _Attr_ (getattr (Q_Result.Q, rest), result)
            return result
        raise AttributeError (name)
    # end def __getattr__

# end class _Attrs_Tuple_

class _Sum_Aggr_ (dict) :

    def __setitem__ (self, key, value) :
        if key in self :
            value += self [key]
        super (_Sum_Aggr_, self).__setitem__ (key, value)
    # end def __setitem__

# end class _Sum_Aggr_

class _Q_Filter_Distinct_ (TFL.Meta.Object) :

    def __init__ (self, criterion) :
        self.criterion = criterion
    # end def __init__

    def __call__ (self, iterable) :
        return uniq_p (iterable, self.criterion)
    # end def __call__

# end class _Q_Filter_Distinct_

class _Q_Result_ (TFL.Meta.Object) :
    """Base class for :class:`Q_Result` and :class:`Q_Result_Composite`."""

    Q             = TFL.Q

    _Attr_        = _Attr_
    _Attrs_Tuple_ = _Attrs_Tuple_

    def __init__ (self, iterable, _distinct = False) :
        self.iterable  = iterable
        self._cache    = None
        self._distinct = _distinct
    # end def __init__

    def all (self) :
        """Return all elements of query result as a list"""
        return list (self)
    # end def all

    def attr (self, getter, allow_duplicates = False) :
        """Restrict query result to the attribute specified by `getter`."""
        _Attr_ = self._Attr_
        if isinstance (getter, pyk.string_types) :
            getter = getattr (self.Q, getter)
        distinct = self._distinct or not allow_duplicates
        if distinct and isinstance (distinct, bool) :
            distinct = uniq
        return Q_Result ((_Attr_ (getter, getter (r)) for r in self), distinct)
    # end def attr

    def attrs (self, * getters, ** kw) :
        """Restrict query result to the attributes specified by `getters`."""
        allow_duplicates = kw.pop ("allow_duplicates", False)
        if kw :
            raise TypeError ("Unknown keyword arguments %s" % sorted (kw))
        _Attrs_Tuple_    = self._Attrs_Tuple_
        if not getters :
            raise TypeError \
                ( "%s.attrs() requires at least one argument"
                % self.__class__.__name__
                )
        def _g (getters) :
            Q = self.Q
            for getter in getters :
                if isinstance (getter, pyk.string_types) :
                    getter = getattr (Q, getter)
                yield getter
        getters  = tuple (_g (getters))
        distinct = self._distinct or not allow_duplicates
        if distinct and isinstance (distinct, bool) :
            distinct = uniq
        return Q_Result \
            ( (_Attrs_Tuple_ (getters, (g (r) for g in getters)) for r in self)
            , distinct
            )
    # end def attrs

    def count (self) :
        """Return number of elements in query result."""
        if self._cache is None :
            self._fill_cache ()
        return len (self._cache)
    # end def count

    def distinct (self, * criteria) :
        """Restrict query result to distinct elements."""
        n = len (criteria)
        if n == 0 :
            _distinct = uniq
        else :
            if n == 1 :
                criterion = first (criteria)
            elif criteria :
                criterion = TFL.Filter_And  (* criteria)
            _distinct = _Q_Filter_Distinct_ (criterion)
        return _Q_Result_ (self, _distinct = _distinct)
    # end def distinct

    def filter (self, * criteria, ** kw) :
        """Restrict query result to elements matching the `criteria`."""
        if kw :
            criteria = list (criteria)
            Q = self.Q
            for k, v in pyk.iteritems (kw) :
                criteria.append (getattr (Q, k) == v)
            criteria = tuple (criteria)
        assert criteria
        if len (criteria) == 1 :
            criterion = first (criteria)
        else :
            criterion = TFL.Filter_And  (* criteria)
        return self._Q_Result_Filtered_ (self, criterion, self._distinct)
    # end def filter

    def first (self) :
        """Return first element of query result."""
        try :
            return first (self)
        except IndexError :
            return None
    # end def first

    def group_by (self, * criteria, ** kw) :
        """Group query result by `criteria`."""
        if kw :
            criteria = list (criteria)
            Q = self.Q
            for k, v in pyk.iteritems (kw) :
                criteria.append (getattr (Q, k) == v)
            criteria = tuple (criteria)
        assert criteria
        if len (criteria) == 1 :
            criterion = first (criteria)
        else :
            criterion = TFL.Filter_And  (* criteria)
        return self._Q_Result_Group_By_ (self, criterion, self._distinct)
    # end def group_by

    def limit (self, limit) :
        """Limit query result to `limit` elements."""
        return self._Q_Result_Limited_ (self, limit, self._distinct)
    # end def limit

    def offset (self, offset) :
        """Discard elements of query result with index < `offset`."""
        return self._Q_Result_Offset_ (self, offset, self._distinct)
    # end def offset

    def one (self) :
        """Return first and only element of query result. Raise IndexError if
           query result contains more than one element.
        """
        result = first (self)
        if len (self._cache) > 1 :
            raise IndexError \
                ("Query result contains %s entries" % len (self._cache))
        return result
    # end def one

    def order_by (self, * criteria) :
        """Order elements of query result by `criteria`."""
        return self._Q_Result_Ordered_ (self, criteria, self._distinct)
    # end def order_by

    def slice (self, start, stop = None) :
        """Restrict elements of query result to slice `start:stop`"""
        return self._Q_Result_Sliced_ (self, start, stop, self._distinct)
    # end def slice

    def _fill_cache (self) :
        if self._cache is None :
            iterable = self.iterable
            distinct = self._distinct
            if distinct :
                iterable = distinct (iterable)
            self._cache  = list (iterable)
    # end def _fill_cache

    def __bool__ (self) :
        if self._cache is None :
            self._fill_cache ()
        return bool (self._cache)
    # end def __bool__

    def __getitem__ (self, key) :
        if isinstance (key, slice) :
            return self.slice (key.start, key.stop)
        if self._cache is None :
            self._fill_cache ()
        return self._cache [key]
    # end def __getitem__

    def __getslice__ (self, start, stop) :
        return self.slice (start, stop)
    # end def __getslice__

    def __iter__ (self) :
        if self._cache is None :
            self._fill_cache ()
        return iter (self._cache)
    # end def __iter__

# end class _Q_Result_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Filtered_ (_Q_Result_) :

    def __init__ (self, iterable, criterion, _distinct = False) :
        self.__super.__init__ (iterable, _distinct = _distinct)
        self._criterion = criterion
    # end def __init__

    def _fill_cache (self) :
        if self._cache is None :
            pred     = self._criterion
            filtered = (x for x in self.iterable if pred (x))
            if self._distinct and not self.iterable._distinct :
                filtered = self._distinct (filtered)
            self._cache = list (filtered)
    # end def _fill_cache

# end class _Q_Result_Filtered_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Group_By_ (_Q_Result_Filtered_) :

    def _fill_cache (self) :
        if self._cache is None :
            pred        = self._criterion
            result      = dict        ()
            sums        = _Sum_Aggr_  ()
            sum_col     = None
            for row in self.iterable :
                key    = pred (row)
                is_sum = getattr (row, "_IS_SUM", None)
                if is_sum is not None :
                    sums [key] = is_sum (row)
                    sum_col    = getattr (row, "_SUM_CO", None)
                result [key]   = row
            if sums :
                sum_fixed      = []
                for key, row in pyk.iteritems (result) :
                    if sum_col is None :
                        sum_fixed.append (sums [key])
                    else :
                        sum_fixed.append \
                            ( row [:sum_col]
                            + (sums [key], )
                            + row [sum_col + 1:]
                            )
                result         = sum_fixed
            else :
                result         = pyk.itervalues (result)
            if self._distinct and not self.iterable._distinct :
                result  = self._distinct (result)
            self._cache = list (result)
    # end def _fill_cache

# end class _Q_Result_Group_By_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Limited_ (_Q_Result_) :

    def __init__ (self, iterable, limit, _distinct = False) :
        self.__super.__init__ (iterable, _distinct = _distinct)
        self._limit = limit
    # end def __init__

    def _fill_cache (self) :
        if self._cache is None :
            iterable = self.iterable
            if self._distinct and not iterable._distinct :
                iterable = self._distinct (iterable)
            self._cache = list (itertools.islice (iterable, 0, self._limit, 1))
    # end def _fill_cache

# end class _Q_Result_Limited_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Offset_ (_Q_Result_) :

    def __init__ (self, iterable, offset, _distinct = False) :
        self.__super.__init__ (iterable, _distinct = _distinct)
        self._offset = offset
    # end def __init__

    def _fill_cache (self) :
        if self._cache is None :
            iterable = self.iterable
            if self._distinct and not iterable._distinct :
                iterable = self._distinct (iterable)
            self._cache = list \
                (itertools.islice (iterable, self._offset, None, 1))
    # end def _fill_cache

# end class _Q_Result_Offset_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Ordered_ (_Q_Result_) :

    def __init__ (self, iterable, criterion, _distinct = False) :
        self.__super.__init__ (iterable, _distinct = _distinct)
        self._criterion = fixed_order_by (criterion)
    # end def __init__

    def _fill_cache (self) :
        if self._cache is None :
            iterable = self.iterable
            if self._distinct and not iterable._distinct :
                iterable = self._distinct (iterable)
            self._cache = sorted (iterable, key = self._criterion)
    # end def _fill_cache

# end class _Q_Result_Ordered_

@TFL.Add_New_Method (_Q_Result_)
class _Q_Result_Sliced_ (_Q_Result_) :

    def __init__ (self, iterable, start, stop, _distinct = False) :
        self.__super.__init__ (iterable, _distinct = _distinct)
        self._start = start
        self._stop  = stop
    # end def __init__

    def _fill_cache (self) :
        if self._cache is None :
            iterable = self.iterable
            if self._distinct and not iterable._distinct :
                iterable = self._distinct (iterable)
            self._cache = list \
                (itertools.islice (iterable, self._start, self._stop))
    # end def _fill_cache

# end class _Q_Result_Sliced_

class Q_Result (_Q_Result_) :
    """Lazy query result. The elements of the query result are only
       materialized when `all`, `count`, `first`, or `iter` or called.
    """

    def __init__ (self, iterable, _distinct = False) :
        self.iterable  = iterable
        self._distinct = _distinct
        try :
            len (iterable)
        except TypeError :
            self._cache = None
        else :
            if _distinct and not getattr (iterable, "_distinct", False) :
                iterable = list (_distinct (iterable))
            self._cache = iterable
    # end def __init__

# end class Q_Result

class Q_Result_Composite (_Q_Result_) :
    """Lazy query result for composite query. The elements of the composite
       query result are only materialized when `all`, `count`, `first`, or
       `iter` or called.
    """

    @TFL.Decorator
    def super_ordered (q) :
        def _ (self, * args, ** kw) :
            name = q.__name__
            result = getattr (self.__super, name) (* args, ** kw)
            if self._order_by :
                result = result.order_by (self._order_by)
            return result
        return _
    # end def super_ordered

    @TFL.Decorator
    def super_ordered_delegate (q) :
        def _ (self, * args, ** kw) :
            name    = q.__name__
            oby     = self._order_by
            queries = self.queries
            result  = self.__class__ \
                ( [getattr (sq, name) (* args, ** kw) for sq in queries]
                , _distinct = self._distinct
                )
            if oby :
                result = result.order_by (oby)
            result = getattr (result.__super, name) (* args, ** kw)
            return result
        return _
    # end def super_ordered_delegate

    def __init__ (self, queries, order_by = None, _distinct = False) :
        self.queries   = queries
        self._order_by = order_by
        self.__super.__init__ \
            (itertools.chain (* queries), _distinct = _distinct)
    # end def __init__

    @super_ordered_delegate
    def distinct (self, * criteria) :
        pass
    # end def distinct

    def filter (self, * criteria, ** kw) :
        return self.__class__ \
            ( [q.filter (* criteria, ** kw) for q in self.queries]
            , self._order_by, self._distinct
            )
    # end def filter

    def first (self) :
        result = self.__class__ \
            ( [(sq.first (), ) for sq in self.queries]
            , _distinct = self._distinct
            )
        if self._order_by :
            result = result.order_by (self._order_by)
        ### filter None result from the sub queries
        for obj in result :
            if obj is not None :
                return obj
    # end def first

    @super_ordered
    def limit (self, limit) :
        pass
    # end def limit

    @super_ordered
    def offset (self, offset) :
        pass
    # end def offset

    def order_by (self, * criteria) :
        return self.__class__ ([self], fixed_order_by (criteria))
    # end def order_by

    @super_ordered
    def slice (self, start, stop = None) :
        pass
    # end def slice

    def _fill_cache (self) :
        if self._cache is None :
            if self._order_by is not None :
                iterable = self.iterable
                if self._distinct :
                    iterable = self._distinct (iterable)
                self._cache = sorted (iterable, key = self._order_by)
            else :
                self.__super._fill_cache ()
    # end def _fill_cache

    def __bool__ (self) :
        return any (self.queries)
    # end def __bool__

# end class Q_Result_Composite

@Single_Dispatch
def fixed_order_by (x) :
    if hasattr (x, "__call__") :
        return x
    else :
        raise ValueError ("Cannot order by %s %r" % (x.__class__.__name__, x))
# end def fixed_order_by

@fixed_order_by.add_type (TFL.Sorted_By, TFL.Q_Exp.Base)
def _fixed_order_by_sorted_by_ (x) :
    return x
# end def _fixed_order_by_sorted_by_

@fixed_order_by.add_type (* pyk.string_types)
def _fixed_order_by_str_ (x) :
    return TFL.Sorted_By (x)
# end def _fixed_order_by_str_

@fixed_order_by.add_type (tuple)
def _fixed_order_by_tuple (xs) :
    if len (xs) == 1 :
        return fixed_order_by (xs [0])
    else :
        return TFL.Sorted_By (* tuple (fixed_order_by (x) for x in xs))
# end def _fixed_order_by_tuple

if __name__ != "__main__" :
    TFL._Export ("*", "_Q_Result_")
### __END__ TFL.Q_Result
