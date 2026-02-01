# -*- coding: utf-8 -*-
# Copyright (C) 2017-2020 Christian Tanzer All rights reserved
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
#    TFL.D2.Coordinates
#
# Purpose
#    Model cartesian and polar coordinates in 2D space
#
# Revision Dates
#    10-Feb-2017 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                       import TFL

from   _TFL.Angle                 import Angle, Angle_D, Angle_R
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._D2
import _TFL._Meta.Object

import math

class Coordinates (TFL.Meta.Object) :
    """Model coordinates in 2D space.

    >>> cc = Cartesian (1, 2)
    >>> cc
    Cartesian (1.0, 2.0)
    >>> cc.r, cc.phi
    (2.23606797749979, Angle_R (1.10714871779))

    >>> pcc = Polar (cc.r, cc.phi)
    >>> pcc
    Polar (2.23606797749979, Angle_R (1.10714871779))
    >>> cc == pcc, pcc == cc
    (True, True)

    >>> cc + 1, cc - 1
    (Cartesian (2.0, 3.0), Cartesian (0.0, 1.0))

    >>> 1 + cc, 1 - cc
    (Cartesian (2.0, 3.0), Cartesian (0.0, -1.0))

    >>> cc * 2 == pcc * 2
    True

    >>> cc + cc, cc - cc
    (Cartesian (2.0, 4.0), Cartesian (0.0, 0.0))

    >>> cc + pcc, cc - pcc, cc + -pcc
    (Cartesian (2.0, 4.0), Cartesian (0.0, 0.0), Cartesian (0.0, 0.0))

    >>> cc * 2, 2 * cc
    (Cartesian (2.0, 4.0), Cartesian (2.0, 4.0))

    >>> cc * -2
    Cartesian (-2.0, -4.0)

    >>> cc*2 == pcc * 2, cc * -2 == pcc * -2
    (True, True)

    >>> cc / 2
    Cartesian (0.5, 1.0)

    >>> with expect_except (TypeError) :
    ...     2 / cc
    TypeError: unsupported operand type(s) for /: 'int' and 'Cartesian'

    >>> cc / -2
    Cartesian (-0.5, -1.0)

    >>> cc/2 == pcc/2, cc / -2 == pcc / -2
    (True, True)

    >>> cc  == (1.0, 2.0), (1.0, 2.0) == cc
    (True, True)

    >>> pcc == (1.0, 2.0), (1.0, 2.0) == pcc
    (True, True)

    >>> pc = Polar (1, 45)
    >>> pc
    Polar (1.0, Angle_D (45))
    >>> cc == pc, pc == cc
    (False, False)
    >>> pc == (0.707106781186, 0.707106781186)
    True
    >>> pc == (0.70710678, 0.70710678)
    False

    >>> with expect_except (TypeError) :
    ...     Coordinates (1, 2)
    TypeError: Use `Cartesian` or `Polar` to create instances of `Coordinates`

    """

    epsilon = 1e-12

    def __init__ (self, * args, ** kwds) :
        raise TypeError \
            ("Use `Cartesian` or `Polar` to create instances of `Coordinates`")
    # end def __init__

    def _normalized_cartesian (self, x, y) :
        eps = self.epsilon
        return Cartesian \
            ( x if abs (x) >= eps else 0
            , y if abs (y) >= eps else 0
            )
    # end def _normalized_cartesian

    def _rhs_x_y (self, rhs) :
        if isinstance (rhs, Coordinates) :
            rhs_x, rhs_y = rhs.x, rhs.y
        elif isinstance (rhs, pyk.number_types) :
            rhs_x, rhs_y = rhs, rhs
        else :
            rhs_x, rhs_y = rhs
        return rhs_x, rhs_y
    # end def _rhs_x_y

    def _subtracted (self, lhs_x, rhs_x, lhs_y, rhs_y) :
        return self._normalized_cartesian (lhs_x - rhs_x, lhs_y - rhs_y)
    # end def _subtracted

    def __add__ (self, rhs) :
        rhs_x, rhs_y = self._rhs_x_y (rhs)
        return self._normalized_cartesian (self.x + rhs_x, self.y + rhs_y)
    # end def __add__

    __radd__ = __add__

    def __bool__ (self) :
        return all (c == 0 for c in self.coords)
    # end def __bool__

    def __eq__ (self, rhs) :
        if isinstance (rhs, Coordinates) :
            rhs_x, rhs_y = rhs.x, rhs.y
        else :
            try :
                rhs_x, rhs_y = rhs
            except :
                return False
        eps = self.epsilon
        return abs (self.x - rhs_x) < eps and abs (self.y - rhs_y) < eps
    # end def __eq__

    def __hash__ (self) :
        return hash (self.coords)
    # end def __hash__

    def __iter__ (self) :
        return iter (self.coords)
    # end def __iter__

    def __repr__ (self) :
        return "%s %s" % (self.__class__.__name__, self.coords)
    # end def __repr__

    def __str__  (self) :
        return "(%s, %s)" % self.coords
    # end def __str__

    def __sub__ (self, rhs) :
        rhs_x, rhs_y = self._rhs_x_y (rhs)
        return self._subtracted (self.x, rhs_x, self.y, rhs_y)
    # end def __sub__

    def __rmul__ (self, rhs) :
        return self * rhs
    # end def __rmul__

    def __rsub__ (self, rhs) :
        rhs_x, rhs_y = self._rhs_x_y (rhs)
        return self._subtracted (rhs_x, self.x, rhs_y, self.y)
    # end def __rsub__

