# -*- coding: utf-8 -*-
# Copyright (C) 2017-2024 Christian Tanzer All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# #*** <License> ************************************************************#
# This module is part of the package TFL.D2.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.D2.Transform
#
# Purpose
#    Model 2-dimensional affine coordinate transformations
#
# Revision Dates
#    12-Feb-2017 (CT) Creation
#     2-Mar-2017 (CT) Change `Scale.__str__` to avoid `.__super.__str__`
#                     * breaks in 2.7 due to effect of `@adapt__str__`
#    17-Mar-2024 (CT) Add `MT.CV`, `MT.cv`, and `MT.rv`
#    ««revision-date»»···
#--

"""
Model 2-dimensional affine coordinate transformations::

    >>> portable_repr._float_epsilon = 5e-15
    >>> def show (x) :
    ...     if isinstance (x, tuple) :
    ...         print ("(" + ", ".join (portable_repr (v) for v in x) + ")")
    ...     else :
    ...         print (repr (x))

    >>> r1 = Rotate (45)
    >>> r2 = Rotate (90)
    >>> r3 = Rotate (60)
    >>> r4 = Rotate (60, 100, 100)
    >>> r1
    Rotate (45)
    >>> r1.as_matrix
    MT ((0.707106781187, -0.707106781187, 0), (0.707106781187, 0.707106781187, 0), (0, 0, 1))

    >>> r2
    Rotate (90)
    >>> r2.as_matrix
    MT ((0, -1, 0), (1, 0, 0), (0, 0, 1))

    >>> r3
    Rotate (60)
    >>> r3.as_matrix
    MT ((0.5, -0.866025403784, 0), (0.866025403784, 0.5, 0), (0, 0, 1))

    >>> r4
    Rotate (60, 100, 100)
    >>> r4.as_matrix
    MT ((0.5, -0.866025403784, 136.602540378), (0.866025403784, 0.5, -36.6025403784), (0, 0, 1))

    >>> r1 * r2
    Rotate (135)
    >>> r1 * r3
    Rotate (105)
    >>> r1 * r4
    Matrix (-0.258819045103, 0.965925826289, -0.965925826289, -0.258819045103, 122.474487139, 70.7106781187)

    >>> s1 = Scale (2)
    >>> s2 = Scale (0.5)
    >>> s3 = Scale (2, 1)

    >>> s1
    Scale (2, 2)
    >>> s1.as_matrix
    MT ((2, 0, 0), (0, 2, 0), (0, 0, 1))
    >>> s2
    Scale (0.5, 0.5)
    >>> s2.as_matrix
    MT ((0.5, 0, 0), (0, 0.5, 0), (0, 0, 1))
    >>> s3
    Scale (2, 1)
    >>> s3.as_matrix
    MT ((2, 0, 0), (0, 1, 0), (0, 0, 1))

    >>> s1 * s2
    Scale (1, 1)
    >>> s1 * s3
    Scale (4, 2)
    >>> s2 * s3
    Scale (1, 0.5)

    >>> t1 = Translate (100, 200)
    >>> t2 = Translate (5, 10)
    >>> t1
    Translate (100, 200)
    >>> t1.as_matrix
    MT ((1, 0, 100), (0, 1, 200), (0, 0, 1))

    >>> - t1
    Translate (-100, -200)

    >>> t1 * t2
    Translate (105, 210)

    >>> t1, s2, r1
    (Translate (100, 200), Scale (0.5, 0.5), Rotate (45))

    >>> t1 * s2
    Matrix (0.5, 0, 0, 0.5, 100, 200)

    >>> s2 * t1
    Matrix (0.5, 0, 0, 0.5, 50, 100)

    >>> t1 * r1
    Matrix (0.707106781187, 0.707106781187, -0.707106781187, 0.707106781187, 100, 200)

    >>> t1 * s2 * r1
    Matrix (0.353553390593, 0.353553390593, -0.353553390593, 0.353553390593, 100, 200)

    >>> s2 * t1 * r1
    Matrix (0.353553390593, 0.353553390593, -0.353553390593, 0.353553390593, 50, 100)

    >>> v  = (5, 8)
    >>> t1 (v)
    (105, 208)
    >>> s2 (v)
    (2.5, 4.0)

    >>> (s2 * t1) (v)
    (52.5, 104.0)

    >>> (t1 * s2) (v)
    (102.5, 204.0)

    >>> from _TFL._D2.Coordinates import Cartesian, Polar
    >>> c_23_42 = Cartesian (23, 42)
    >>> p_1_45  = Polar (1, 45)
    >>> show (c_23_42.as_cartesian.coords)
    (23, 42)
    >>> show (p_1_45.as_cartesian.coords)
    (0.707106781187, 0.707106781187)

    >>> t2
    Translate (5, 10)
    >>> show (t2 (c_23_42))
    (28, 52)
    >>> show (t2 (p_1_45))
    (6, Angle_D (55))

    >>> r1
    Rotate (45)
    >>> show (r1 (c_23_42))
    (-13.4350288425, 45.9619407771)
    >>> show (r1 (p_1_45))
    (0, 1)
    >>> show ((- r1) (Polar (1, 45)))
    (1, 0)

    >>> Rotate (90) * Scale (1, -1)
    Matrix (0, 1, 1, 0, 0, 0)

    >>> print (Scale (1, -1))
    scale(1, -1)

"""

