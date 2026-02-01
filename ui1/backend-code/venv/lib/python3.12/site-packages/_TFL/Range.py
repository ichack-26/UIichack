# -*- coding: utf-8 -*-
# Copyright (C) 2016-2022 Christian Tanzer All rights reserved
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
#    TFL.Range
#
# Purpose
#    Represent a range of values of some element type
#
# Revision Dates
#    23-Jun-2016 (CT) Creation
#     4-Jul-2016 (CT) Finish creation
#     6-Jul-2016 (CT) Add `contains`
#     6-Jul-2016 (CT) Add import callback for `TFL.json_dump`
#    25-Jul-2016 (CT) Add `contains_rop`
#    26-Jul-2016 (CT) Add `attr_tuple`, `btype_lower`, `btype_upper`
#     9-Sep-2016 (CT) Add `FO`
#    14-Sep-2016 (CT) Add `ui_display`
#    20-Sep-2016 (CT) Factor `bound_from_string`
#    27-Feb-2017 (CT) Make `_test_json` Python 3.6 compatible
#                     * Adapt to change of format of `TypeError`
#                       raised by `json.dump`
#     1-Mar-2017 (CT) Add `Float_Range_Discrete`
#     9-Mar-2017 (CT) Add `epsilon` to `_Range_Discrete_.__iter__`
#                     and `Float_Range_Discrete`
#     4-Apr-2017 (CT) Add guard for `eps` and `last` to `__iter__`
#    19-Aug-2019 (CT) Use `print_prepr`
#    12-Oct-2022 (CT) Fix doctests broken by Python-3.10
#    26-Oct-2022 (CT) Fix doctests broken by Python-3.11
#                     * Unfortunately, nothing of the AttributeError's message
#                       is left anymore
#    ««revision-date»»···
#--

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _TFL._Meta.totally_ordered import totally_ordered
from   _TFL.portable_repr         import portable_repr, print_prepr
from   _TFL.Regexp                import Regexp

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.FO
import _TFL.Infinity

import operator

class _M_Base_ (TFL.Meta.Object.__class__) :
    """Meta base class for bounds and range classes"""

    __rank = 0

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls._sort_key    = _M_Base_.__rank
        _M_Base_.__rank += 1
    # end def __init__

# end class _M_Base_

class _Range_ (TFL.Meta.Object, metaclass = _M_Base_) :
    """Base class for type-specific range classes."""

    S_Type               = None
    default_btype        = "[)"
    """Default for :attr:`btype`: unless redefined by a descendent class,
    the default :attr:`lower` bound is inclusive and the default
    :attr:`upper` bound exclusive, i.e., "[)".
    """

    finite               = {}
    """Descendent classes can override `finite` to set a minimum value
    for :attr:`lower` and a maximum value for :attr:`upper`.
    """

    range_pattern        = Regexp\
        ( r" *"
          r"(?P<LB>\[|\()?"
          r" *"
          r"(?P<lower>[^,]*)"
          r", *"
          r"(?P<upper>[^])]*)"
          r"(?P<UB>\]|\))?"
          r" *"
          r"$"
        )

    class _Range_FO_ (TFL.FO) :
        """Formatter for range objects and their bounds."""

        def _attr_as_str (self, obj, name, value) :
            return obj._sub_type_as_str (value)
        # end def _attr_as_str

    # end class _Range_FO_

    FO = property (_Range_FO_)

    def __init__ (self, lower = None, upper = None, btype = None) :
        """Create a new range with bounds `lower` and `upper`.

           `btype` specifies whether the `lower` and `upper` bounds
           are inclusive or exclusive. The possible values are:
           "[]", "[)", "(]", "()"; by default, the `lower` bound is
           inclusive and the `upper` bound exclusive, i.e., "[)".
        """
        if self.S_Type is None :
            raise TypeError \
                ( "Cannot instantiate %s, doesn't define a sub-type"
                % self.__class__.__name__
                )
        self.__lower  = lower
        self.__upper  = upper
        self.__btype  = self.default_btype if btype is None else btype
    # end def __init__

    @classmethod
    def args_from_string (cls, s) :
        """Extract init-arguments from string representation of range."""
        pat    = cls.range_pattern
        result = ()
        if pat.match (s) :
            if bool (pat.LB) != bool (pat.UB) :
                raise ValueError ("Need both bounds or none")
            btype  = pat.LB + pat.UB if pat.LB and pat.UB else None
            lower  = cls.bound_from_string (pat.lower.strip ())
            upper  = cls.bound_from_string (pat.upper.strip ())
            result = (lower, upper, btype)
        return result
    # end def args_from_string

    @classmethod
    def bound_from_string (cls, s) :
        """Convert `s` to boundary value"""
        return None if s in ("None", "") else cls._sub_type_from_str (s)
    # end def bound_from_string

    @classmethod
    def from_string (cls, s) :
        """Convert string representation of range to instance of `cls`."""
        args = cls.args_from_string (s)
        if args :
            return cls (* args)
    # end def from_string

    @TFL.Meta.Once_Property
    def LB (self) :
        """Lower bound :class:`handler<_Lower_Bounds_>`."""
        return _Bounds_ [self.btype_lower] (self)
    # end def LB

    @TFL.Meta.Once_Property
    def UB (self) :
        """Upper bound :class:`handler<_Upper_Bounds_>`."""
        return _Bounds_ [self.btype_upper] (self)
    # end def UB

    @property
    def btype (self) :
        """Bound type representation: one of [], [), (], ()."""
        return self.__btype
    # end def btype

    @property
    def btype_lower (self) :
        """Lower bound type representation: one of [, (."""
        return self.__btype [0]
    # end def btype_lower

    @property
    def btype_upper (self) :
        """Upper bound type representation: one of ), ]."""
        return self.__btype [1]
    # end def btype_upper

    @TFL.Meta.Once_Property
    def exclusive (self) :
        """True if any of the bounds is exclusive."""
        return self.LB.exclusive or self.UB.exclusive
    # end def exclusive

    @TFL.Meta.Once_Property
    def is_empty (self) :
        """True if range doesn't contain any values."""
        l      = self.LB.first
        u      = self.UB.first
        x      = self.exclusive_continuous
        result = not (l is None or u is None) and (l >= u if x else l > u)
        return result
    # end def is_empty

    @property
    def lower (self) :
        """Value of lower bound."""
        return self.__lower
    # end def lower

    @property
    def upper (self) :
        """Value of upper bound."""
        return self.__upper
    # end def upper

    def attr_tuple (self) :
        return (self.lower, self.upper)
    # end def attr_tuple

    def contains (self, other) :
        """Return True if `self` contains value or range `other`."""
        return other in self
    # end def contains

    def intersection (self, other) :
        """Return overlapping range between `self` and `other`."""
        return self & other
    # end def intersection

    def overlaps (self, other) :
        """True if `self` and `other` overlap, i.e., have values in common."""
        if bool (self) and bool (other) :
            b1, b2, b3, b4 = self.sorted_bounds (other)
            return self.bounds_overlap (b1, b2, b3, b4)
        else :
            return False
    # end def overlaps

    def sorted_bounds (self, other) :
        """Return sorted bounds of `self` and `other`."""
        ### Ensure that for adjacent ranges, r.UB sorts before l.LB
        l, r = (self, other) if self.LB <= other.LB else (other, self)
        return sorted ([l.UB, r.UB, l.LB, r.LB])
    # end def sorted_bounds

    def union (self, other) :
        """Return union range between `self` and `other`."""
        return self | other
    # end def union

    def _sub_type_add (self, v, delta) :
        return v + delta
    # end def _sub_type_add

    def _sub_type_as_repr (self, v) :
        return "%r" % (v, )
    # end def _sub_type_as_repr

    def _sub_type_as_str (self, v) :
        return "%s" % (v, )
    # end def _sub_type_as_str

    @classmethod
    def _sub_type_from_str (cls, s) :
        return cls.S_Type (s)
    # end def _sub_type_from_str

    def _sub_type_sub (self, v, delta) :
        return v - delta
    # end def _sub_type_sub

    def __add__ (self, delta) :
        shift = self._sub_type_add
        return self.__class__ \
            ( shift (self.lower, delta)
            , shift (self.upper, delta)
            , self.btype
            )
    # end def __add__

    def __and__ (self, rhs) :
        """Return overlapping range between `self` and `other`."""
        b1, b2, b3, b4 = self.sorted_bounds (rhs)
        if self.overlaps (rhs) :
            args = (b2.first, b3.first, "[]")
        else :
            args = (b2.bound, b3.bound, "()")
        return self.__class__ (* args)
    # end def __and__

    def __bool__ (self) :
        return not self.is_empty
    # end def __bool__

    def __contains__ (self, item) :
        if isinstance (item, _Range_) :
            raise TypeError \
                ( "%r must redefine `__contains__` to deal with "
                  "`_Range_` instances %r; or wrong type was passed in!"
                % (self, item)
                )
        else :
            l, u = self.LB,  self.UB
            return l.contains (item) and u.contains (item)
    # end def __contains__

    def __eq__ (self, other) :
        if isinstance (other, _Range_) :
            return \
                (   self.LB.cmp_value == other.LB.cmp_value
                and self.UB.cmp_value == other.UB.cmp_value
                )
        else :
            return (self.LB.first, self.UB.first) == other
    # end def __eq__

    def __hash__ (self) :
        return hash ((self.LB.cmp_value, self.UB.cmp_value))
    # end def __hash__

    def __lt__ (self, other) :
        l, u = self.LB.first, self.UB.first
        if isinstance (other, _Range_) :
            raise TypeError \
                ( "%r must redefine `__lt__` to deal with "
                  "`_Range_` instances %r; or wrong type was passed in!"
                % (self, other)
                )
        else :
            return (l, u) < other
    # end def __lt__

    def __ne__ (self, rhs) :
        return not (self == rhs)
    # end def __ne__

    def __or__ (self, rhs) :
        """Return union range between `self` and `other`, if they overlap."""
        b1, b2, b3, b4 = self.sorted_bounds (rhs)
        if self.overlaps (rhs) :
            args = (b1.bound, b4.bound, b1.btype + b4.btype)
        else :
            args = (b2.bound, b3.bound, "()")
        return self.__class__ (* args)
    # end def __or__

    def __radd__ (self, rhs) :
        return self + rhs
    # end def __radd__

    def __repr__ (self) :
        btype  = portable_repr (self.btype)
        cname  = self.__class__.__name__
        star   = self._sub_type_as_repr
        result = "%s (%s, %s, %s)" % \
            (cname, star (self.lower), star (self.upper), btype)
        return pyk.reprify (result)
    # end def __repr__

    def __str__ (self) :
        lbt, rbt = self.btype
        stas     = self._sub_type_as_str
        return "%s%s, %s%s" % (lbt, stas (self.lower), stas (self.upper), rbt)
    # end def __str__

    def __sub__ (self, delta) :
        shift = self._sub_type_sub
        return self.__class__ \
            ( shift (self.lower, delta)
            , shift (self.upper, delta)
            , self.btype
            )
    # end def __sub__

# end class _Range_