# end class Coordinates

class Cartesian (Coordinates) :
    """Model cartesian coordinates in 2D space."""

    def __init__ (self, x = 0.0, y = 0.0) :
        self._x = float (x)
        self._y = float (y)
    # end def __init__

    @property
    def as_cartesian (self) :
        return self
    # end def as_cartesian

    @Once_Property
    def coords (self) :
        return (self._x, self._y)
    # end def coords

    @Once_Property
    def phi (self) :
        """Angular coordinate of polar coordinate system"""
        return Angle_R.atan2 (self._y, self._x)
    # end def phi

    @Once_Property
    def r (self) :
        """Radial coordinate of polar coordinate system"""
        x, y = self._x, self._y
        return math.sqrt (x*x + y*y)
    # end def r

    @property
    def x (self) :
        """Horizontal coordinate (abscissa)"""
        return self._x
    # end def x

    @property
    def y (self) :
        """Vertical coordinate (ordinate)"""
        return self._y
    # end def y

    def __mul__ (self, rhs) :
        """Scale up by multiplying with `rhs`"""
        return self.__class__ (self._x * rhs, self._y * rhs)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (- self._x, - self._y)
    # end def __neg__

    def __truediv__ (self, rhs) :
        """Scale down by dviding by `rhs`"""
        return self.__class__ (self._x / rhs, self._y / rhs)
    # end def __truediv__

# end class Cartesian

class Polar (Coordinates) :
    """Model polar coordinates in 2D space."""

    def __init__ (self, r = 0.0, phi = 0.0) :
        if isinstance (phi, pyk.int_types) :
            phi   = float (phi)
        self._r   = abs   (float (r))
        self._phi = Angle (phi)
    # end def __init__

    @property
    def as_cartesian (self) :
        return Cartesian (self.x, self.y)
    # end def as_cartesian

    @Once_Property
    def coords (self) :
        return (self._r, self._phi)
    # end def coords

    @property
    def phi (self) :
        """Angular coordinate"""
        return self._phi
    # end def phi

    @property
    def r (self) :
        """Radial coordinate"""
        return self._r
    # end def r

    @Once_Property
    def x (self) :
        """Horizontal coordinate in cartesian coordinates"""
        return self._r * self._phi.cos
    # end def x

    @Once_Property
    def y (self) :
        """Vertical coordinate in cartesian coordinates"""
        return self._r * self._phi.sin
    # end def y

    def _scaled_phi (self, rhs) :
        result = self._phi
        if rhs < 0 :
            result += Angle_D (180.0)
        return result
    # end def _scaled_phi

    def __mul__ (self, rhs) :
        """Scale up by multiplying with `rhs`"""
        r   = self._r * abs    (rhs)
        phi = self._scaled_phi (rhs)
        return self.__class__  (r, phi)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (self._r, self._phi + Angle_D (180.0))
    # end def __neg__

    def __truediv__ (self, rhs) :
        """Scale down by dviding by `rhs`"""
        r   = self._r / abs    (rhs)
        phi = self._scaled_phi (rhs)
        return self.__class__  (r, phi)
    # end def __truediv__

# end class Polar

if __name__ != "__main__" :
    TFL.D2._Export ("*")
### __END__ TFL.D2.Coordinates
