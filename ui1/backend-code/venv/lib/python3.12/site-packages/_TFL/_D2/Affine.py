# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Christian Tanzer. All rights reserved
# tanzer@gg32.com                                      https://www.gg32.com
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <https://www.gg32.com/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.D2.Affine
#
# Purpose
#    Model affine transformations in 2D space
#
# Revision Dates
#    29-Nov-2007 (CT) Creation
#    20-Aug-2012 (CT) Add `Reflection`, `__neg__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    ««revision-date»»···
#--

from   _TFL        import TFL
from   _TFL._D2    import D2
import _TFL._Meta.Object

class Affine (TFL.Meta.Object) :
    """Affine transformation in 2D space.

    >>> t_2_4 = Affine.Trans (2, 4)
    >>> t_2_4
    Affine (1, 0, 2, 0, 1, 4)
    >>> - t_2_4
    Affine (1, 0, -2, 0, 1, -4)

    >>> s_3_5 = Affine.Scale (3, 5)
    >>> s_3_5
    Affine (3, 0, 0, 0, 5, 0)

    >>> - s_3_5
    Affine (0.333333333333, 0, 0, 0, 0.2, 0)

    >>> [t_2_4 (p) for p in ((0, 0), (0, 1), (1, 0))]
    [(2, 4), (2, 5), (3, 4)]
    >>> [s_3_5 (p) for p in [(0, 0), (1, 1), (2, 4), (2, 5), (3, 4)]]
    [(0, 0), (3, 5), (6, 20), (6, 25), (9, 20)]
    >>> t_2_4 (s_3_5 ((2, 2))), s_3_5 (t_2_4 ((2, 2)))
    ((8, 14), (12, 30))
    >>> t_s = t_2_4 * s_3_5
    >>> s_t = s_3_5 * t_2_4
    >>> t_s ((2, 2)), s_t ((2, 2))
    ((8, 14), (12, 30))

    >>> re_x = Affine.Reflection (0, 1)
    >>> re_y = Affine.Reflection (1, 0)

    >>> re_x
    Affine (-1, 0, 0, 0, 1, 0)
    >>> re_y
    Affine (1, 0, 0, 0, -1, 0)

    >>> - re_x
    Affine (-1, 0, 0, 0, 1, 0)

    >>> - re_y
    Affine (1, 0, 0, 0, -1, 0)

    >>> [re_x (p) for p in ((0, 0), (0, 1), (1, 0), (-1, 0), (0, -1))]
    [(0, 0), (0, 1), (-1, 0), (1, 0), (0, -1)]

    >>> [re_y (p) for p in ((0, 0), (0, 1), (1, 0), (-1, 0), (0, -1))]
    [(0, 0), (0, -1), (1, 0), (-1, 0), (0, 1)]

    >>> points = [(-10, 20), (0, 20), (-10, 0), (0, 0), (0, -20), (10, -20)]
    >>> c2s   = Affine.Trans (10, 20) * re_y
    >>> c2s_b = Affine.Reflection (1, 0, 10, 20)
    >>> s2c   = - c2s
    >>> c2s
    Affine (1, 0, 10, 0, -1, 20)
    >>> c2s_b
    Affine (1, 0, 10, 0, -1, 20)

    >>> s2c
    Affine (1, 0, -10, 0, -1, 20)

    >>> points
    [(-10, 20), (0, 20), (-10, 0), (0, 0), (0, -20), (10, -20)]

    >>> [re_y (p) for p in points]
    [(-10, -20), (0, -20), (-10, 0), (0, 0), (0, 20), (10, 20)]

    >>> [c2s (p) for p in points]
    [(0, 0), (10, 0), (0, 20), (10, 20), (10, 40), (20, 40)]

    >>> tps = [c2s_b (p) for p in points]
    >>> tps
    [(0, 0), (10, 0), (0, 20), (10, 20), (10, 40), (20, 40)]

    >>> ttps = [s2c (p) for p in tps]
    >>> ttps
    [(-10, 20), (0, 20), (-10, 0), (0, 0), (0, -20), (10, -20)]

    >>> points == ttps
    True

    """

    _str_format = "(" + ", ".join (("%.12g", ) * 6) + ")"

    @classmethod
    def Reflection (cls, lx = 1, ly = 0, dx = 0, dy = 0) :
        """Returns affine transformations for reflection about a line between
           (0, 0) and (lx, ly).
        """
        n2 = (lx * lx + ly * ly)
        sd = (lx * lx - ly * ly) / n2
        xy = (2  * lx * ly)      / n2
        return cls (sd, xy, dx, xy, - sd, dy)
    # end def Reflection

    @classmethod
    def Rot (cls, angle) :
        """Returns affine transformation for counter-clockwise rotation by
           `angle`.
        """
        return cls (angle.cos, - angle.sin, 0, angle.sin, angle.cos, 0)
    # end def Rot

    @classmethod
    def Scale (cls, sx, sy) :
        """Returns affine transformation for scaling by `sx`, `sy`."""
        return cls (sx, 0, 0, 0, sy, 0)
    # end def Scale

    @classmethod
    def Trans (cls, dx, dy) :
        """Returns affine transformation for translation by `dx`, `dy`."""
        return cls (1, 0, dx, 0, 1, dy)
    # end def Trans

    def __init__ (self, a, b, c, d, e, f) :
        def _clean (* args) :
            def _gen () :
                for x in args :
                    i = int (x)
                    yield i if x == i else x
            return tuple (_gen ())
        self._matrix = (_clean (a, b, c), _clean (d, e, f), (0, 0, 1))
    # end def __init__

    def __call__ (self, p) :
        """Return affine transformation of point `p`."""
        xc, yc = self._matrix [:2]
        pc     = list (p) + [1]
        return \
            ( sum (u * v for (u, v) in zip (pc, xc))
            , sum (u * w for (u, w) in zip (pc, yc))
            )
    # end def __call__

    def __mul__ (self, rhs) :
        if isinstance (rhs, Affine) :
            sm = self._matrix
            rm = list (zip (* rhs._matrix)) # transpose
            return self.__class__ \
                ( sum (u * v for (u, v) in zip (sm [0], rm [0]))
                , sum (u * v for (u, v) in zip (sm [0], rm [1]))
                , sum (u * v for (u, v) in zip (sm [0], rm [2]))
                , sum (u * v for (u, v) in zip (sm [1], rm [0]))
                , sum (u * v for (u, v) in zip (sm [1], rm [1]))
                , sum (u * v for (u, v) in zip (sm [1], rm [2]))
                )
    # end def __mul__

    def __neg__ (self) :
        """Return inverse affine transformation."""
        (a, b, c), (d, e, f) = self._matrix [:2]
        A   = +e
        B   = -d
        D   = -b
        E   = +a
        G   = b * f - c * e
        H   = c * d - a * f
        K   = a * e - b * d
        det = a * A + b * B
        assert det == K, ("det = %s; K = %s" % (det, K))
        return self.__class__ \
            (A / det, D / det, G / det, B / det, E / det, H / det)
    # end def __neg__

    def __str__ (self) :
        (a, b, c), (d, e, f) = self._matrix [:2]
        return self._str_format % (a, b, c, d, e, f)
    # end def __str__

    def __repr__ (self) :
        return "%s %s" % (self.__class__.__name__, str (self))
    # end def __repr__

# end class Affine

if __name__ != "__main__" :
    D2._Export ("*")
### __END__ TFL.D2.Affine
