# -*- coding: utf-8 -*-
# Copyright (C) 2002-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.D2.Point
#
# Purpose
#    Classes modeling points in 2D space
#
# Revision Dates
#    24-Jun-2002 (CT) Creation
#    25-Jun-2002 (CT) Classes for relative Points renamed
#    26-Jun-2002 (CT) `R_Point_nP` added
#    22-Aug-2002 (CT) s/KeyError/IndexError/ for `__.etitem__` methods
#    24-Mar-2003 (CT) Converted to new-style class
#    24-Mar-2003 (CT) `__radd__` and `__rsub__` added
#    24-Mar-2003 (CT) `__rmul__` changed to alias of `__mul__`
#    24-Mar-2003 (CT) `__rdiv__` removed
#     5-Apr-2005 (CT) `import _TFL._D2.Rect` added to doctest of `R_Point_R`
#     4-Jun-2005 (CT) `__getitem__` simplified
#    29-Nov-2007 (CT) Doctest of `R_Point_R` corrected
#    29-Nov-2007 (CT) Use `sum` instead of `reduce/operator.add`
#    29-Nov-2007 (CT) Use `@property` instead of `__getattr__`
#    15-Apr-2012 (CT) Add `import _TFL._D2.Line` to doctest of `R_Point_L`
#    13-Aug-2012 (CT) Add class variable `Point` to `_R_Point_`
#    20-Aug-2012 (CT) Add `norm`, `transformed`
#    20-Aug-2012 (CT) Sort methods alphabetically
#    21-Aug-2012 (CT) Move `transformed` to `_Point_`, let it return `Point`
#    21-Aug-2012 (CT) Change shift to unpack `right`
#     3-Sep-2012 (CT) Add `_Point_.free`
#    19-Oct-2012 (RS) Fix multiplication by `Point (0, 0)` for `_R_Point_`
#    19-Oct-2012 (RS) Fix `_R_Point_` arithmetics when `_scale` != (1, 1)
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL                import TFL

from   _TFL._D2            import D2
from   _TFL.pyk            import pyk

import _TFL._Meta.Object

import math

class _Point_ (TFL.Meta.Object) :
    """Base class for points in 2D space."""

    @property
    def free (self) :
        return Point (self.x, self.y)
    # end def free

    @property
    def norm (self) :
        x, y = self
        return math.sqrt (x*x + y*y)
    # end def norm

    def list (self) :
        return (self.x, self.y)
    # end def list

    def transformed (self, affine) :
        """Return another `Point` whose coordinates are derived via `affine`
           transform from `self`.
        """
        return Point (* affine (self))
    # end def transformed

    def __abs__ (self) :
        return Point (abs (self.x), abs (self.y))
    # end def __abs__

    def __getitem__ (self, index) :
        """Returns `x` for `index == 0` and `y` for `index == 1`"""
        return (self.x, self.y) [index]
    # end def __getitem__

    def __iter__ (self) :
        yield self.x
        yield self.y
    # end def __iter__

    def __len__ (self) :
        return 2
    # end def __len__

    def __bool__ (self) :
        return not (self.x == self.y == 0)
    # end def __bool__

    def __repr__ (self) :
        return "%s %s" % (self.__class__.__name__, tuple (self))
    # end def __repr__

    def __str__  (self) :
        return "(%s, %s)" % (self.x, self.y)
    # end def __str__

# end class _Point_