from   _TFL                       import TFL

from   _TFL.Angle                 import Angle, Angle_D, Angle_R
from   _TFL.formatted_repr        import formatted_repr, formatted_repr_compact
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._D2
import _TFL._Meta.Object

from   itertools                  import chain as ichain

import math

class MT (TFL.Meta.Object) :
    """Matrix type.

    >>> x = MT ((1,2,3), (4, 5, 6))
    >>> print (x)
    [ (1, 2, 3)
    , (4, 5, 6)
    ]
    >>> x.rows
    ((1, 2, 3), (4, 5, 6))
    >>> x.cols
    ((1, 4), (2, 5), (3, 6))
    >>> print (x.m, "x", x.n)
    2 x 3

    >>> x.T
    MT ((1, 4), (2, 5), (3, 6))

    >>> x
    MT ((1, 2, 3), (4, 5, 6))
    >>> x + x
    MT ((2, 4, 6), (8, 10, 12))
    >>> 5 + x
    MT ((6, 7, 8), (9, 10, 11))

    >>> x * 3
    MT ((3, 6, 9), (12, 15, 18))

    >>> p = MT ((2, 3, 4), (1, 0, 0))
    >>> q = MT ((0, 1000), (1, 100), (0, 10))
    >>> p * q
    MT ((3, 2340), (0, 1000))

    >>> a = MT ((1, 2), (3, 4))
    >>> b = MT ((0, 1), (0, 0))
    >>> a * b
    MT ((0, 1), (0, 3))
    >>> b * a
    MT ((3, 4), (0, 0))

    >>> x = MT ([1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12])
    >>> y = MT ([1, 2], [1, 2], [3, 4])
    >>> x * y
    MT ((12, 18), (27, 42), (42, 66), (57, 90))

    >>> bool (x)
    True
    >>> bool (MT ((0, 0, 0), (0, 0, 0)))
    False

    >>> cv = MT.CV ((1, 2, 3))
    >>> cv
    MT ([1], [2], [3])
    >>> cv.cols
    ((1, 2, 3),)
    >>> cv.cv
    (1, 2, 3)
    >>> cv.rv is None
    True

    >>> x_times_cv = x * cv
    >>> x_times_cv.rows
    ((14,), (32,), (50,), (68,))
    >>> x_times_cv.cols
    ((14, 32, 50, 68),)
    >>> x_times_cv.cv
    (14, 32, 50, 68)

    >>> cv.T
    MT ((1, 2, 3),)

    >>> cv_times_y = cv.T * y
    >>> cv_times_y.rows
    ((12, 18),)
    >>> cv_times_y.cols
    ((12,), (18,))
    >>> cv_times_y.cv is None
    True
    >>> cv_times_y.rv
    (12, 18)

    """

    ### https://en.wikipedia.org/wiki/Matrix_(mathematics)

    def __init__ (self, * rows) :
        self.rows = rows
    # end def __init__

    @classmethod
    def CV (cls, rvs) :
        "Create matrix as a Column Vector from values in `rvs`"
        return cls (* ([v] for v in rvs))
    # end def CV

    @Once_Property
    def cols (self) :
        """Columns of matrix."""
        return tuple (zip (* self.rows))
    # end def cols

    @Once_Property
    def cv (self) :
        """Column vector"""
        cols = self.cols
        if len (cols) == 1 :
            return cols [0]
    # end def cv

    @Once_Property
    def m (self) :
        """Number of rows of matrix."""
        return len (self.rows)
    # end def m

    @Once_Property
    def n (self) :
        """Number of columns of matrix."""
        return len (self.cols)
    # end def n

    @Once_Property
    def rv (self) :
        """Row vector"""
        rows = self.rows
        if len (rows) == 1 :
            return rows [0]
    # end def rv

    @Once_Property
    def T (self) :
        """Transposition of matrix."""
        return self.__class__ (* self.cols)
    # end def T

    def __add__ (self, rhs) :
        if isinstance (rhs, pyk.number_types) :
            result = \
                (   tuple (tuple (x + rhs for x in row))
                for row in self.rows
                )
        else :
            if self.m != rhs.m or self.n != rhs.n :
                raise TypeError \
                    ( "%r has wrong shape %sx%s, %r expected %sx%s"
                    % (rhs, rhs.m, rhs.n, self, self.m, self.n)
                    )
            result = \
                (   tuple (tuple (l + r for l, r in zip (l_row, r_row)))
                for l_row, r_row in zip (self.rows, rhs.rows)
                )
        return self.__class__ (* result)
    # end def __add__

    def __bool__ (self) :
        return any (x != 0 for row in self.rows for x in row)
    # end def __bool__

    def __mul__ (self, rhs) :
        if isinstance (rhs, pyk.number_types) :
            result = \
                (   tuple (tuple (x * rhs for x in row))
                for row in self.rows
                )
        else :
            if self.n != rhs.m :
                raise TypeError \
                    ( "%r has wrong shape %sx%s, %r expected %s rows"
                    % (rhs, rhs.m, rhs.n, self, self.n)
                    )
            result = tuple \
                ( tuple
                    (   sum (l * r for l, r in zip (l_row, r_col))
                    for r_col in rhs.cols
                    )
                for l_row in self.rows
                )
        return self.__class__ (* result)
    # end def __mul__

    __radd__ = __add__
    __rmul__ = __mul__

    def __repr__ (self) :
        return "MT %s" % portable_repr (self.rows)
    # end def __repr__

    def __str__ (self) :
        frc = formatted_repr_compact
        return "[ " + "\n, ".join (frc (r) for r in self.rows) + "\n]"
    # end def __str__