@totally_ordered
class _Range_Continuous_ (_Range_) :
    """Base class for type-specific continuous range classes."""

    delta = None

    @TFL.Meta.Once_Property
    def exclusive_continuous (self) :
        return self.exclusive
    # end def exclusive_continuous

    def after (self, other) :
        """Return true if `self` is after `other`."""
        l, ou = self.LB, other.UB
        oper  = operator.ge if l.exclusive and ou.exclusive else operator.gt
        return bool (self) and bool (other) and oper (l.cmp_value, ou.cmp_value)
    # end def after

    def before (self, other) :
        """Return true of `self` is before `other`."""
        u, ol = self.UB, other.LB
        oper  = operator.le if u.exclusive and ol.exclusive else operator.lt
        return bool (self) and bool (other) and oper (u.cmp_value, ol.cmp_value)
    # end def before

    def bounds_overlap (self, b1, b2, b3, b4) :
        """True if the bounds `b1`, `b2`, `b3`, `b4` overlap.

           `b1`, `b2`, `b3`, `b4` must be sorted.
        """
        if b1.range is not b2.range :
            ### guard for special case: `b2 == "x)"`, `b3 == "[x"`
            return True if not b2.exclusive else b2.bound < b3.bound
        else :
            return \
                (   not (b2.exclusive or b3.exclusive)
                and b2.cmp_value == b3.cmp_value
                )
    # end def bounds_overlap

    def is_adjacent (self, other) :
        """Return true if `self` and `other` are adjacent."""
        l, r   = (self, other) if self <= other else (other, self)
        lb, rb = l.UB, r.LB
        return \
            (   bool (l)
            and bool (r)
            and (lb.exclusive or rb.exclusive)
            and lb.bound == rb.bound
            )
    # end def is_adjacent

    def __contains__ (self, item) :
        """True if `self` contains `item`.

           `item` can be an instance of `self.S_Type` or a range.
        """
        if isinstance (item, _Range_Continuous_) :
            lb, ub = self.LB,  self.UB
            i_lower, i_upper = item.lower, item.upper
            return \
                (   bool (item)
                and (  lb.cmp_value == item.LB.cmp_value
                    or lb.contains (i_lower)
                    )
                and (  ub.cmp_value == item.UB.cmp_value
                    or ub.contains (i_upper)
                    )
                and lb.contains (i_upper)
                and ub.contains (i_lower)
                )
        elif isinstance (item, _Range_Discrete_) :
            raise TypeError ("Cannot mix %r and %r" % (self, item))
        else :
            return self.__super.__contains__ (item)
    # end def __contains__

    __eq__ = _Range_.__eq__ ### `totally_ordered` looks in class __dict__

    def __ge__ (self, other) :
        l,  u  = self.LB,  self.UB
        if isinstance (other, _Range_Continuous_) :
            ol, ou = other.LB, other.UB
            return l.cmp_value >= ol.cmp_value and u.cmp_value >= ou.cmp_value
        elif isinstance (other, _Range_Discrete_) :
            raise TypeError ("Cannot mix %r and %r" % (self, other))
        else :
            return (l.first, u.first) >= other
    # end def __ge__

    def __le__ (self, other) :
        l,  u  = self.LB,  self.UB
        if isinstance (other, _Range_Continuous_) :
            ol, ou = other.LB, other.UB
            return l.cmp_value <= ol.cmp_value and u.cmp_value <= ou.cmp_value
        elif isinstance (other, _Range_Discrete_) :
            raise TypeError ("Cannot mix %r and %r" % (self, other))
        else :
            return (l.first, u.first) <= other
    # end def __le__

    def __lt__ (self, other) :
        if isinstance (other, _Range_Continuous_) :
            l,  u  = self.LB,  self.UB
            ol, ou = other.LB, other.UB
            return \
                (  (l.cmp_value <= ol.cmp_value and u.cmp_value <  ou.cmp_value)
                or (l.cmp_value <  ol.cmp_value and u.cmp_value <= ou.cmp_value)
                )
        elif isinstance (other, _Range_Discrete_) :
            raise TypeError ("Cannot mix %r and %r" % (self, other))
        else :
            return self.__super.__lt__ (other)
    # end def __lt__

# end class _Range_Continuous_

@totally_ordered
class _Range_Discrete_ (_Range_) :
    """Base class for type-specific discrete range classes."""

    exclusive_continuous = False
    epsilon              = 0

    @property
    def delta (self) :
        """Delta value between adjacent values of the range."""
        raise TypeError \
            ("Discrete range %s must define `delta`" % (self.__class__))
    # end def delta

    @TFL.Meta.Property
    def length (self) :
        """Number of values in range."""
        lower, upper = self.LB.first, self.UB.first
        if lower is None or upper is None :
            result = TFL.Infinity
        else :
            result = self._length (lower, upper) if bool (self) else 0
        return result
    # end def length

    def after (self, other) :
        """Return true if `self` is after `other`."""
        l, ou = self.LB, other.UB
        return bool (self) and bool (other) and l.cmp_value > ou.cmp_value
    # end def after

    def before (self, other) :
        """Return true of `self` is before `other`."""
        u, ol = self.UB, other.LB
        return bool (self) and bool (other) and u.cmp_value < ol.cmp_value
    # end def before

    def bounds_overlap (self, b1, b2, b3, b4) :
        return b1.range is not b2.range or b2.cmp_value == b3.cmp_value
    # end def bounds_overlap

    def is_adjacent (self, other) :
        """Return true if `self` and `other` are adjacent."""
        l, r = (self, other) if self <= other else (other, self)
        add  = self._sub_type_add
        return \
            (   bool (l)
            and bool (r)
            and add (l.UB.first, self.delta) == r.LB.first
            )
    # end def is_adjacent

    def _length (self, lower, upper) :
        return ((upper - lower) // self.delta) + 1
    # end def _length

    def __contains__ (self, item) :
        if isinstance (item, _Range_Discrete_) :
            lb, ub = self.LB,  self.UB
            il, iu = item.LB.first, item.UB.first
            return \
                (   bool (item)
                and lb.contains (il)
                and lb.contains (iu)
                and ub.contains (il)
                and ub.contains (iu)
                )
        elif isinstance (item, _Range_Continuous_) :
            raise TypeError ("Cannot mix %r and %r" % (self, item))
        else :
            return self.__super.__contains__ (item)
    # end def __contains__

    __eq__ = _Range_.__eq__ ### `totally_ordered` looks in class __dict__

    def __iter__ (self) :
        """Iterator over all values of range.

           Does not work for ranges with infinite lower bound.
        """
        add   = self._sub_type_add
        delta = self.delta
        eps   = self.epsilon
        next  = self.LB.first
        last  = \
            (self.UB.first if self.UB.first is not None else TFL.Infinity)
        if eps and last is not None :
            last += eps
        if next is None or last is None :
            raise ValueError \
                ( "Cannot iterate over range `%s` with infinite bound"
                % (self, )
                )
        while next <= last :
            yield next
            next = add (next, delta)
    # end def __iter__

    def __len__ (self) :
        """Number of values in range."""
        return self.length
    # end def __len__

    def __lt__ (self, other) :
        if isinstance (other, _Range_Discrete_) :
            l, u = self.LB.cmp_value, self.UB.cmp_value
            return (l, u) < (other.LB.cmp_value, other.UB.cmp_value)
        elif isinstance (other, _Range_Continuous_) :
            raise TypeError ("Cannot mix %r and %r" % (self, other))
        else :
            return self.__super.__lt__ (other)
    # end def __lt__

# end class _Range_Discrete_

class Float_Range (_Range_Continuous_) :
    """Range of float values."""

    S_Type = float
    """`Float_Range` has subtype `float`."""

# end class Float_Range

class Float_Range_Discrete (_Range_Discrete_) :
    """Range of float values wit discrete delta."""

    S_Type = float
    """`Float_Range` has subtype `float`."""

    delta  = 1.0
    """Default delta between adjacent values of `Float_Range_Discrete` is 1."""

    def __init__ (self, * args, ** kwds) :
        self.pop_to_self (kwds, "delta")
        self.epsilon = self.delta / 10.
        self.__super.__init__ (* args, ** kwds)
    # end def __init__

# end class Float_Range_Discrete

class Int_Range (_Range_Discrete_) :
    """Range of integer values."""

    S_Type = int
    """`Int_Range` has subtype `int`."""

    delta  = 1
    """Default delta between adjacent values of `Int_Range` is 1."""

# end class Int_Range

### define bounds specific classes after range specific classes to
### fer the right order in sphinx generated documentation

class _M_Bounds_ (_M_Base_) :
    """Meta class for bounds type classes"""

    Table   = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        btype = cls.btype
        if btype is not None :
            Table = cls.Table
            if btype in Table :
                raise TypeError \
                    ( "Two different bounds type classes with "
                      "same btype %s: %s, %s"
                    , (btype, Table [btype], cls)
                    )
            Table [btype] = cls
    # end def __init__

    def __getitem__ (cls, key) :
        return cls.Table [key]
    # end def __getitem__

# end class _M_Bounds_

@totally_ordered
class _Bounds_ (TFL.Meta.Object, metaclass = _M_Bounds_) :
    """Base class for bounds types"""

    btype     = None

    def __init__ (self, range) :
        self.range = range
    # end def __init__

    @TFL.Meta.Property
    def bound (self) :
        """Value of bound as specified by corresponding `range` or :attr:`inf`"""
        result = getattr (self.range, self.side)
        if result is None :
            result = self.inf
        return result
    # end def bound

    @TFL.Meta.Property
    def cmp_value (self) :
        """Value used to compare bounds"""
        return (self.first, not self.exclusive) \
            if self.range.delta is None else self.first
    # end def cmp_value

    @TFL.Meta.Property
    def inf (self) :
        """Extreme bound value as defined by `range.finite`, if any"""
        return self.range.finite.get (self.side)
    # end def inf

    @TFL.Meta.Property
    def sort_key (self) :
        """Value used for sorting bounds of two ranges"""
        return (self.first, not self.exclusive, self.bound)
    # end def sort_key

    def contains (self, value) :
        """Determine if bound contains `value`"""
        bound = self.bound
        if bound is None :
            return True
        else :
            return value is not None and self.contains_op (bound, value)
    # end def contains

    def __eq__ (self, rhs) :
        return self.sort_key == \
            (rhs.sort_key if isinstance (rhs, _Bounds_) else rhs)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.sort_key)
    # end def __hash__

    def __lt__ (self, rhs) :
        return self.sort_key < \
            (rhs.sort_key if isinstance (rhs, _Bounds_) else rhs)
    # end def __lt__

    def __repr__ (self) :
        return pyk.reprify ("%s" % self)
    # end def __repr__

    def __str__ (self) :
        return self.fmt % dict (bound = self.bound, btype = self.btype)
    # end def __str__

# end class _Bounds_

class _Exclusive_Bounds_ (_Bounds_) :
    """Mixin for exclusive bounds types."""

    exclusive = True

    @TFL.Meta.Property
    def first (self) :
        """First element inside the `range` next to bound"""
        result = self.bound
        if result is not None :
            delta = self.range.delta
            if delta is not None :
                result = self.delta_op (result, delta)
        return result
    # end def first

# end class _Exclusive_Bounds_

class _Inclusive_Bounds_ (_Bounds_) :
    """Mixin for inclusive bounds types."""

    exclusive = False

    @TFL.Meta.Property
    def first (self) :
        """First element inside the `range` next to bound"""
        return self.bound
    # end def first

# end class _Inclusive_Bounds_

class _Lower_Bounds_ (_Bounds_) :
    """Mixin for lower bounds."""

    fmt         = "%(btype)s%(bound)s"
    side        = "lower"

# end class _Lower_Bounds_

class _Upper_Bounds_ (_Bounds_) :
    """Mixin for upper bounds."""

    fmt         = "%(bound)s%(btype)s"
    side        = "upper"

# end class _Upper_Bounds_

class Exclusive_Lower_Bound (_Exclusive_Bounds_, _Lower_Bounds_) :
    """Exclusive lower bound of a range."""

    btype        = "("
    contains_op  = operator.lt
    contains_rop = operator.ge

    @property
    def delta_op (self) :
        """Operation to add `delta` to `bound`"""
        return self.range._sub_type_add
    # end def delta_op