class Point (_Point_) :
    """Model a point in rectangular, 2-dimensional space."""

    def __init__ (self, x = 0, y = 0) :
        (self.x, self.y) = (x, y)
    # end def __init__

    def scale (self, right) :
        """Scale by point or number `right`"""
        try :
            (self.x, self.y) = (self.x * right.x, self.y * right.y)
        except AttributeError :
            (self.x, self.y) = (self.x * right,   self.y * right)
        return self
    # end def scale

    def shift (self, right) :
        dx, dy = right
        (self.x, self.y) = (self.x + dx, self.y + dy)
        return self
    # end def shift

    def __abs__ (self) :
        return self.__class__ (abs (self.x), abs (self.y))
    # end def __abs__

    def __add__  (self, right) :
        try :
            return self.__class__ (self.x + right.x, self.y + right.y)
        except AttributeError :
            return self.__class__ (self.x + right,   self.y + right)
    # end def __add__

    __radd__ = __add__

    def __floordiv__  (self, right) :
        try :
            return self.__class__ \
                (self.x // right.x, self.y // right.y)
        except AttributeError :
            return self.__class__ \
                (self.x // right,   self.y // right)
    # end def __floordiv__

    def __mul__  (self, right) :
        try :
            return self.__class__ (self.x * right.x, self.y * right.y)
        except AttributeError :
            return self.__class__ (self.x * right,   self.y * right)
    # end def __mul__

    __rmul__ = __mul__

    def __neg__ (self) :
        return self.__class__ (- self.x, - self.y)
    # end def __neg__

    def __setitem__ (self, index, value) :
        """Set `x` (for `index == 0`) or `y` (for `index == 1`) to `value`."""
        if index == 0 :
            self.x = value
        elif index == 1 :
            self.y = value
        else :
            raise IndexError (index)
    # end def __setitem__

    def __sub__  (self, right) :
        try :
            return self.__class__ (self.x - right.x, self.y - right.y)
        except AttributeError :
            return self.__class__ (self.x - right,   self.y - right)
    # end def __sub__

    __rsub__ = __sub__

    def __truediv__  (self, right) :
        try :
            return self.__class__ \
                (float (self.x) / right.x, float (self.y) / right.y)
        except AttributeError :
            return self.__class__ \
                (float (self.x) / right,   float (self.y) / right)
    # end def __truediv__

# end class Point

class _R_Point_ (_Point_) :
    """Base class for Points positioned relative to another point."""

    Point = Point

    @property
    def free (self) :
        return self.Point (self.x, self.y)
    # end def free

    @property
    def x (self) :
        return (self._ref_point.x + self._offset.x) * self._scale.x
    # end def x

    @property
    def y (self) :
        return (self._ref_point.y + self._offset.y) * self._scale.y
    # end def y

    def __init__ (self, offset = None, scale = None) :
        # need explicit test for None -- bool (Point (0, 0)) == False
        self._offset = offset
        self._scale  = scale
        if self._offset is None :
            self._offset = self.Point (0, 0)
        if self._scale  is None :
            self._scale  = self.Point (1, 1)
    # end def __init__

    def scale (self, right) :
        self._scale.scale (right)
        return self
    # end def scale

    def shift (self, right) :
        self._offset.shift (right)
        return self
    # end def shift

    def _reference (self) :
        raise NotImplementedError
    # end def _reference

    def __add__  (self, right) :
        """ We first normalize to a scale (1, 1) then add. """
        return self.__class__ \
            (* self._reference ()
            + ( ( (self._offset + self._ref_point) * self._scale
                - self._ref_point
                + right
                )
              , Point (1, 1)
              )
            )
    # end def __add__

    def __floordiv__  (self, right) :
        return self.__class__ \
            (* self._reference () + (self._offset, self._scale // right))
    # end def __floordiv__

    def __mul__  (self, right) :
        return self.__class__ \
            (* self._reference () + (self._offset, self._scale * right))
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ \
            (* self._reference () + (self._offset, - self._scale))
    # end def __neg__

    def __rdiv__ (self, left) :
        return self.__class__ \
            (* self._reference () + (self._offset, self._scale / left))
    # end def __rdiv__

    def __rmul__ (self, left) :
        return self.__class__ \
            (* self._reference () + (self._offset, self._scale * left))
    # end def __rmul__

    def __sub__  (self, right) :
        """ We first normalize to a scale (1, 1) then subtract. """
        return self.__class__ \
            (* self._reference ()
            + ( ( (self._offset + self._ref_point) * self._scale
                - self._ref_point
                - right
                )
              , Point (1, 1)
              )
            )
    # end def __sub__

    def __truediv__  (self, right) :
        return self.__class__ \
            (* self._reference () + (self._offset, self._scale / right))
    # end def __truediv__

# end class _R_Point_

class R_Point_P (_R_Point_) :
    """Point positioned relative to another point.

       >>> p = Point     (5, 42)
       >>> q = R_Point_P (p, Point (3, 7))
       >>> print (p, q)
       (5, 42) (8, 49)
       >>> p.scale (Point (2, 0.5))
       Point (10, 21.0)
       >>> print (p, q)
       (10, 21.0) (13, 28.0)
       >>> q.scale (Point (3, 2))
       R_Point_P (39, 56.0)
       >>> print (p, q)
       (10, 21.0) (39, 56.0)
       >>> x = R_Point_P (Point (5, 42), Point (-3, -32))
       >>> x
       R_Point_P (2, 10)
       >>> x * Point (3, 2)
       R_Point_P (6, 20)
       >>> x * Point (0, 0)
       R_Point_P (0, 0)
       >>> x * Point (1, 0)
       R_Point_P (2, 0)
       >>> x * Point (0, 1)
       R_Point_P (0, 10)
       >>> p1 = R_Point_P (Point (1, 1), Point (4, -2))
       >>> p1
       R_Point_P (5, -1)
       >>> p2 = R_Point_P (Point (1, 1), Point (2, -3))
       >>> p2
       R_Point_P (3, -2)
       >>> x1 = p1 * Point (0, 1)
       >>> x1
       R_Point_P (0, -1)
       >>> x2 = p2 * Point (1, 0)
       >>> x2
       R_Point_P (3, 0)
       >>> x1 + x2
       R_Point_P (3, -1)
       >>> x1 - x2
       R_Point_P (-3, -1)
       >>> x2 - x1
       R_Point_P (3, 1)
    """

    def __init__ (self, ref_point, offset = None, scale = None) :
        self._ref_point = ref_point
        self.__super.__init__ (offset, scale)
    # end def __init__

    def _reference (self) :
        return (self._ref_point, )
    # end def _reference

# end class R_Point_P

class R_Point_L (_R_Point_) :
    """Point positioned relative to a line.

       >>> import _TFL._D2.Line
       >>> l = D2.Line   (Point (0, 0), Point (20, 10))
       >>> q = R_Point_L (l, 0.5, Point (2, 2))
       >>> r = -q
       >>> print (l, q, r)
       ((0, 0), (20, 10)) (12.0, 7.0) (-12.0, -7.0)
       >>> l.shift (Point (5, 5))
       Line ((5, 5), (25, 15))
       >>> print (l, q, r)
       ((5, 5), (25, 15)) (17.0, 12.0) (-17.0, -12.0)
       >>> x1 = q * Point (1, 0)
       >>> x1
       R_Point_L (17.0, 0.0)
       >>> x2 = q * Point (0, 1)
       >>> x2
       R_Point_L (0.0, 12.0)
       >>> x1 + x2
       R_Point_L (17.0, 12.0)
       >>> x1 - x2
       R_Point_L (17.0, -12.0)
       >>> x2 - x1
       R_Point_L (-17.0, 12.0)
    """

    @property
    def _ref_point (self) :
        return self._ref_line.point (self._shift)
    # end def _ref_point

    def __init__ (self, ref_line, shift, offset = None, scale = None) :
        self._ref_line = ref_line
        self._shift    = shift
        self.__super.__init__ (offset, scale)
    # end def __init__

    def _reference (self) :
        return self._ref_line, self._shift
    # end def _reference

# end class R_Point_L

class R_Point_R (_R_Point_) :
    """Point positioned relative to a rectangle.

       >>> from _TFL._D2.Screen import Rect
       >>> r = Rect   (Point (0, 10), Point (20, 10))
       >>> p = R_Point_R (r, Rect.Center_Top, Point (0, 2))
       >>> print (r, p)
       ((0, 10), (20, 10)) (10.0, 12.0)
       >>> r.shift (Point (5.0, 5.0))
       Rect ((5.0, 15.0), (20, 10))
       >>> print (r, p)
       ((5.0, 15.0), (20, 10)) (15.0, 17.0)
       >>> x1 = p * Point (1, 0)
       >>> x1
       R_Point_R (15.0, 0.0)
       >>> x2 = p * Point (0, 1)
       >>> x2
       R_Point_R (0.0, 17.0)
       >>> x1 + x2
       R_Point_R (15.0, 17.0)
       >>> x1 - x2
       R_Point_R (15.0, -17.0)
       >>> x2 - x1
       R_Point_R (-15.0, 17.0)
    """

    @property
    def _ref_point (self) :
        return self._ref_rectangle.point (self._rect_point)
    # end def _ref_point

    def __init__ \
        (self, ref_rectangle, rect_point, offset = None, scale = None) :
        self._ref_rectangle = ref_rectangle
        self._rect_point    = rect_point
        self.__super.__init__ (offset, scale)
    # end def __init__

    def _reference (self) :
        return self._ref_rectangle, self._rect_point
    # end def _reference

# end class R_Point_R

class R_Point_nP (_R_Point_) :
    """Point positioned relative to (linear combination of) n other points.

       >>> p = Point     (5, 42)
       >>> q = R_Point_P (p, Point (3, 7))
       >>> a = R_Point_nP ((p, q), (0.5, 0.5), (1.0, 0.0))
       >>> print (p, q, a)
       (5, 42) (8, 49) (6.5, 42.0)
       >>> b = R_Point_nP ((p, q, a), (0., 0., 1.0), (0.3, 0.4, 0.3))
       >>> print (p, q, a, "(%.1f, %.1f)" % tuple (b))
       (5, 42) (8, 49) (6.5, 42.0) (6.5, 44.8)
       >>> x1 = a * Point (1, 0)
       >>> x1
       R_Point_nP (6.5, 0.0)
       >>> x2 = a * Point (0, 1)
       >>> x2
       R_Point_nP (0.0, 42.0)
       >>> x1 + x2
       R_Point_nP (6.5, 42.0)
       >>> x1 - x2
       R_Point_nP (6.5, -42.0)
       >>> x2 - x1
       R_Point_nP (-6.5, 42.0)
    """

    @property
    def _ref_point (self) :
        return Point \
            ( sum (   (p.x * w)
                  for (p, w) in zip (self._ref_points, self._x_weights)
                  )
            , sum (   (p.y * w)
                  for (p, w) in zip (self._ref_points, self._y_weights)
                  )
            )
    # end def _ref_point

    def __init__ \
        ( self, ref_points, x_weights, y_weights
        , offset = None, scale = None
        ) :
        if not (len (ref_points) == len (x_weights) == len (y_weights)) :
            raise ValueError \
                ( "%s must have equal length"
                % ((ref_points, x_weights, y_weights), )
                )
        self._ref_points  = ref_points
        self._x_weights   = x_weights
        self._y_weights   = y_weights
        self.__super.__init__ (offset, scale)
    # end def __init__

    def _reference (self) :
        return (self._ref_points, self._x_weights, self._y_weights)
    # end def _reference

# end class R_Point_nP

P  = Point
Pp = R_Point_P
Pl = R_Point_L
Pr = R_Point_R
Pn = R_Point_nP

if __name__ != "__main__" :
    D2._Export ("*", "_Point_", "_R_Point_", "P", "Pp", "Pl", "Pr", "Pn")
### __END__ TFL.D2.Point