# end class MT

class _Affine_Transform_ (TFL.Meta.Object) :
    """Base class of affine transforms."""

    ### https://en.wikipedia.org/wiki/Transformation_matrix#Affine_transformations

    name = None

    def __call__ (self, v) :
        """Apply transformation to two-dimensional vector `v`."""
        try :
            as_cartesian = v.as_cartesian
        except AttributeError :
            pass
        else :
            v = v.x, v.y
        vm     = MT (* tuple ((x, ) for x in v + (1, )))
        result = self.as_matrix * vm
        return result.cols [0] [:-1]
    # end def __call__

    def __mul__ (self, rhs) :
        result = self.as_matrix * rhs.as_matrix
        return Matrix.from_MT (result)
    # end def __mul__

    def __repr__ (self) :
        return self._formatted_r ()
    # end def __repr__

    def __str__ (self) :
        return self._formatted_s ()
    # end def __str__

    def _formatted_r (self) :
        name = self.name
        return "%s (%s)" % \
            ( self.__class__.__name__ if name is None else name
            , ", ".join (portable_repr (a) for a in self.args)
            )
    # end def _formatted_r

    def _formatted_s (self) :
        return self._formatted_r ().lower ().replace (" (", "(")
    # end def _formatted_s

# end class _Affine_Transform_

class Matrix (_Affine_Transform_) :
    """Transform specified as transformation matrix"""

    def __init__ (self, a, b, c, d, e, f) :
        self.a, self.b, self.c, self.d, self.e, self.f = self.args \
            = a, b, c, d, e, f
    # end def __init__

    @classmethod
    def from_MT (cls, mt) :
        args = tuple (ichain (* (c [:2] for c in mt.cols)))
        return cls   (* args)
    # end def from_MT

    @Once_Property
    def as_matrix (self) :
        return MT \
            ((self.a, self.c, self.e), (self.b, self.d, self.f), (0, 0, 1))
    # end def as_matrix