# end class Exclusive_Lower_Bound

class Exclusive_Upper_Bound (_Exclusive_Bounds_, _Upper_Bounds_) :
    """Exclusive upper bound of a range."""

    btype        = ")"
    contains_op  = operator.gt
    contains_rop = operator.le

    @property
    def delta_op (self) :
        """Operation to add `delta` to `bound`"""
        return self.range._sub_type_sub
    # end def delta_op

# end class Exclusive_Upper_Bound

class Inclusive_Lower_Bound (_Inclusive_Bounds_, _Lower_Bounds_) :
    """Inclusive lower bound of a range."""

    btype        = "["
    contains_op  = operator.le
    contains_rop = operator.gt

# end class Inclusive_Lower_Bound

class Inclusive_Upper_Bound (_Inclusive_Bounds_, _Upper_Bounds_) :
    """Inclusive upper bound of a range."""

    btype        = "]"
    contains_op  = operator.ge
    contains_rop = operator.lt

# end class Inclusive_Upper_Bound

@TFL._Add_Import_Callback ("_TFL.json_dump")
def _import_cb_json_dump (module) :
    @module.default.add_type (_Range_)
    def json_encode_range (o) :
        return str (o)
# end def _import_cb_json_dump

@TFL._Add_Import_Callback ("_TFL.ui_display")
def _import_ui_display (module) :
    @module.ui_display.add_type (_Range_)
    def _ui_display_range (obj) :
        return str (obj)
# end def _import_ui_display

### «text» ### start of documentation
__doc__ = r"""
This module provides base classes for implementing `range types` and
defines two concrete `range types` :class:`Int_Range` and
:class:`Float_Range`.

A `range type` represents a range of values of the `subtype`, i.e.,
the specific type of the range's elements. For instance, the range
type :class:`Int_Range` represents a range of values of subtype `int`.

The `subtype` of a `range type` must be totally ordered so that
exclusion/inclusion of values and overlap of ranges is well-defined.

An instance of a `range type` is defined by its :attr:`lower` and
:attr:`upper` bound; the range comprises all values between
:attr:`lower` and :attr:`upper`. Each bound can be inclusive or
exclusive — inclusive bounds are included in the range, exclusive
bounds are not part of the range. That gives the four combinations:

    ============== ===================================================
    representation bounds
    ============== ===================================================
    []             :class:`inclusive lower<Inclusive_Lower_Bound>`,
                   :class:`inclusive upper<Inclusive_Upper_Bound>`

    [)             :class:`inclusive lower<Inclusive_Lower_Bound>`,
                   :class:`exclusive upper<Exclusive_Upper_Bound>`

    (]             :class:`exclusive lower<Exclusive_Lower_Bound>`,
                   :class:`inclusive upper<Inclusive_Upper_Bound>`

    ()             :class:`exclusive lower<Exclusive_Lower_Bound>`,
                   :class:`exclusive upper<Exclusive_Upper_Bound>`
    ============== ===================================================

By default, a range has bounds `[)`, i.e., inclusive lower and
exclusive upper, matching Python's indexing conventions.

A value of `None` for a `lower` or `upper` bound means that the
corresponding bound is infinite, i.e., unbounded. An infinite lower
bound means that all values less than the upper bound are part of the
range; an infinite upper bound means that all values greater than the
lower bound are part of the range. A specific range type can define
values for `infinite` bounds in the dictionary :attr:`finite`.

For instance, :class:`Time_Range<_TFL.Range_DT.Time_Range>` has a
:attr:`finite` with the value::

    dict (lower = datetime.time.min, upper = datetime.time.max)

Depending on the characteristics of the subtype, there are two kinds
of Range:

* :class:`Discrete<_Range_Discrete_>`

  Discrete range types have a well-defined
  :attr:`delta<_Range_Discrete_.delta>` that specifies the distance
  between adjacent values of the range. Bounded ranges have a specific
  number of elements given by :attr:`length<_Range_Discrete_.length>`
  and can be iterated over. Ranges with a bounded lower bound don't
  have a finite :attr:`length<_Range_Discrete_.length>` but can be
  iterated over, if the caller takes care to terminate the iteration
  manually.

  :class:`Int_Range` is a :class:`discrete range type<_Range_Discrete_>`.

* :class:`Continuous<_Range_Continuous_>`

  Continuous ranges do not have a specific `delta` that specifies
  the distance between adjacent values of the range. Therefore,
  for exclusive bounds there is no defined value closest to the
  exclusive bound's value.

  :class:`Float_Range` is a :class:`continuous range type<_Range_Continuous_>`.

"""

def _show_ab (r1, r2) :
    r1_a_r2 = r1.after  (r2)
    r2_b_r1 = r2.before (r1)
    tail    = "    *** r1 after r2 != r2 before r1 ***" \
        if r1_a_r2 != r2_b_r1 else ""
    print ("%s after %s : %5s%s" % (r1, r2, r1_a_r2, tail))
# end def _show_ab

def _show_adj (r1, r2) :
    r1_ia_r2 = r1.is_adjacent (r2)
    r2_ia_r1 = r2.is_adjacent (r1)
    tail     = "    *** r1 is_adjacent r2 != r2 is_adjacent r1 ***" \
        if r1_ia_r2 != r2_ia_r1 else ""
    print ("%s is_adjacent %s : %5s%s" % (r1, r2, r1_ia_r2, tail))
# end def _show_adj

def _show_fs (R, s) :
    print ("%6s : %r" % (s, R.from_string (s)))
# end def _show_fs

def _show_intersection (r1, r2) :
    r1_in_r2 = r1.intersection (r2)
    r2_in_r1 = r2.intersection (r1)
    tail     = "*** union not communitative ***" \
        if (r1 and r2 and r1_in_r2 != r2_in_r1) else ""
    print ("%s intersection %s : %5s%s" % (r1, r2, r1_in_r2, tail))
# end def _show_intersection

def _show_ovl (r1, r2) :
    r1_ol_r2 = r1.overlaps (r2)
    r2_ol_r1 = r2.overlaps (r1)
    tail     = "    *** overlap not communitative ***" \
        if r1_ol_r2 != r2_ol_r1 else ""
    print ("%s overlaps %s : %5s%s" % (r1, r2, r1_ol_r2, tail))
# end def _show_ovl

def _show_sb (r1, r2) :
    r1_sb_r2 = r1.sorted_bounds (r2)
    r2_sb_r1 = r2.sorted_bounds (r1)
    tail     = "    *** sorted_bounds not communitative ***" \
        if r1_sb_r2 != r2_sb_r1 else ""
    print \
        ( "%s %s --> %s%s"
        % (r1, r2,", ".join ("'%s'" % b for b in r1_sb_r2), tail)
        )
# end def _show_sb

def _show_union (r1, r2) :
    r1_un_r2 = r1.union (r2)
    r2_un_r1 = r2.union (r1)
    tail     = "*** union not communitative ***" \
        if (r1 and r2 and r1_un_r2 != r2_un_r1) else ""
    print ("%s union %s : %5s%s" % (r1, r2, r1_un_r2, tail))
# end def _show_union

_test_float_range = r"""

    >>> R = Float_Range

    >>> infinite = R ()
    >>> infinite_l = R (None, 1.0)
    >>> infinite_u = R (1.0, None)
    >>> infinite
    Float_Range (None, None, '[)')
    >>> print (infinite, infinite_l, infinite_u)
    [None, None) [None, 1.0) [1.0, None)
    >>> bool (infinite), bool (infinite_l), bool (infinite_u)
    (True, True, True)
    >>> infinite in infinite, infinite_l in infinite, infinite_u in infinite
    (True, True, True)
    >>> infinite in infinite_l, infinite in infinite_u, infinite_l in infinite_u
    (False, False, False)

    >>> empty = R (1.0, 1.0)
    >>> empty
    Float_Range (1.0, 1.0, '[)')
    >>> print (empty)
    [1.0, 1.0)
    >>> bool (empty)
    False
    >>> empty.LB.bound, empty.LB.first, empty.LB.inf
    (1.0, 1.0, None)
    >>> empty.UB.bound, empty.UB.first, empty.UB.inf
    (1.0, 1.0, None)
    >>> empty in infinite, empty in infinite_l, empty in infinite_u
    (False, False, False)

    >>> point = R (1.0, 1.0, "[]")
    >>> point
    Float_Range (1.0, 1.0, '[]')
    >>> print (point)
    [1.0, 1.0]
    >>> point.LB.bound, point.LB.first, point.LB.inf
    (1.0, 1.0, None)
    >>> point.UB.bound, point.UB.first, point.UB.inf
    (1.0, 1.0, None)
    >>> bool (point)
    True
    >>> point in infinite, point in infinite_l, point in infinite_u
    (True, False, True)

    >>> point_x = R (1.0, 2.0)
    >>> point_x
    Float_Range (1.0, 2.0, '[)')
    >>> print (point_x)
    [1.0, 2.0)
    >>> point_x.LB.bound, point_x.LB.first, point_x.LB.inf
    (1.0, 1.0, None)
    >>> point_x.UB.bound, point_x.UB.first, point_x.UB.inf
    (2.0, 2.0, None)
    >>> bool (point_x)
    True
    >>> point_x in infinite, point_x in infinite_l, point_x in infinite_u
    (True, False, True)

    >>> ii_24 = R (2.0, 4.0, "[]")
    >>> ix_24 = R (2.0, 4.0, "[)")
    >>> xi_24 = R (2.0, 4.0, "(]")
    >>> xx_24 = R (2.0, 4.0, "()")
    >>> ii_25 = R (2.0, 5.0, "[]")
    >>> ix_25 = R (2.0, 5.0, "[)")
    >>> xi_25 = R (2.0, 5.0, "(]")
    >>> xx_25 = R (2.0, 5.0, "()")

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, portable_repr (r.range_pattern.match (str (r)).groupdict ()))
    [2.0, 4.0] {'LB' : '[', 'UB' : ']', 'lower' : '2.0', 'upper' : '4.0'}
    [2.0, 4.0) {'LB' : '[', 'UB' : ')', 'lower' : '2.0', 'upper' : '4.0'}
    (2.0, 4.0] {'LB' : '(', 'UB' : ']', 'lower' : '2.0', 'upper' : '4.0'}
    (2.0, 4.0) {'LB' : '(', 'UB' : ')', 'lower' : '2.0', 'upper' : '4.0'}

    >>> for r in (point, point_x, ii_24) :
    ...     print (r.FO, r.FO.lower, r.FO.upper)
    [1.0, 1.0] 1.0 1.0
    [1.0, 2.0) 1.0 2.0
    [2.0, 4.0] 2.0 4.0

    >>> for i in range (2, 5) :
    ...     v = float (i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "in", r, ":", v in r)
    2.0 in [2.0, 4.0] : True
    2.0 in [2.0, 4.0) : True
    2.0 in (2.0, 4.0] : False
    2.0 in (2.0, 4.0) : False
    3.0 in [2.0, 4.0] : True
    3.0 in [2.0, 4.0) : True
    3.0 in (2.0, 4.0] : True
    3.0 in (2.0, 4.0) : True
    4.0 in [2.0, 4.0] : True
    4.0 in [2.0, 4.0) : False
    4.0 in (2.0, 4.0] : True
    4.0 in (2.0, 4.0) : False

    >>> for i in range (2, 5) :
    ...     v = float (i)
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "+", r, ":", v + r, "" if v+r == r+v else "*** + isn't communitative ***")
    2.0 + [2.0, 4.0] : [4.0, 6.0]
    2.0 + [2.0, 4.0) : [4.0, 6.0)
    2.0 + (2.0, 4.0] : (4.0, 6.0]
    2.0 + (2.0, 4.0) : (4.0, 6.0)
    3.0 + [2.0, 4.0] : [5.0, 7.0]
    3.0 + [2.0, 4.0) : [5.0, 7.0)
    3.0 + (2.0, 4.0] : (5.0, 7.0]
    3.0 + (2.0, 4.0) : (5.0, 7.0)
    4.0 + [2.0, 4.0] : [6.0, 8.0]
    4.0 + [2.0, 4.0) : [6.0, 8.0)
    4.0 + (2.0, 4.0] : (6.0, 8.0]
    4.0 + (2.0, 4.0) : (6.0, 8.0)

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2.0, 4.0] == [2.0, 4.0] : True True
    [2.0, 4.0] == [2.0, 4.0) : False False
    [2.0, 4.0] == (2.0, 4.0] : False False
    [2.0, 4.0] == (2.0, 4.0) : False False
    [2.0, 4.0) == [2.0, 4.0] : False False
    [2.0, 4.0) == [2.0, 4.0) : True True
    [2.0, 4.0) == (2.0, 4.0] : False False
    [2.0, 4.0) == (2.0, 4.0) : False False
    (2.0, 4.0] == [2.0, 4.0] : False False
    (2.0, 4.0] == [2.0, 4.0) : False False
    (2.0, 4.0] == (2.0, 4.0] : True True
    (2.0, 4.0] == (2.0, 4.0) : False False
    (2.0, 4.0) == [2.0, 4.0] : False False
    (2.0, 4.0) == [2.0, 4.0) : False False
    (2.0, 4.0) == (2.0, 4.0] : False False
    (2.0, 4.0) == (2.0, 4.0) : True True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2.0, 4.0] == [2.0, 5.0] : False False
    [2.0, 4.0] == [2.0, 5.0) : False False
    [2.0, 4.0] == (2.0, 5.0] : False False
    [2.0, 4.0] == (2.0, 5.0) : False False
    [2.0, 4.0) == [2.0, 5.0] : False False
    [2.0, 4.0) == [2.0, 5.0) : False False
    [2.0, 4.0) == (2.0, 5.0] : False False
    [2.0, 4.0) == (2.0, 5.0) : False False
    (2.0, 4.0] == [2.0, 5.0] : False False
    (2.0, 4.0] == [2.0, 5.0) : False False
    (2.0, 4.0] == (2.0, 5.0] : False False
    (2.0, 4.0] == (2.0, 5.0) : False False
    (2.0, 4.0) == [2.0, 5.0] : False False
    (2.0, 4.0) == [2.0, 5.0) : False False
    (2.0, 4.0) == (2.0, 5.0] : False False
    (2.0, 4.0) == (2.0, 5.0) : False False

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print \
    ...             ( "%s < %s : %5s; %s <= %s : %s"
    ...             % (r1, r2, r1 < r2, r1, r2, r1 <= r2)
    ...             )
    [2.0, 4.0] < [2.0, 4.0] : False; [2.0, 4.0] <= [2.0, 4.0] : True
    [2.0, 4.0] < [2.0, 4.0) : False; [2.0, 4.0] <= [2.0, 4.0) : False
    [2.0, 4.0] < (2.0, 4.0] : False; [2.0, 4.0] <= (2.0, 4.0] : False
    [2.0, 4.0] < (2.0, 4.0) : False; [2.0, 4.0] <= (2.0, 4.0) : False
    [2.0, 4.0) < [2.0, 4.0] :  True; [2.0, 4.0) <= [2.0, 4.0] : True
    [2.0, 4.0) < [2.0, 4.0) : False; [2.0, 4.0) <= [2.0, 4.0) : True
    [2.0, 4.0) < (2.0, 4.0] : False; [2.0, 4.0) <= (2.0, 4.0] : False
    [2.0, 4.0) < (2.0, 4.0) : False; [2.0, 4.0) <= (2.0, 4.0) : False
    (2.0, 4.0] < [2.0, 4.0] :  True; (2.0, 4.0] <= [2.0, 4.0] : True
    (2.0, 4.0] < [2.0, 4.0) : False; (2.0, 4.0] <= [2.0, 4.0) : False
    (2.0, 4.0] < (2.0, 4.0] : False; (2.0, 4.0] <= (2.0, 4.0] : True
    (2.0, 4.0] < (2.0, 4.0) : False; (2.0, 4.0] <= (2.0, 4.0) : False
    (2.0, 4.0) < [2.0, 4.0] :  True; (2.0, 4.0) <= [2.0, 4.0] : True
    (2.0, 4.0) < [2.0, 4.0) :  True; (2.0, 4.0) <= [2.0, 4.0) : True
    (2.0, 4.0) < (2.0, 4.0] :  True; (2.0, 4.0) <= (2.0, 4.0] : True
    (2.0, 4.0) < (2.0, 4.0) : False; (2.0, 4.0) <= (2.0, 4.0) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print \
    ...             ( "%s > %s : %5s; %s >= %s : %s"
    ...             % (r1, r2, r1 > r2, r1, r2, r1 >= r2)
    ...             )
    [2.0, 4.0] > [2.0, 4.0] : False; [2.0, 4.0] >= [2.0, 4.0] : True
    [2.0, 4.0] > [2.0, 4.0) :  True; [2.0, 4.0] >= [2.0, 4.0) : True
    [2.0, 4.0] > (2.0, 4.0] :  True; [2.0, 4.0] >= (2.0, 4.0] : True
    [2.0, 4.0] > (2.0, 4.0) :  True; [2.0, 4.0] >= (2.0, 4.0) : True
    [2.0, 4.0) > [2.0, 4.0] : False; [2.0, 4.0) >= [2.0, 4.0] : False
    [2.0, 4.0) > [2.0, 4.0) : False; [2.0, 4.0) >= [2.0, 4.0) : True
    [2.0, 4.0) > (2.0, 4.0] : False; [2.0, 4.0) >= (2.0, 4.0] : False
    [2.0, 4.0) > (2.0, 4.0) :  True; [2.0, 4.0) >= (2.0, 4.0) : True
    (2.0, 4.0] > [2.0, 4.0] : False; (2.0, 4.0] >= [2.0, 4.0] : False
    (2.0, 4.0] > [2.0, 4.0) : False; (2.0, 4.0] >= [2.0, 4.0) : False
    (2.0, 4.0] > (2.0, 4.0] : False; (2.0, 4.0] >= (2.0, 4.0] : True
    (2.0, 4.0] > (2.0, 4.0) :  True; (2.0, 4.0] >= (2.0, 4.0) : True
    (2.0, 4.0) > [2.0, 4.0] : False; (2.0, 4.0) >= [2.0, 4.0] : False
    (2.0, 4.0) > [2.0, 4.0) : False; (2.0, 4.0) >= [2.0, 4.0) : False
    (2.0, 4.0) > (2.0, 4.0] : False; (2.0, 4.0) >= (2.0, 4.0] : False
    (2.0, 4.0) > (2.0, 4.0) : False; (2.0, 4.0) >= (2.0, 4.0) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "in", r2, ":", r1 in r2)
    [2.0, 4.0] in [2.0, 4.0] : True
    [2.0, 4.0] in [2.0, 4.0) : False
    [2.0, 4.0] in (2.0, 4.0] : False
    [2.0, 4.0] in (2.0, 4.0) : False
    [2.0, 4.0) in [2.0, 4.0] : True
    [2.0, 4.0) in [2.0, 4.0) : True
    [2.0, 4.0) in (2.0, 4.0] : False
    [2.0, 4.0) in (2.0, 4.0) : False
    (2.0, 4.0] in [2.0, 4.0] : True
    (2.0, 4.0] in [2.0, 4.0) : False
    (2.0, 4.0] in (2.0, 4.0] : True
    (2.0, 4.0] in (2.0, 4.0) : False
    (2.0, 4.0) in [2.0, 4.0] : True
    (2.0, 4.0) in [2.0, 4.0) : True
    (2.0, 4.0) in (2.0, 4.0] : True
    (2.0, 4.0) in (2.0, 4.0) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "in", r2, ":", r1 in r2, "<->", r2 in r1)
    [2.0, 4.0] in [2.0, 5.0] : True <-> False
    [2.0, 4.0] in [2.0, 5.0) : True <-> False
    [2.0, 4.0] in (2.0, 5.0] : False <-> False
    [2.0, 4.0] in (2.0, 5.0) : False <-> False
    [2.0, 4.0) in [2.0, 5.0] : True <-> False
    [2.0, 4.0) in [2.0, 5.0) : True <-> False
    [2.0, 4.0) in (2.0, 5.0] : False <-> False
    [2.0, 4.0) in (2.0, 5.0) : False <-> False
    (2.0, 4.0] in [2.0, 5.0] : True <-> False
    (2.0, 4.0] in [2.0, 5.0) : True <-> False
    (2.0, 4.0] in (2.0, 5.0] : True <-> False
    (2.0, 4.0] in (2.0, 5.0) : True <-> False
    (2.0, 4.0) in [2.0, 5.0] : True <-> False
    (2.0, 4.0) in [2.0, 5.0) : True <-> False
    (2.0, 4.0) in (2.0, 5.0] : True <-> False
    (2.0, 4.0) in (2.0, 5.0) : True <-> False

    >>> for i in range (1, 4) :
    ...     for bs in ("[]", "[)", "(]", "()") :
    ...         r = R (1.0, float (i), bs)
    ...         print \
    ...             ( "r : %s %5s; 1 in r: %5s; 2 in r: %5s"
    ...             % (r, bool (r), 1 in r, 2 in r)
    ...             )
    r : [1.0, 1.0]  True; 1 in r:  True; 2 in r: False
    r : [1.0, 1.0) False; 1 in r: False; 2 in r: False
    r : (1.0, 1.0] False; 1 in r: False; 2 in r: False
    r : (1.0, 1.0) False; 1 in r: False; 2 in r: False
    r : [1.0, 2.0]  True; 1 in r:  True; 2 in r:  True
    r : [1.0, 2.0)  True; 1 in r:  True; 2 in r: False
    r : (1.0, 2.0]  True; 1 in r: False; 2 in r:  True
    r : (1.0, 2.0)  True; 1 in r: False; 2 in r: False
    r : [1.0, 3.0]  True; 1 in r:  True; 2 in r:  True
    r : [1.0, 3.0)  True; 1 in r:  True; 2 in r:  True
    r : (1.0, 3.0]  True; 1 in r: False; 2 in r:  True
    r : (1.0, 3.0)  True; 1 in r: False; 2 in r:  True


    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ab (R (2, 3, bt1), R (1.0, 2, bt2))
    ...         _show_ab (R (3, 5, bt1), R (1.0, 3, bt2))
    ...         _show_ab (R (4, 6, bt1), R (1.0, 3, bt2))
    [2, 3] after [1.0, 2] : False
    [3, 5] after [1.0, 3] : False
    [4, 6] after [1.0, 3] :  True
    [2, 3] after [1.0, 2) :  True
    [3, 5] after [1.0, 3) :  True
    [4, 6] after [1.0, 3) :  True
    [2, 3] after (1.0, 2] : False
    [3, 5] after (1.0, 3] : False
    [4, 6] after (1.0, 3] :  True
    [2, 3] after (1.0, 2) :  True
    [3, 5] after (1.0, 3) :  True
    [4, 6] after (1.0, 3) :  True
    [2, 3) after [1.0, 2] : False
    [3, 5) after [1.0, 3] : False
    [4, 6) after [1.0, 3] :  True
    [2, 3) after [1.0, 2) :  True
    [3, 5) after [1.0, 3) :  True
    [4, 6) after [1.0, 3) :  True
    [2, 3) after (1.0, 2] : False
    [3, 5) after (1.0, 3] : False
    [4, 6) after (1.0, 3] :  True
    [2, 3) after (1.0, 2) :  True
    [3, 5) after (1.0, 3) :  True
    [4, 6) after (1.0, 3) :  True
    (2, 3] after [1.0, 2] : False
    (3, 5] after [1.0, 3] : False
    (4, 6] after [1.0, 3] :  True
    (2, 3] after [1.0, 2) :  True
    (3, 5] after [1.0, 3) :  True
    (4, 6] after [1.0, 3) :  True
    (2, 3] after (1.0, 2] : False
    (3, 5] after (1.0, 3] : False
    (4, 6] after (1.0, 3] :  True
    (2, 3] after (1.0, 2) :  True
    (3, 5] after (1.0, 3) :  True
    (4, 6] after (1.0, 3) :  True
    (2, 3) after [1.0, 2] : False
    (3, 5) after [1.0, 3] : False
    (4, 6) after [1.0, 3] :  True
    (2, 3) after [1.0, 2) :  True
    (3, 5) after [1.0, 3) :  True
    (4, 6) after [1.0, 3) :  True
    (2, 3) after (1.0, 2] : False
    (3, 5) after (1.0, 3] : False
    (4, 6) after (1.0, 3] :  True
    (2, 3) after (1.0, 2) :  True
    (3, 5) after (1.0, 3) :  True
    (4, 6) after (1.0, 3) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_adj (R (2, 3, bt1), R (1.0, 2, bt2))
    ...         _show_adj (R (3, 5, bt1), R (1.0, 3, bt2))
    ...         _show_adj (R (4, 6, bt1), R (1.0, 3, bt2))
    [2, 3] is_adjacent [1.0, 2] : False
    [3, 5] is_adjacent [1.0, 3] : False
    [4, 6] is_adjacent [1.0, 3] : False
    [2, 3] is_adjacent [1.0, 2) :  True
    [3, 5] is_adjacent [1.0, 3) :  True
    [4, 6] is_adjacent [1.0, 3) : False
    [2, 3] is_adjacent (1.0, 2] : False
    [3, 5] is_adjacent (1.0, 3] : False
    [4, 6] is_adjacent (1.0, 3] : False
    [2, 3] is_adjacent (1.0, 2) :  True
    [3, 5] is_adjacent (1.0, 3) :  True
    [4, 6] is_adjacent (1.0, 3) : False
    [2, 3) is_adjacent [1.0, 2] : False
    [3, 5) is_adjacent [1.0, 3] : False
    [4, 6) is_adjacent [1.0, 3] : False
    [2, 3) is_adjacent [1.0, 2) :  True
    [3, 5) is_adjacent [1.0, 3) :  True
    [4, 6) is_adjacent [1.0, 3) : False
    [2, 3) is_adjacent (1.0, 2] : False
    [3, 5) is_adjacent (1.0, 3] : False
    [4, 6) is_adjacent (1.0, 3] : False
    [2, 3) is_adjacent (1.0, 2) :  True
    [3, 5) is_adjacent (1.0, 3) :  True
    [4, 6) is_adjacent (1.0, 3) : False
    (2, 3] is_adjacent [1.0, 2] :  True
    (3, 5] is_adjacent [1.0, 3] :  True
    (4, 6] is_adjacent [1.0, 3] : False
    (2, 3] is_adjacent [1.0, 2) :  True
    (3, 5] is_adjacent [1.0, 3) :  True
    (4, 6] is_adjacent [1.0, 3) : False
    (2, 3] is_adjacent (1.0, 2] :  True
    (3, 5] is_adjacent (1.0, 3] :  True
    (4, 6] is_adjacent (1.0, 3] : False
    (2, 3] is_adjacent (1.0, 2) :  True
    (3, 5] is_adjacent (1.0, 3) :  True
    (4, 6] is_adjacent (1.0, 3) : False
    (2, 3) is_adjacent [1.0, 2] :  True
    (3, 5) is_adjacent [1.0, 3] :  True
    (4, 6) is_adjacent [1.0, 3] : False
    (2, 3) is_adjacent [1.0, 2) :  True
    (3, 5) is_adjacent [1.0, 3) :  True
    (4, 6) is_adjacent [1.0, 3) : False
    (2, 3) is_adjacent (1.0, 2] :  True
    (3, 5) is_adjacent (1.0, 3] :  True
    (4, 6) is_adjacent (1.0, 3] : False
    (2, 3) is_adjacent (1.0, 2) :  True
    (3, 5) is_adjacent (1.0, 3) :  True
    (4, 6) is_adjacent (1.0, 3) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_sb (R (3, 5, bt1), R (1.0, 3, bt2))
    [3, 5] [1.0, 3] --> '[1.0', '3]', '[3', '5]'
    [3, 5] [1.0, 3) --> '[1.0', '3)', '[3', '5]'
    [3, 5] (1.0, 3] --> '(1.0', '3]', '[3', '5]'
    [3, 5] (1.0, 3) --> '(1.0', '3)', '[3', '5]'
    [3, 5) [1.0, 3] --> '[1.0', '3]', '[3', '5)'
    [3, 5) [1.0, 3) --> '[1.0', '3)', '[3', '5)'
    [3, 5) (1.0, 3] --> '(1.0', '3]', '[3', '5)'
    [3, 5) (1.0, 3) --> '(1.0', '3)', '[3', '5)'
    (3, 5] [1.0, 3] --> '[1.0', '(3', '3]', '5]'
    (3, 5] [1.0, 3) --> '[1.0', '3)', '(3', '5]'
    (3, 5] (1.0, 3] --> '(1.0', '(3', '3]', '5]'
    (3, 5] (1.0, 3) --> '(1.0', '3)', '(3', '5]'
    (3, 5) [1.0, 3] --> '[1.0', '(3', '3]', '5)'
    (3, 5) [1.0, 3) --> '[1.0', '3)', '(3', '5)'
    (3, 5) (1.0, 3] --> '(1.0', '(3', '3]', '5)'
    (3, 5) (1.0, 3) --> '(1.0', '3)', '(3', '5)'

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_sb (R (1.0, 5, bt1), R (2, 6, bt2))
    [1.0, 5] [2, 6] --> '[1.0', '[2', '5]', '6]'
    [1.0, 5] [2, 6) --> '[1.0', '[2', '5]', '6)'
    [1.0, 5] (2, 6] --> '[1.0', '(2', '5]', '6]'
    [1.0, 5] (2, 6) --> '[1.0', '(2', '5]', '6)'
    [1.0, 5) [2, 6] --> '[1.0', '[2', '5)', '6]'
    [1.0, 5) [2, 6) --> '[1.0', '[2', '5)', '6)'
    [1.0, 5) (2, 6] --> '[1.0', '(2', '5)', '6]'
    [1.0, 5) (2, 6) --> '[1.0', '(2', '5)', '6)'
    (1.0, 5] [2, 6] --> '(1.0', '[2', '5]', '6]'
    (1.0, 5] [2, 6) --> '(1.0', '[2', '5]', '6)'
    (1.0, 5] (2, 6] --> '(1.0', '(2', '5]', '6]'
    (1.0, 5] (2, 6) --> '(1.0', '(2', '5]', '6)'
    (1.0, 5) [2, 6] --> '(1.0', '[2', '5)', '6]'
    (1.0, 5) [2, 6) --> '(1.0', '[2', '5)', '6)'
    (1.0, 5) (2, 6] --> '(1.0', '(2', '5)', '6]'
    (1.0, 5) (2, 6) --> '(1.0', '(2', '5)', '6)'

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (3, 5, bt1), R (1.0, 3, bt2))
    [3, 5] overlaps [1.0, 3] :  True
    [3, 5] overlaps [1.0, 3) : False
    [3, 5] overlaps (1.0, 3] :  True
    [3, 5] overlaps (1.0, 3) : False
    [3, 5) overlaps [1.0, 3] :  True
    [3, 5) overlaps [1.0, 3) : False
    [3, 5) overlaps (1.0, 3] :  True
    [3, 5) overlaps (1.0, 3) : False
    (3, 5] overlaps [1.0, 3] : False
    (3, 5] overlaps [1.0, 3) : False
    (3, 5] overlaps (1.0, 3] : False
    (3, 5] overlaps (1.0, 3) : False
    (3, 5) overlaps [1.0, 3] : False
    (3, 5) overlaps [1.0, 3) : False
    (3, 5) overlaps (1.0, 3] : False
    (3, 5) overlaps (1.0, 3) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (3, 5, bt1), R (1.0, 4, bt2))
    [3, 5] overlaps [1.0, 4] :  True
    [3, 5] overlaps [1.0, 4) :  True
    [3, 5] overlaps (1.0, 4] :  True
    [3, 5] overlaps (1.0, 4) :  True
    [3, 5) overlaps [1.0, 4] :  True
    [3, 5) overlaps [1.0, 4) :  True
    [3, 5) overlaps (1.0, 4] :  True
    [3, 5) overlaps (1.0, 4) :  True
    (3, 5] overlaps [1.0, 4] :  True
    (3, 5] overlaps [1.0, 4) :  True
    (3, 5] overlaps (1.0, 4] :  True
    (3, 5] overlaps (1.0, 4) :  True
    (3, 5) overlaps [1.0, 4] :  True
    (3, 5) overlaps [1.0, 4) :  True
    (3, 5) overlaps (1.0, 4] :  True
    (3, 5) overlaps (1.0, 4) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (3, 5, bt1), R (1.0, 3, bt2))
    [3, 5] intersection [1.0, 3] : [3, 3]
    [3, 5] intersection [1.0, 3) : (3, 3)
    [3, 5] intersection (1.0, 3] : [3, 3]
    [3, 5] intersection (1.0, 3) : (3, 3)
    [3, 5) intersection [1.0, 3] : [3, 3]
    [3, 5) intersection [1.0, 3) : (3, 3)
    [3, 5) intersection (1.0, 3] : [3, 3]
    [3, 5) intersection (1.0, 3) : (3, 3)
    (3, 5] intersection [1.0, 3] : (3, 3)
    (3, 5] intersection [1.0, 3) : (3, 3)
    (3, 5] intersection (1.0, 3] : (3, 3)
    (3, 5] intersection (1.0, 3) : (3, 3)
    (3, 5) intersection [1.0, 3] : (3, 3)
    (3, 5) intersection [1.0, 3) : (3, 3)
    (3, 5) intersection (1.0, 3] : (3, 3)
    (3, 5) intersection (1.0, 3) : (3, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (3, 5, bt1), R (1.0, 4, bt2))
    [3, 5] intersection [1.0, 4] : [3, 4]
    [3, 5] intersection [1.0, 4) : [3, 4]
    [3, 5] intersection (1.0, 4] : [3, 4]
    [3, 5] intersection (1.0, 4) : [3, 4]
    [3, 5) intersection [1.0, 4] : [3, 4]
    [3, 5) intersection [1.0, 4) : [3, 4]
    [3, 5) intersection (1.0, 4] : [3, 4]
    [3, 5) intersection (1.0, 4) : [3, 4]
    (3, 5] intersection [1.0, 4] : [3, 4]
    (3, 5] intersection [1.0, 4) : [3, 4]
    (3, 5] intersection (1.0, 4] : [3, 4]
    (3, 5] intersection (1.0, 4) : [3, 4]
    (3, 5) intersection [1.0, 4] : [3, 4]
    (3, 5) intersection [1.0, 4) : [3, 4]
    (3, 5) intersection (1.0, 4] : [3, 4]
    (3, 5) intersection (1.0, 4) : [3, 4]

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (3, 5, bt1), R (1.0, 3, bt2))
    [3, 5] union [1.0, 3] : [1.0, 5]
    [3, 5] union [1.0, 3) : (3, 3)
    [3, 5] union (1.0, 3] : (1.0, 5]
    [3, 5] union (1.0, 3) : (3, 3)
    [3, 5) union [1.0, 3] : [1.0, 5)
    [3, 5) union [1.0, 3) : (3, 3)
    [3, 5) union (1.0, 3] : (1.0, 5)
    [3, 5) union (1.0, 3) : (3, 3)
    (3, 5] union [1.0, 3] : (3, 3)
    (3, 5] union [1.0, 3) : (3, 3)
    (3, 5] union (1.0, 3] : (3, 3)
    (3, 5] union (1.0, 3) : (3, 3)
    (3, 5) union [1.0, 3] : (3, 3)
    (3, 5) union [1.0, 3) : (3, 3)
    (3, 5) union (1.0, 3] : (3, 3)
    (3, 5) union (1.0, 3) : (3, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (3, 5, bt1), R (1.0, 4, bt2))
    [3, 5] union [1.0, 4] : [1.0, 5]
    [3, 5] union [1.0, 4) : [1.0, 5]
    [3, 5] union (1.0, 4] : (1.0, 5]
    [3, 5] union (1.0, 4) : (1.0, 5]
    [3, 5) union [1.0, 4] : [1.0, 5)
    [3, 5) union [1.0, 4) : [1.0, 5)
    [3, 5) union (1.0, 4] : (1.0, 5)
    [3, 5) union (1.0, 4) : (1.0, 5)
    (3, 5] union [1.0, 4] : [1.0, 5]
    (3, 5] union [1.0, 4) : [1.0, 5]
    (3, 5] union (1.0, 4] : (1.0, 5]
    (3, 5] union (1.0, 4) : (1.0, 5]
    (3, 5) union [1.0, 4] : [1.0, 5)
    (3, 5) union [1.0, 4) : [1.0, 5)
    (3, 5) union (1.0, 4] : (1.0, 5)
    (3, 5) union (1.0, 4) : (1.0, 5)

    >>> rs = (",5", "3,", "3, 5", "[1, 2]", "[2, 2)", "(1, 5]", "(1, 3)")
    >>> for r in rs :
    ...     _show_fs (R, r)
        ,5 : Float_Range (None, 5.0, '[)')
       3,  : Float_Range (3.0, None, '[)')
      3, 5 : Float_Range (3.0, 5.0, '[)')
    [1, 2] : Float_Range (1.0, 2.0, '[]')
    [2, 2) : Float_Range (2.0, 2.0, '[)')
    (1, 5] : Float_Range (1.0, 5.0, '(]')
    (1, 3) : Float_Range (1.0, 3.0, '()')

    >>> Rd = Float_Range_Discrete

    >>> r1 = Rd (0.0, 1.0, "[]", delta = 0.2)
    >>> print_prepr (list (r1))
    [0, 0.2, 0.4, 0.6, 0.8, 1]

    >>> r2 = Rd (0.0, 1.0, "()", delta = 0.2)
    >>> print_prepr (list (r2))
    [0.2, 0.4, 0.6, 0.8]

""" ### _test_float_range