# end class Matrix

class Rotate (_Affine_Transform_) :
    """Transform specifying a rotation."""

    def __init__ (self, angle, cx = 0, cy = 0) :
        self.angle = Angle (angle)
        self.cx    = cx
        self.cy    = cy
    # end def __init__

    @Once_Property
    def args (self) :
        a, cx, cy = self.angle.degrees, self.cx, self.cy
        return (a, cx, cy) if cx and cy else (a, )
    # end def

    @Once_Property
    def as_matrix (self) :
        a       = self.angle
        result  = MT ((a.cos, -a.sin, 0), (a.sin, a.cos, 0), (0, 0, 1))
        if self.cx or self.cy :
            tr      = Translate (self.cx, self.cy)
            result  = tr.as_matrix * result *(- tr).as_matrix
        return result
    # end def as_matrix

    def __mul__ (self, rhs) :
        if isinstance (rhs, Rotate) and (self.cx, self.cy) == (rhs.cx, rhs.cy) :
            return self.__class__ (self.angle + rhs.angle, self.cx, self.cy)
        else :
            return self.__super.__mul__ (rhs)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (- self.angle, self.cx, self.cy)
    # end def __neg__

# end class Rotate

class Scale (_Affine_Transform_) :
    """Transform specifying a scale operation."""

    def __init__ (self, sx, sy = None) :
        self.sx = sx
        self.sy = sx if sy is None else sy
    # end def __init__

    @Once_Property
    def args (self) :
        return self.sx, self.sy
    # end def

    @Once_Property
    def as_matrix (self) :
        return MT ((self.sx, 0, 0), (0, self.sy, 0), (0, 0, 1))
    # end def as_matrix

    def __call__ (self, v) :
        """Apply scaling transformation to `v`."""
        return tuple (s * t for s, t in zip (v, self.args))
    # end def __call__

    def __mul__ (self, rhs) :
        if isinstance (rhs, Scale) :
            return self.__class__ (self.sx * rhs.sx, self.sy * rhs.sy)
        else :
            return self.__super.__mul__ (rhs)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (- self.sx, - self.sy)
    # end def __neg__

    def __str__ (self) :
        return "scale(%s)" % self.sx if self.sx == self.sy \
            else self._formatted_s ()
    # end def __str__

# end class Scale

class _Skew_ (_Affine_Transform_) :
    """Base class for skew transformations."""

    def __init__ (self, angle) :
        self.angle = Angle (angle)
    # end def __init__

    @Once_Property
    def args (self) :
        return (self.angle.degrees, )
    # end def

    def __neg__ (self) :
        return self.__class__ (- self.angle)
    # end def __neg__

# end class _Skew_

class Skew_X (_Skew_) :
    """Transform specifying a skew transformation along the X axis."""

    name = "skewX"

    @Once_Property
    def as_matrix (self) :
        return MT ((1, self.angle.tan, 0), (0, 1, 0), (0, 0, 1))
    # end def as_matrix

# end class Skew_X

class Skew_Y (_Skew_) :
    """Transform specifying a skew transformation along the Y axis."""

    name = "skewY"

    @Once_Property
    def as_matrix (self) :
        return MT ((1, 0, 0), (self.angle.tan, 1, 0), (0, 0, 1))
    # end def as_matrix

# end class Skew_X

class Translate (_Affine_Transform_) :
    """Transform specifying a translation."""

    def __init__ (self, tx, ty = 0) :
        self.tx = tx
        self.ty = ty
    # end def __init__

    @Once_Property
    def args (self) :
        return self.tx, self.ty
    # end def

    @Once_Property
    def as_matrix (self) :
        return MT ((1, 0, self.tx), (0, 1, self.ty), (0, 0, 1))
    # end def as_matrix

    def __call__ (self, v) :
        """Apply translation to `v`."""
        return tuple (s + t for s, t in zip (v, self.args))
    # end def __call__

    def __mul__ (self, rhs) :
        if isinstance (rhs, Translate) :
            return self.__class__ (self.tx + rhs.tx, self.ty + rhs.ty)
        else :
            return self.__super.__mul__ (rhs)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (- self.tx, - self.ty)
    # end def __neg__

# end class Translate

if __name__ != "__main__" :
    TFL.D2._Export_Module ()
### __END__ TFL.D2.Transform