_test_int_range = r"""

    >>> R = Int_Range

    >>> infinite   = R ()
    >>> infinite_l = R (None, 1)
    >>> infinite_u = R (1, None)
    >>> infinite
    Int_Range (None, None, '[)')
    >>> print (infinite, infinite_l, infinite_u)
    [None, None) [None, 1) [1, None)
    >>> bool (infinite), bool (infinite_l), bool (infinite_u)
    (True, True, True)
    >>> infinite in infinite, infinite_l in infinite, infinite_u in infinite
    (True, True, True)
    >>> infinite in infinite_l, infinite in infinite_u, infinite_l in infinite_u
    (False, False, False)
    >>> print_prepr ((infinite.length, infinite_l.length, infinite_u.length))
    (Infinity, Infinity, Infinity)

    >>> empty = R (1, 1)
    >>> empty
    Int_Range (1, 1, '[)')
    >>> print (empty)
    [1, 1)
    >>> bool (empty)
    False
    >>> empty.LB.bound, empty.LB.first, empty.LB.inf
    (1, 1, None)
    >>> empty.UB.bound, empty.UB.first, empty.UB.inf
    (1, 0, None)
    >>> empty in infinite, empty in infinite_l, empty in infinite_u
    (False, False, False)
    >>> empty.length
    0

    >>> point = R (1, 1, "[]")
    >>> point
    Int_Range (1, 1, '[]')
    >>> print (point)
    [1, 1]
    >>> point.LB.bound, point.LB.first, point.LB.inf
    (1, 1, None)
    >>> point.UB.bound, point.UB.first, point.UB.inf
    (1, 1, None)
    >>> bool (point)
    True
    >>> point in infinite, point in infinite_l, point in infinite_u
    (True, False, True)
    >>> point.length
    1

    >>> point_x = R (1, 2)
    >>> point_x
    Int_Range (1, 2, '[)')
    >>> print (point_x)
    [1, 2)
    >>> point_x.LB.bound, point_x.LB.first, point_x.LB.inf
    (1, 1, None)
    >>> point_x.UB.bound, point_x.UB.first, point_x.UB.inf
    (2, 1, None)
    >>> bool (point_x)
    True
    >>> point_x in infinite, point_x in infinite_l, point_x in infinite_u
    (True, False, True)
    >>> point_x.length
    1

    >>> ii_24 = R (2, 4, "[]")
    >>> ix_24 = R (2, 4, "[)")
    >>> xi_24 = R (2, 4, "(]")
    >>> xx_24 = R (2, 4, "()")
    >>> ii_25 = R (2, 5, "[]")
    >>> ix_25 = R (2, 5, "[)")
    >>> xi_25 = R (2, 5, "(]")
    >>> xx_25 = R (2, 5, "()")

    >>> for r in (ii_24, ix_24, xi_24, xx_24, empty) :
    ...     print (r, len (r), tuple (r))
    [2, 4] 3 (2, 3, 4)
    [2, 4) 2 (2, 3)
    (2, 4] 2 (3, 4)
    (2, 4) 1 (3,)
    [1, 1) 0 ()

    >>> for r in (point, point_x, ii_24) :
    ...     print (r.FO, r.FO.lower, r.FO.upper)
    [1, 1] 1 1
    [1, 2) 1 2
    [2, 4] 2 4

    >>> with expect_except (AttributeError) : # doctest:+ELLIPSIS
    ...     ii_24.lower  = -2
    ...     ii_24.upper  = 20
    ...     ii_24.btype  = "()"
    ...     ii_24.length = 0
    AttributeError: ...

    >>> with expect_except (AttributeError) : # doctest:+ELLIPSIS
    ...     ii_24.upper  = 20
    AttributeError: ...

    >>> with expect_except (AttributeError) : # doctest:+ELLIPSIS
    ...     ii_24.btype  = "()"
    AttributeError: ...

    >>> with expect_except (AttributeError) : # doctest:+ELLIPSIS
    ...     ii_24.length = 0
    AttributeError: ...

    >>> for r in (ii_24, ix_24, xi_24, xx_24) :
    ...     print (r, portable_repr (r.range_pattern.match (str (r)).groupdict ()))
    [2, 4] {'LB' : '[', 'UB' : ']', 'lower' : '2', 'upper' : '4'}
    [2, 4) {'LB' : '[', 'UB' : ')', 'lower' : '2', 'upper' : '4'}
    (2, 4] {'LB' : '(', 'UB' : ']', 'lower' : '2', 'upper' : '4'}
    (2, 4) {'LB' : '(', 'UB' : ')', 'lower' : '2', 'upper' : '4'}

    >>> for v in range (2, 5) :
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (v, "in", r, ":", v in r)
    2 in [2, 4] : True
    2 in [2, 4) : True
    2 in (2, 4] : False
    2 in (2, 4) : False
    3 in [2, 4] : True
    3 in [2, 4) : True
    3 in (2, 4] : True
    3 in (2, 4) : True
    4 in [2, 4] : True
    4 in [2, 4) : False
    4 in (2, 4] : True
    4 in (2, 4) : False

    >>> for v in range (2, 5) :
    ...     for r in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r, "-", v, ":", r - v)
    [2, 4] - 2 : [0, 2]
    [2, 4) - 2 : [0, 2)
    (2, 4] - 2 : (0, 2]
    (2, 4) - 2 : (0, 2)
    [2, 4] - 3 : [-1, 1]
    [2, 4) - 3 : [-1, 1)
    (2, 4] - 3 : (-1, 1]
    (2, 4) - 3 : (-1, 1)
    [2, 4] - 4 : [-2, 0]
    [2, 4) - 4 : [-2, 0)
    (2, 4] - 4 : (-2, 0]
    (2, 4) - 4 : (-2, 0)

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2, 4] == [2, 4] : True True
    [2, 4] == [2, 4) : False False
    [2, 4] == (2, 4] : False False
    [2, 4] == (2, 4) : False False
    [2, 4) == [2, 4] : False False
    [2, 4) == [2, 4) : True True
    [2, 4) == (2, 4] : False False
    [2, 4) == (2, 4) : False False
    (2, 4] == [2, 4] : False False
    (2, 4] == [2, 4) : False False
    (2, 4] == (2, 4] : True True
    (2, 4] == (2, 4) : False False
    (2, 4) == [2, 4] : False False
    (2, 4) == [2, 4) : False False
    (2, 4) == (2, 4] : False False
    (2, 4) == (2, 4) : True True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "==", r2, ":", r1 == r2, not r1 != r2)
    [2, 4] == [2, 5] : False False
    [2, 4] == [2, 5) : True True
    [2, 4] == (2, 5] : False False
    [2, 4] == (2, 5) : False False
    [2, 4) == [2, 5] : False False
    [2, 4) == [2, 5) : False False
    [2, 4) == (2, 5] : False False
    [2, 4) == (2, 5) : False False
    (2, 4] == [2, 5] : False False
    (2, 4] == [2, 5) : False False
    (2, 4] == (2, 5] : False False
    (2, 4] == (2, 5) : True True
    (2, 4) == [2, 5] : False False
    (2, 4) == [2, 5) : False False
    (2, 4) == (2, 5] : False False
    (2, 4) == (2, 5) : False False

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print \
    ...             ( "%s < %s : %5s; %s <= %s : %s"
    ...             % (r1, r2, r1 < r2, r1, r2, r1 <= r2)
    ...             )
    [2, 4] < [2, 5] :  True; [2, 4] <= [2, 5] : True
    [2, 4] < [2, 5) : False; [2, 4] <= [2, 5) : True
    [2, 4] < (2, 5] :  True; [2, 4] <= (2, 5] : True
    [2, 4] < (2, 5) :  True; [2, 4] <= (2, 5) : True
    [2, 4) < [2, 5] :  True; [2, 4) <= [2, 5] : True
    [2, 4) < [2, 5) :  True; [2, 4) <= [2, 5) : True
    [2, 4) < (2, 5] :  True; [2, 4) <= (2, 5] : True
    [2, 4) < (2, 5) :  True; [2, 4) <= (2, 5) : True
    (2, 4] < [2, 5] : False; (2, 4] <= [2, 5] : False
    (2, 4] < [2, 5) : False; (2, 4] <= [2, 5) : False
    (2, 4] < (2, 5] :  True; (2, 4] <= (2, 5] : True
    (2, 4] < (2, 5) : False; (2, 4] <= (2, 5) : True
    (2, 4) < [2, 5] : False; (2, 4) <= [2, 5] : False
    (2, 4) < [2, 5) : False; (2, 4) <= [2, 5) : False
    (2, 4) < (2, 5] :  True; (2, 4) <= (2, 5] : True
    (2, 4) < (2, 5) :  True; (2, 4) <= (2, 5) : True

    >>> for r1 in (ii_25, ix_25, xi_25, xx_25) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print \
    ...             ( "%s > %s : %5s; %s >= %s : %s"
    ...             % (r1, r2, r1 > r2, r1, r2, r1 >= r2)
    ...             )
    [2, 5] > [2, 4] :  True; [2, 5] >= [2, 4] : True
    [2, 5] > [2, 4) :  True; [2, 5] >= [2, 4) : True
    [2, 5] > (2, 4] : False; [2, 5] >= (2, 4] : False
    [2, 5] > (2, 4) : False; [2, 5] >= (2, 4) : False
    [2, 5) > [2, 4] : False; [2, 5) >= [2, 4] : True
    [2, 5) > [2, 4) :  True; [2, 5) >= [2, 4) : True
    [2, 5) > (2, 4] : False; [2, 5) >= (2, 4] : False
    [2, 5) > (2, 4) : False; [2, 5) >= (2, 4) : False
    (2, 5] > [2, 4] :  True; (2, 5] >= [2, 4] : True
    (2, 5] > [2, 4) :  True; (2, 5] >= [2, 4) : True
    (2, 5] > (2, 4] :  True; (2, 5] >= (2, 4] : True
    (2, 5] > (2, 4) :  True; (2, 5] >= (2, 4) : True
    (2, 5) > [2, 4] :  True; (2, 5) >= [2, 4] : True
    (2, 5) > [2, 4) :  True; (2, 5) >= [2, 4) : True
    (2, 5) > (2, 4] : False; (2, 5) >= (2, 4] : True
    (2, 5) > (2, 4) :  True; (2, 5) >= (2, 4) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_24, ix_24, xi_24, xx_24) :
    ...         print (r1, "in", r2, ":", r1 in r2)
    [2, 4] in [2, 4] : True
    [2, 4] in [2, 4) : False
    [2, 4] in (2, 4] : False
    [2, 4] in (2, 4) : False
    [2, 4) in [2, 4] : True
    [2, 4) in [2, 4) : True
    [2, 4) in (2, 4] : False
    [2, 4) in (2, 4) : False
    (2, 4] in [2, 4] : True
    (2, 4] in [2, 4) : False
    (2, 4] in (2, 4] : True
    (2, 4] in (2, 4) : False
    (2, 4) in [2, 4] : True
    (2, 4) in [2, 4) : True
    (2, 4) in (2, 4] : True
    (2, 4) in (2, 4) : True

    >>> for r1 in (ii_24, ix_24, xi_24, xx_24) :
    ...     for r2 in (ii_25, ix_25, xi_25, xx_25) :
    ...         print (r1, "in", r2, ":", r1 in r2, "<->", r1.contains (r2))
    [2, 4] in [2, 5] : True <-> False
    [2, 4] in [2, 5) : True <-> True
    [2, 4] in (2, 5] : False <-> False
    [2, 4] in (2, 5) : False <-> True
    [2, 4) in [2, 5] : True <-> False
    [2, 4) in [2, 5) : True <-> False
    [2, 4) in (2, 5] : False <-> False
    [2, 4) in (2, 5) : False <-> False
    (2, 4] in [2, 5] : True <-> False
    (2, 4] in [2, 5) : True <-> False
    (2, 4] in (2, 5] : True <-> False
    (2, 4] in (2, 5) : True <-> True
    (2, 4) in [2, 5] : True <-> False
    (2, 4) in [2, 5) : True <-> False
    (2, 4) in (2, 5] : True <-> False
    (2, 4) in (2, 5) : True <-> False

    >>> for i in range (1, 4) :
    ...     for bs in ("[]", "[)", "(]", "()") :
    ...         r = R (1, i, bs)
    ...         print \
    ...             ( "r : %s %5s; 1 in r: %5s; 2 in r: %5s"
    ...             % (r, bool (r), 1 in r, r.contains (2))
    ...             )
    r : [1, 1]  True; 1 in r:  True; 2 in r: False
    r : [1, 1) False; 1 in r: False; 2 in r: False
    r : (1, 1] False; 1 in r: False; 2 in r: False
    r : (1, 1) False; 1 in r: False; 2 in r: False
    r : [1, 2]  True; 1 in r:  True; 2 in r:  True
    r : [1, 2)  True; 1 in r:  True; 2 in r: False
    r : (1, 2]  True; 1 in r: False; 2 in r:  True
    r : (1, 2) False; 1 in r: False; 2 in r: False
    r : [1, 3]  True; 1 in r:  True; 2 in r:  True
    r : [1, 3)  True; 1 in r:  True; 2 in r:  True
    r : (1, 3]  True; 1 in r: False; 2 in r:  True
    r : (1, 3)  True; 1 in r: False; 2 in r:  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ab (R (2, 3, bt1), R (1, 2, bt2))
    ...         _show_ab (R (3, 5, bt1), R (1, 3, bt2))
    ...         _show_ab (R (4, 6, bt1), R (1, 3, bt2))
    [2, 3] after [1, 2] : False
    [3, 5] after [1, 3] : False
    [4, 6] after [1, 3] :  True
    [2, 3] after [1, 2) :  True
    [3, 5] after [1, 3) :  True
    [4, 6] after [1, 3) :  True
    [2, 3] after (1, 2] : False
    [3, 5] after (1, 3] : False
    [4, 6] after (1, 3] :  True
    [2, 3] after (1, 2) : False
    [3, 5] after (1, 3) :  True
    [4, 6] after (1, 3) :  True
    [2, 3) after [1, 2] : False
    [3, 5) after [1, 3] : False
    [4, 6) after [1, 3] :  True
    [2, 3) after [1, 2) :  True
    [3, 5) after [1, 3) :  True
    [4, 6) after [1, 3) :  True
    [2, 3) after (1, 2] : False
    [3, 5) after (1, 3] : False
    [4, 6) after (1, 3] :  True
    [2, 3) after (1, 2) : False
    [3, 5) after (1, 3) :  True
    [4, 6) after (1, 3) :  True
    (2, 3] after [1, 2] :  True
    (3, 5] after [1, 3] :  True
    (4, 6] after [1, 3] :  True
    (2, 3] after [1, 2) :  True
    (3, 5] after [1, 3) :  True
    (4, 6] after [1, 3) :  True
    (2, 3] after (1, 2] :  True
    (3, 5] after (1, 3] :  True
    (4, 6] after (1, 3] :  True
    (2, 3] after (1, 2) : False
    (3, 5] after (1, 3) :  True
    (4, 6] after (1, 3) :  True
    (2, 3) after [1, 2] : False
    (3, 5) after [1, 3] :  True
    (4, 6) after [1, 3] :  True
    (2, 3) after [1, 2) : False
    (3, 5) after [1, 3) :  True
    (4, 6) after [1, 3) :  True
    (2, 3) after (1, 2] : False
    (3, 5) after (1, 3] :  True
    (4, 6) after (1, 3] :  True
    (2, 3) after (1, 2) : False
    (3, 5) after (1, 3) :  True
    (4, 6) after (1, 3) :  True

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_adj (R (2, 3, bt1), R (1, 2, bt2))
    ...         _show_adj (R (3, 5, bt1), R (1, 3, bt2))
    ...         _show_adj (R (4, 6, bt1), R (1, 3, bt2))
    [2, 3] is_adjacent [1, 2] : False
    [3, 5] is_adjacent [1, 3] : False
    [4, 6] is_adjacent [1, 3] :  True
    [2, 3] is_adjacent [1, 2) :  True
    [3, 5] is_adjacent [1, 3) :  True
    [4, 6] is_adjacent [1, 3) : False
    [2, 3] is_adjacent (1, 2] : False
    [3, 5] is_adjacent (1, 3] : False
    [4, 6] is_adjacent (1, 3] :  True
    [2, 3] is_adjacent (1, 2) : False
    [3, 5] is_adjacent (1, 3) :  True
    [4, 6] is_adjacent (1, 3) : False
    [2, 3) is_adjacent [1, 2] : False
    [3, 5) is_adjacent [1, 3] : False
    [4, 6) is_adjacent [1, 3] :  True
    [2, 3) is_adjacent [1, 2) :  True
    [3, 5) is_adjacent [1, 3) :  True
    [4, 6) is_adjacent [1, 3) : False
    [2, 3) is_adjacent (1, 2] : False
    [3, 5) is_adjacent (1, 3] : False
    [4, 6) is_adjacent (1, 3] :  True
    [2, 3) is_adjacent (1, 2) : False
    [3, 5) is_adjacent (1, 3) :  True
    [4, 6) is_adjacent (1, 3) : False
    (2, 3] is_adjacent [1, 2] :  True
    (3, 5] is_adjacent [1, 3] :  True
    (4, 6] is_adjacent [1, 3] : False
    (2, 3] is_adjacent [1, 2) : False
    (3, 5] is_adjacent [1, 3) : False
    (4, 6] is_adjacent [1, 3) : False
    (2, 3] is_adjacent (1, 2] :  True
    (3, 5] is_adjacent (1, 3] :  True
    (4, 6] is_adjacent (1, 3] : False
    (2, 3] is_adjacent (1, 2) : False
    (3, 5] is_adjacent (1, 3) : False
    (4, 6] is_adjacent (1, 3) : False
    (2, 3) is_adjacent [1, 2] : False
    (3, 5) is_adjacent [1, 3] :  True
    (4, 6) is_adjacent [1, 3] : False
    (2, 3) is_adjacent [1, 2) : False
    (3, 5) is_adjacent [1, 3) : False
    (4, 6) is_adjacent [1, 3) : False
    (2, 3) is_adjacent (1, 2] : False
    (3, 5) is_adjacent (1, 3] :  True
    (4, 6) is_adjacent (1, 3] : False
    (2, 3) is_adjacent (1, 2) : False
    (3, 5) is_adjacent (1, 3) : False
    (4, 6) is_adjacent (1, 3) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_sb (R (3, 5, bt1), R (1, 3, bt2))
    [3, 5] [1, 3] --> '[1', '3]', '[3', '5]'
    [3, 5] [1, 3) --> '[1', '3)', '[3', '5]'
    [3, 5] (1, 3] --> '(1', '3]', '[3', '5]'
    [3, 5] (1, 3) --> '(1', '3)', '[3', '5]'
    [3, 5) [1, 3] --> '[1', '3]', '[3', '5)'
    [3, 5) [1, 3) --> '[1', '3)', '[3', '5)'
    [3, 5) (1, 3] --> '(1', '3]', '[3', '5)'
    [3, 5) (1, 3) --> '(1', '3)', '[3', '5)'
    (3, 5] [1, 3] --> '[1', '3]', '(3', '5]'
    (3, 5] [1, 3) --> '[1', '3)', '(3', '5]'
    (3, 5] (1, 3] --> '(1', '3]', '(3', '5]'
    (3, 5] (1, 3) --> '(1', '3)', '(3', '5]'
    (3, 5) [1, 3] --> '[1', '3]', '(3', '5)'
    (3, 5) [1, 3) --> '[1', '3)', '(3', '5)'
    (3, 5) (1, 3] --> '(1', '3]', '(3', '5)'
    (3, 5) (1, 3) --> '(1', '3)', '(3', '5)'

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_sb (R (1, 5, bt1), R (2, 6, bt2))
    [1, 5] [2, 6] --> '[1', '[2', '5]', '6]'
    [1, 5] [2, 6) --> '[1', '[2', '6)', '5]'
    [1, 5] (2, 6] --> '[1', '(2', '5]', '6]'
    [1, 5] (2, 6) --> '[1', '(2', '6)', '5]'
    [1, 5) [2, 6] --> '[1', '[2', '5)', '6]'
    [1, 5) [2, 6) --> '[1', '[2', '5)', '6)'
    [1, 5) (2, 6] --> '[1', '(2', '5)', '6]'
    [1, 5) (2, 6) --> '[1', '(2', '5)', '6)'
    (1, 5] [2, 6] --> '(1', '[2', '5]', '6]'
    (1, 5] [2, 6) --> '(1', '[2', '6)', '5]'
    (1, 5] (2, 6] --> '(1', '(2', '5]', '6]'
    (1, 5] (2, 6) --> '(1', '(2', '6)', '5]'
    (1, 5) [2, 6] --> '(1', '[2', '5)', '6]'
    (1, 5) [2, 6) --> '(1', '[2', '5)', '6)'
    (1, 5) (2, 6] --> '(1', '(2', '5)', '6]'
    (1, 5) (2, 6) --> '(1', '(2', '5)', '6)'

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (3, 5, bt1), R (1, 3, bt2))
    [3, 5] overlaps [1, 3] :  True
    [3, 5] overlaps [1, 3) : False
    [3, 5] overlaps (1, 3] :  True
    [3, 5] overlaps (1, 3) : False
    [3, 5) overlaps [1, 3] :  True
    [3, 5) overlaps [1, 3) : False
    [3, 5) overlaps (1, 3] :  True
    [3, 5) overlaps (1, 3) : False
    (3, 5] overlaps [1, 3] : False
    (3, 5] overlaps [1, 3) : False
    (3, 5] overlaps (1, 3] : False
    (3, 5] overlaps (1, 3) : False
    (3, 5) overlaps [1, 3] : False
    (3, 5) overlaps [1, 3) : False
    (3, 5) overlaps (1, 3] : False
    (3, 5) overlaps (1, 3) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_ovl (R (3, 5, bt1), R (1, 4, bt2))
    [3, 5] overlaps [1, 4] :  True
    [3, 5] overlaps [1, 4) :  True
    [3, 5] overlaps (1, 4] :  True
    [3, 5] overlaps (1, 4) :  True
    [3, 5) overlaps [1, 4] :  True
    [3, 5) overlaps [1, 4) :  True
    [3, 5) overlaps (1, 4] :  True
    [3, 5) overlaps (1, 4) :  True
    (3, 5] overlaps [1, 4] :  True
    (3, 5] overlaps [1, 4) : False
    (3, 5] overlaps (1, 4] :  True
    (3, 5] overlaps (1, 4) : False
    (3, 5) overlaps [1, 4] :  True
    (3, 5) overlaps [1, 4) : False
    (3, 5) overlaps (1, 4] :  True
    (3, 5) overlaps (1, 4) : False

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (3, 5, bt1), R (1, 3, bt2))
    [3, 5] intersection [1, 3] : [3, 3]
    [3, 5] intersection [1, 3) : (3, 3)
    [3, 5] intersection (1, 3] : [3, 3]
    [3, 5] intersection (1, 3) : (3, 3)
    [3, 5) intersection [1, 3] : [3, 3]
    [3, 5) intersection [1, 3) : (3, 3)
    [3, 5) intersection (1, 3] : [3, 3]
    [3, 5) intersection (1, 3) : (3, 3)
    (3, 5] intersection [1, 3] : (3, 3)
    (3, 5] intersection [1, 3) : (3, 3)
    (3, 5] intersection (1, 3] : (3, 3)
    (3, 5] intersection (1, 3) : (3, 3)
    (3, 5) intersection [1, 3] : (3, 3)
    (3, 5) intersection [1, 3) : (3, 3)
    (3, 5) intersection (1, 3] : (3, 3)
    (3, 5) intersection (1, 3) : (3, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (3, 5, bt1), R (1, 4, bt2))
    [3, 5] intersection [1, 4] : [3, 4]
    [3, 5] intersection [1, 4) : [3, 3]
    [3, 5] intersection (1, 4] : [3, 4]
    [3, 5] intersection (1, 4) : [3, 3]
    [3, 5) intersection [1, 4] : [3, 4]
    [3, 5) intersection [1, 4) : [3, 3]
    [3, 5) intersection (1, 4] : [3, 4]
    [3, 5) intersection (1, 4) : [3, 3]
    (3, 5] intersection [1, 4] : [4, 4]
    (3, 5] intersection [1, 4) : (4, 3)
    (3, 5] intersection (1, 4] : [4, 4]
    (3, 5] intersection (1, 4) : (4, 3)
    (3, 5) intersection [1, 4] : [4, 4]
    (3, 5) intersection [1, 4) : (4, 3)
    (3, 5) intersection (1, 4] : [4, 4]
    (3, 5) intersection (1, 4) : (4, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_intersection (R (1, 5, bt1), R (2, 6, bt2))
    [1, 5] intersection [2, 6] : [2, 5]
    [1, 5] intersection [2, 6) : [2, 5]
    [1, 5] intersection (2, 6] : [3, 5]
    [1, 5] intersection (2, 6) : [3, 5]
    [1, 5) intersection [2, 6] : [2, 4]
    [1, 5) intersection [2, 6) : [2, 4]
    [1, 5) intersection (2, 6] : [3, 4]
    [1, 5) intersection (2, 6) : [3, 4]
    (1, 5] intersection [2, 6] : [2, 5]
    (1, 5] intersection [2, 6) : [2, 5]
    (1, 5] intersection (2, 6] : [3, 5]
    (1, 5] intersection (2, 6) : [3, 5]
    (1, 5) intersection [2, 6] : [2, 4]
    (1, 5) intersection [2, 6) : [2, 4]
    (1, 5) intersection (2, 6] : [3, 4]
    (1, 5) intersection (2, 6) : [3, 4]

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (3, 5, bt1), R (1, 3, bt2))
    [3, 5] union [1, 3] : [1, 5]
    [3, 5] union [1, 3) : (3, 3)
    [3, 5] union (1, 3] : (1, 5]
    [3, 5] union (1, 3) : (3, 3)
    [3, 5) union [1, 3] : [1, 5)
    [3, 5) union [1, 3) : (3, 3)
    [3, 5) union (1, 3] : (1, 5)
    [3, 5) union (1, 3) : (3, 3)
    (3, 5] union [1, 3] : (3, 3)
    (3, 5] union [1, 3) : (3, 3)
    (3, 5] union (1, 3] : (3, 3)
    (3, 5] union (1, 3) : (3, 3)
    (3, 5) union [1, 3] : (3, 3)
    (3, 5) union [1, 3) : (3, 3)
    (3, 5) union (1, 3] : (3, 3)
    (3, 5) union (1, 3) : (3, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (3, 5, bt1), R (1, 4, bt2))
    [3, 5] union [1, 4] : [1, 5]
    [3, 5] union [1, 4) : [1, 5]
    [3, 5] union (1, 4] : (1, 5]
    [3, 5] union (1, 4) : (1, 5]
    [3, 5) union [1, 4] : [1, 4]
    [3, 5) union [1, 4) : [1, 5)
    [3, 5) union (1, 4] : (1, 4]
    [3, 5) union (1, 4) : (1, 5)
    (3, 5] union [1, 4] : [1, 5]
    (3, 5] union [1, 4) : (4, 3)
    (3, 5] union (1, 4] : (1, 5]
    (3, 5] union (1, 4) : (4, 3)
    (3, 5) union [1, 4] : [1, 4]
    (3, 5) union [1, 4) : (4, 3)
    (3, 5) union (1, 4] : (1, 4]
    (3, 5) union (1, 4) : (4, 3)

    >>> for bt1 in ("[]", "[)", "(]", "()") :
    ...     for bt2 in ("[]", "[)", "(]", "()") :
    ...         _show_union (R (1, 5, bt1), R (2, 6, bt2))
    [1, 5] union [2, 6] : [1, 6]
    [1, 5] union [2, 6) : [1, 5]
    [1, 5] union (2, 6] : [1, 6]
    [1, 5] union (2, 6) : [1, 5]
    [1, 5) union [2, 6] : [1, 6]
    [1, 5) union [2, 6) : [1, 6)
    [1, 5) union (2, 6] : [1, 6]
    [1, 5) union (2, 6) : [1, 6)
    (1, 5] union [2, 6] : (1, 6]
    (1, 5] union [2, 6) : (1, 5]
    (1, 5] union (2, 6] : (1, 6]
    (1, 5] union (2, 6) : (1, 5]
    (1, 5) union [2, 6] : (1, 6]
    (1, 5) union [2, 6) : (1, 6)
    (1, 5) union (2, 6] : (1, 6]
    (1, 5) union (2, 6) : (1, 6)

    >>> rs = ("None, 5", "3, None", "3, 5", "[1, 2]", "[2, 2)", "(1, 5]", "(1, 3)")
    >>> for r in rs :
    ...     _show_fs (R, r)
    None, 5 : Int_Range (None, 5, '[)')
    3, None : Int_Range (3, None, '[)')
      3, 5 : Int_Range (3, 5, '[)')
    [1, 2] : Int_Range (1, 2, '[]')
    [2, 2) : Int_Range (2, 2, '[)')
    (1, 5] : Int_Range (1, 5, '(]')
    (1, 3) : Int_Range (1, 3, '()')

    >>> for r in (infinite, infinite_l, infinite_u) :
    ...     print ("Trying to iterate over", r)
    ...     with expect_except (ValueError) :
    ...         for i, v in enumerate (r) :
    ...             print (" ", i, v)
    ...             if i > 2 :
    ...                 break
    Trying to iterate over [None, None)
    ValueError: Cannot iterate over range `[None, None)` with infinite bound
    Trying to iterate over [None, 1)
    ValueError: Cannot iterate over range `[None, 1)` with infinite bound
    Trying to iterate over [1, None)
      0 1
      1 2
      2 3
      3 4

""" ### _test_int_range

_test_json = r"""
    >>> import json

    >>> r = Int_Range (23, 42)

    >>> with expect_except (TypeError) :
    ...     print (json.dumps ({ "test_range" : r })) # doctest:+ELLIPSIS
    TypeError: ... is not JSON serializable

    >>> import _TFL.json_dump
    >>> print (TFL.json_dump.to_string ({ "test_range" : r }))
    {"test_range": "[23, 42)"}

"""

__test__ = dict \
    ( test_float_range = _test_float_range
    , test_int_range   = _test_int_range
    , test_json        = _test_json
    )

def _sphinx_members (dct = None) :
    """Return names of all bound and range classes defined by `dct`"""
    if dct is None :
        dct = globals ()
    mod = dct.get ("__name__")
    def _gen () :
        MC = _M_Base_
        for k, v in pyk.iteritems (dct) :
            if isinstance (v, MC) and v.__module__ == mod :
                yield v
    result = tuple \
        (c.__name__ for c in sorted (_gen (), key = lambda c : c._sort_key))
    return result
__sphinx__members = _sphinx_members ()

if __name__ != "__main__" :
    TFL._Export ("*", "_Range_Continuous_", "_Range_Discrete_")
### __END__ TFL.Range
